"""Output Guard checks the audited report before displaying final view to user."""

import re
from dataclasses import dataclass, field
from typing import Any

from reports.guards.input_guard import PROMPT_INJECTION_PATTERNS
from reports.services import validate_report_data


STRATEGY_RECOMMENDATION_PATTERNS = [
    re.compile(r"\bwe recommend\b", re.I),
    re.compile(r"\byou should\b", re.I),
    re.compile(r"\bshould respond\b", re.I),
    re.compile(r"\baction plan\b", re.I),
    re.compile(r"\bnext steps?\b", re.I),
    re.compile(r"\bstrategic recommendation\b", re.I),
]

@dataclass(frozen=True)
class OutputGuardResult:
    is_valid: bool
    errors: list[str] = field(default_factory=list)
    repairable_errors: list[str] = field(default_factory=list)

    @property
    def message(self):
        return " ".join(self.errors)


class ReportOutputGuard:
    def validate(self, report_data: dict[str, Any], skipped_sources=None):
        errors = []
        skipped_sources = skipped_sources or []

        is_valid, validation_error = validate_report_data(report_data)

        if not is_valid:
            errors.append(validation_error)
            return OutputGuardResult(is_valid=False, errors=errors)

        nested_errors = self._validate_required_nested_fields(report_data)
        errors.extend(nested_errors)
        citation_object_errors = self._validate_citation_objects(report_data)
        errors.extend(citation_object_errors)
        citation_errors = self._validate_accepted_claim_citations(report_data)
        errors.extend(citation_errors)
        rejected_claim_errors = self._validate_rejected_claims(report_data)
        errors.extend(rejected_claim_errors)
        errors.extend(self._validate_no_unsafe_text(report_data))
        errors.extend(self._validate_no_skipped_source_citations(report_data, skipped_sources))

        return OutputGuardResult(
            is_valid=not errors,
            errors=errors,
            repairable_errors=[
                error
                for error in nested_errors
                + citation_object_errors
                + citation_errors
                + rejected_claim_errors
                if is_missing_field_error(error)
            ],
        )


    def _validate_required_nested_fields(self, report_data):
        errors = []

        if not isinstance(report_data["user_perception"].get("summary"), str):
            errors.append("user_perception.summary must be a string.")

        confidence = report_data["confidence"]

        if not isinstance(confidence.get("level"), str):
            errors.append("confidence.level must be a string.")

        if not isinstance(confidence.get("reason"), str):
            errors.append("confidence.reason must be a string.")

        return errors


    def _validate_citation_objects(self, report_data):
        errors = []

        for index, citation in enumerate(report_data["citations"], start=1):
            if not isinstance(citation, dict):
                errors.append(f"citations item {index} must be an object.")
                continue

            for field_name in ["id", "title", "url", "snippet"]:
                if not citation.get(field_name):
                    errors.append(f"citations item {index} must include {field_name}.")

        return errors


    def _validate_accepted_claim_citations(self, report_data):
        """Check that all claims have proper citations."""
        errors = []
        citation_ids = {
            citation.get("id")
            for citation in report_data["citations"]
            if isinstance(citation, dict)
        }

        for section_name, field_name in [("timeline", "event"), ("themes", "summary")]:
            for index, item in enumerate(report_data[section_name], start=1):
                if not isinstance(item, dict):
                    errors.append(f"{section_name} item {index} must be an object.")
                    continue

                if item.get(field_name) and not item.get("citation_id"):
                    errors.append(f"{section_name} item {index} must include citation_id.")
                    continue

                if item.get("citation_id") and item["citation_id"] not in citation_ids:
                    errors.append(
                        f"{section_name} item {index} references unknown citation_id "
                        f"{item['citation_id']}."
                    )

        user_perception = report_data["user_perception"]
        summary = user_perception.get("summary", "")
        MISSING_EVIDENCE_MESSAGE = "No user perception evidence was available."

        if summary and summary != MISSING_EVIDENCE_MESSAGE:
            citation_id = user_perception.get("citation_id")
            citation_ids_value = user_perception.get("citation_ids")

            if citation_id and citation_id not in citation_ids:
                errors.append(
                    f"user_perception references unknown citation_id {citation_id}."
                )
            elif citation_ids_value:
                unknown_ids = [
                    value
                    for value in citation_ids_value
                    if value not in citation_ids
                ]

                if unknown_ids:
                    errors.append(
                        "user_perception references unknown citation_id "
                        f"{unknown_ids[0]}."
                    )
            elif citation_ids:
                errors.append("user_perception must include citation_id or citation_ids.")

        return errors


    def _validate_rejected_claims(self, report_data):
        """Check that any rejected claims have adjoining reason."""
        errors = []

        for index, item in enumerate(report_data["rejected_claims"], start=1):
            if not isinstance(item, dict):
                errors.append(f"rejected_claims item {index} must be an object.")
                continue

            if not item.get("claim"):
                errors.append(f"rejected_claims item {index} must include claim.")

            reason = item.get("reason")

            if not reason:
                errors.append(f"rejected_claims item {index} must include reason.")
            elif len(re.findall(r"[.!?]", reason)) > 1:
                errors.append(
                    f"rejected_claims item {index} reason must be one sentence."
                )

        return errors


    def _validate_no_unsafe_text(self, report_data):
        """Check that no claims follow patterns similarly seen in prompt-injection attacks (potentionally extracted from external sources)."""
        errors = []

        for text in iter_report_strings(report_data):
            for pattern in PROMPT_INJECTION_PATTERNS:
                if pattern.search(text):
                    errors.append("Report output repeats prompt-injection-like source text.")
                    return errors

            for pattern in STRATEGY_RECOMMENDATION_PATTERNS:
                if pattern.search(text):
                    # Optional: Avoiding recommendations on strategy from LLM.
                    errors.append("Report output contains strategic recommendation language.")
                    return errors

        return errors


    def _validate_no_skipped_source_citations(self, report_data, skipped_sources):
        """Check that none of the citations include a skipped source."""
        errors = []
        skipped_urls = set()

        for skipped_source in skipped_sources:
            if isinstance(skipped_source, dict):
                skipped_urls.add(skipped_source.get("url"))
            else:
                skipped_urls.add(skipped_source.candidate.url)

        skipped_urls.discard(None)

        if not skipped_urls:
            return errors

        for citation in report_data["citations"]:
            if isinstance(citation, dict) and citation.get("url") in skipped_urls:
                errors.append("Report citations include a skipped source.")
                return errors

        return errors


def iter_report_strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for child in value.values():
            yield from iter_report_strings(child)
    elif isinstance(value, list):
        for child in value:
            yield from iter_report_strings(child)


def is_missing_field_error(error):
    return (
        "must include" in error
        or "must be a string" in error
        or "must be str" in error
        or "must include citation_id" in error
        or "user_perception must include citation_id or citation_ids" in error
    )
