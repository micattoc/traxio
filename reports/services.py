def build_mock_report(company, product):
    """Generate filler data."""
    return {
        "timeline": [
            {
                "date": "2026-01-15",
                "event": f"{product} appeared in external launch coverage.",
                "citation_id": "citation-1",
            }
        ],
        "themes": [
            {
                "theme": "Workflow automation",
                "summary": f"External coverage positioned {product} around reducing repetitive launch research work.",
                "citation_id": "citation-1",
            }
        ],
        "user_perception": {
            "summary": "Public user feedback is not available in this mock preview.",
            "sentiment": "unknown",
            "citation_id": None,
        },
        "confidence": {
            "level": "low",
            "reason": "This is mock data used to verify the report preview and save flow.",
        },
        "agent_timeline": [
            {
                "agent": "Mock Workflow",
                "event": "Generated placeholder report data for the Django preview flow.",
            }
        ],
        "rejected_claims": [
            {
                "claim": "Public reception was strongly positive.",
                "reason": "Rejected because the mock report has no user feedback evidence.",
            }
        ],
        "citations": [
            {
                "id": "citation-1",
                "source_type": "press",
                "title": "Mock external launch coverage",
                "url": "https://example.com/mock-launch-coverage",
                "snippet": "Example source snippet used only for UI development.",
            }
        ],
    }

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