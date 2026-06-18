"""Helpers for parsing and normalising CrewAI report output."""

import json
import re


def parse_json_object(raw_output):
    try:
        return json.loads(raw_output)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", raw_output, re.S)

        if not match:
            raise

        return json.loads(match.group(0))


def normalise_report_data(report_data):
    report_data = dict(report_data)

    user_perception = report_data.get("user_perception")

    if isinstance(user_perception, dict):
        user_perception.setdefault("summary", "")
    elif isinstance(user_perception, list):
        report_data["user_perception"] = {
            "summary": summarise_list_items(user_perception),
        }
    elif isinstance(user_perception, str):
        report_data["user_perception"] = {
            "summary": user_perception,
        }
    else:
        report_data["user_perception"] = {
            "summary": "No user perception evidence was available.",
        }

    return report_data


def summarise_list_items(items):
    summaries = []

    for item in items:
        if isinstance(item, dict):
            summary = item.get("summary") or item.get("text") or item.get("finding")
            if summary:
                summaries.append(str(summary))
        elif item:
            summaries.append(str(item))

    if not summaries:
        return "No user perception evidence was available."

    return " ".join(summaries)


REPORT_CITATION_SECTIONS = {
    "timeline": {
        "evidence_attribute": "timeline",
        "target_type": "list",
        "citation_field": "citation_id",
    },
    "themes": {
        "evidence_attribute": "themes",
        "target_type": "list",
        "citation_field": "citation_id",
    },
    "user_perception": {
        "evidence_attribute": "user_perception",
        "target_type": "object",
        "citation_field": "citation_ids",
    },
}


def attach_missing_report_citations(report_data, workflow_evidence):
    for section_name, section_config in REPORT_CITATION_SECTIONS.items():
        evidence_items = getattr(
            workflow_evidence,
            section_config["evidence_attribute"],
            [],
        )
        citation_ids = get_evidence_citation_ids(evidence_items)

        if not citation_ids:
            continue

        if section_config["target_type"] == "list":
            attach_missing_list_citations(
                report_data=report_data,
                section_name=section_name,
                citation_ids=citation_ids,
                citation_field=section_config["citation_field"],
            )
        else:
            attach_missing_object_citations(
                report_data=report_data,
                section_name=section_name,
                citation_ids=citation_ids,
                citation_field=section_config["citation_field"],
            )


def get_evidence_citation_ids(evidence_items):
    return [
        item["citation_id"]
        for item in evidence_items
        if isinstance(item, dict) and item.get("citation_id")
    ]


def attach_missing_list_citations(report_data, section_name, citation_ids, citation_field):
    section_items = report_data.get(section_name, [])

    if not isinstance(section_items, list):
        return

    for index, item in enumerate(section_items):
        if not isinstance(item, dict) or item.get(citation_field):
            continue

        item[citation_field] = citation_ids[min(index, len(citation_ids) - 1)]


def attach_missing_object_citations(report_data, section_name, citation_ids, citation_field):
    section_item = report_data.get(section_name, {})

    if not isinstance(section_item, dict):
        return

    if section_item.get("citation_id") or section_item.get("citation_ids"):
        return

    section_item[citation_field] = citation_ids
