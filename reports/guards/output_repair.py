"""Repair report output guard failures."""

from copy import deepcopy
from dataclasses import dataclass, field

from reports.agents.report_output import attach_missing_report_citations


@dataclass(frozen=True)
class OutputRepairResult:
    report_data: dict
    applied_repairs: list[str] = field(default_factory=list)


class ReportOutputRepairer:
    def repair(self, report_data, workflow_evidence=None):
        repaired_report = deepcopy(report_data)
        applied_repairs = []

        applied_repairs.extend(self._repair_missing_nested_fields(repaired_report))
        applied_repairs.extend(self._repair_missing_citation_fields(repaired_report))
        applied_repairs.extend(self._repair_missing_rejected_claim_fields(repaired_report))

        if workflow_evidence:
            before_report = deepcopy(repaired_report)
            attach_missing_report_citations(repaired_report, workflow_evidence)
            applied_repairs.extend(
                self._describe_claim_citation_repairs(before_report, repaired_report)
            )

        return OutputRepairResult(
            report_data=repaired_report,
            applied_repairs=applied_repairs,
        )

    def _repair_missing_nested_fields(self, report_data):
        applied_repairs = []
        user_perception = report_data.get("user_perception")

        if isinstance(user_perception, dict) and not isinstance(
            user_perception.get("summary"),
            str,
        ):
            user_perception["summary"] = "No user perception evidence was available."
            applied_repairs.append("Added missing user perception summary.")

        confidence = report_data.get("confidence")

        if isinstance(confidence, dict):
            if not isinstance(confidence.get("level"), str):
                confidence["level"] = "low"
                applied_repairs.append("Added missing confidence level.")

            if not isinstance(confidence.get("reason"), str):
                confidence["reason"] = "Confidence was inferred from available evidence."
                applied_repairs.append("Added missing confidence reason.")

        return applied_repairs

    def _repair_missing_citation_fields(self, report_data):
        applied_repairs = []
        citations = report_data.get("citations", [])

        if not isinstance(citations, list):
            return applied_repairs

        for index, citation in enumerate(citations, start=1):
            if not isinstance(citation, dict):
                continue

            if not citation.get("id"):
                citation["id"] = f"citation-{index}"
                applied_repairs.append(f"Added missing citation ID to source {index}.")

            if not citation.get("title"):
                citation["title"] = f"Source {index}"
                applied_repairs.append(f"Added missing citation title to source {index}.")

            if not citation.get("snippet"):
                citation["snippet"] = "Source snippet was unavailable."
                applied_repairs.append(f"Added missing citation snippet to source {index}.")

        return applied_repairs

    def _repair_missing_rejected_claim_fields(self, report_data):
        applied_repairs = []
        rejected_claims = report_data.get("rejected_claims", [])

        if not isinstance(rejected_claims, list):
            return applied_repairs

        for index, rejected_claim in enumerate(rejected_claims, start=1):
            if not isinstance(rejected_claim, dict):
                continue

            if not rejected_claim.get("claim"):
                rejected_claim["claim"] = "Unspecified unsupported claim."
                applied_repairs.append(f"Added missing rejected claim text to item {index}.")

            if not rejected_claim.get("reason"):
                rejected_claim["reason"] = "The available evidence did not support this claim."
                applied_repairs.append(f"Added missing rejected claim reason to item {index}.")

        return applied_repairs

    def _describe_claim_citation_repairs(self, before_report, repaired_report):
        applied_repairs = []

        for section_name in ["timeline", "themes"]:
            before_items = before_report.get(section_name, [])
            repaired_items = repaired_report.get(section_name, [])

            if not isinstance(before_items, list) or not isinstance(repaired_items, list):
                continue

            for index, repaired_item in enumerate(repaired_items, start=1):
                before_item = before_items[index - 1] if index - 1 < len(before_items) else {}

                if (
                    isinstance(before_item, dict)
                    and isinstance(repaired_item, dict)
                    and not before_item.get("citation_id")
                    and repaired_item.get("citation_id")
                ):
                    applied_repairs.append(
                        f"Added a missing evidence citation to {section_name} item {index}."
                    )

        before_user_perception = before_report.get("user_perception", {})
        repaired_user_perception = repaired_report.get("user_perception", {})

        if (
            isinstance(before_user_perception, dict)
            and isinstance(repaired_user_perception, dict)
            and not before_user_perception.get("citation_id")
            and not before_user_perception.get("citation_ids")
            and (
                repaired_user_perception.get("citation_id")
                or repaired_user_perception.get("citation_ids")
            )
        ):
            applied_repairs.append("Added missing evidence citations to user perception.")

        return applied_repairs
