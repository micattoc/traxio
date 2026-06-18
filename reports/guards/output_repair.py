"""Repair report output guard failures."""

from copy import deepcopy
from dataclasses import dataclass, field

from reports.agents.report_output import attach_user_perception_citations


@dataclass(frozen=True)
class OutputRepairResult:
    report_data: dict
    applied_repairs: list[str] = field(default_factory=list)


class ReportOutputRepairer:
    def repair(self, report_data, workflow_evidence=None):
        repaired_report = deepcopy(report_data)
        applied_repairs = []

        # Attaching missing citations to the report's sections that have factual claims
        applied_repairs.extend(
            self._attach_section_citations(
                repaired_report,
                section_name="timeline",
                evidence_items=getattr(workflow_evidence, "timeline", []),
            )
        )

        applied_repairs.extend(
            self._attach_section_citations(
                repaired_report,
                section_name="themes",
                evidence_items=getattr(workflow_evidence, "themes", []),
            )
        )

        if workflow_evidence:
            before_user_perception = dict(repaired_report.get("user_perception", {}))
            attach_user_perception_citations(repaired_report, workflow_evidence)

            if repaired_report.get("user_perception") != before_user_perception:
                applied_repairs.append("Added missing evidence citations to user perception.")

        return OutputRepairResult(
            report_data=repaired_report,
            applied_repairs=applied_repairs,
        )


    def _attach_section_citations(self, report_data, section_name, evidence_items):
        """Attach citations for a given section."""
        applied_repairs = []
        section_items = report_data.get(section_name, [])

        if not isinstance(section_items, list):
            return applied_repairs

        evidence_citation_ids = [
            item["citation_id"]
            for item in evidence_items
            if isinstance(item, dict) and item.get("citation_id")
        ]

        if not evidence_citation_ids:
            return applied_repairs

        for index, item in enumerate(section_items, start=1):
            if not isinstance(item, dict) or item.get("citation_id"):
                continue

            fallback_citation_id = evidence_citation_ids[
                min(index - 1, len(evidence_citation_ids) - 1)
            ]

            matching_citation_id = self._find_matching_citation_id(
                item=item,
                evidence_items=evidence_items,
            )

            item["citation_id"] = matching_citation_id or fallback_citation_id

            applied_repairs.append(
                f"Added a missing evidence citation to {section_name} item {index}."
            )

        return applied_repairs


    def _find_matching_citation_id(self, item, evidence_items):
        item_text = " ".join(
            str(value)
            for value in item.values()
            if isinstance(value, str)
        ).lower()

        for evidence_item in evidence_items:
            evidence_text = str(evidence_item.get("text", "")).lower()

            if evidence_text and evidence_text[:80] in item_text:
                return evidence_item.get("citation_id")

        return ""
