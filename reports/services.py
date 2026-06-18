# Sections used to verify that report is properly structured.
REQUIRED_REPORT_SECTIONS = {
    "timeline",
    "themes",
    "user_perception",
    "confidence",
    "agent_timeline",
    "rejected_claims",
    "citations",
}


def validate_report_data(report_data):
    if not isinstance(report_data, dict):
        return False, "report_data must be dict."

    missing_sections = REQUIRED_REPORT_SECTIONS - set(report_data.keys())

    if missing_sections:
        return False, f"Missing report sections: {', '.join(sorted(missing_sections))}"

    expected_types = {
        "timeline": list,
        "themes": list,
        "user_perception": dict,
        "confidence": dict,
        "agent_timeline": list,
        "rejected_claims": list,
        "citations": list,
    }

    for section, expected_type in expected_types.items():
        if not isinstance(report_data[section], expected_type):
            return False, f"{section} must be {expected_type.__name__}."

    nested_required_values = {
        "user_perception.summary": report_data["user_perception"].get("summary"),
        "confidence.level": report_data["confidence"].get("level"),
        "confidence.reason": report_data["confidence"].get("reason"),
    }

    for name, value in nested_required_values.items():
        if not isinstance(value, str):
            return False, f"{name} must be str."

    return True, ""