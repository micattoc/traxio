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

    return True, ""