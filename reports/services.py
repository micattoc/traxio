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