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


def attach_user_perception_citations(report_data, workflow_evidence):
    user_perception = report_data.get("user_perception", {})

    if not isinstance(user_perception, dict):
        return

    if user_perception.get("citation_id") or user_perception.get("citation_ids"):
        return

    citation_ids = [
        item["citation_id"]
        for item in workflow_evidence.user_perception
        if item.get("citation_id")
    ]

    if citation_ids:
        user_perception["citation_ids"] = citation_ids
