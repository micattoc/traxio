"""Formatting information extracted by LlamaIndex retrieval from vector store."""

from reports.evidence.retrieval import (
    retrieve_theme_evidence,
    retrieve_timeline_evidence,
    retrieve_user_perception_evidence,
)

from .types import WorkflowEvidence


def collect_workflow_evidence(company, product, run_id):
    return WorkflowEvidence(
        timeline=format_retrieved_evidence(
            retrieve_timeline_evidence(company=company, product=product, run_id=run_id),
            citation_prefix="timeline",
        ),
        themes=format_retrieved_evidence(
            retrieve_theme_evidence(company=company, product=product, run_id=run_id),
            citation_prefix="theme",
        ),
        user_perception=format_retrieved_evidence(
            retrieve_user_perception_evidence(
                company=company,
                product=product,
                run_id=run_id,
            ),
            citation_prefix="perception",
        ),
    )


def format_retrieved_evidence(retrieved_evidence, citation_prefix):
    formatted_evidence = []

    for index, item in enumerate(retrieved_evidence, start=1):
        metadata = item.metadata or {}
        formatted_evidence.append(
            {
                "citation_id": f"{citation_prefix}-{index}",
                "text": item.text,
                "score": item.score,
                "source_type": metadata.get("source_type", "unknown"),
                "source_title": metadata.get("source_title", "Untitled source"),
                "source_url": metadata.get("source_url", ""),
                "published_at": metadata.get("published_at"),
            }
        )

    return formatted_evidence


def build_citations_from_evidence(workflow_evidence):
    citations_by_id = {}

    for evidence_items in [
        workflow_evidence.timeline,
        workflow_evidence.themes,
        workflow_evidence.user_perception,
    ]:
        for item in evidence_items:
            citations_by_id[item["citation_id"]] = {
                "id": item["citation_id"],
                "source_type": item["source_type"],
                "title": item["source_title"],
                "url": item["source_url"],
                "snippet": item["text"][:300],
            }

    return list(citations_by_id.values())


def evidence_to_prompt_context(workflow_evidence):
    sections = []

    for label, evidence_items in [
        ("Timeline Evidence", workflow_evidence.timeline),
        ("Theme Evidence", workflow_evidence.themes),
        ("User Perception Evidence", workflow_evidence.user_perception),
    ]:
        if not evidence_items:
            sections.append(f"{label}: none retrieved.")
            continue

        lines = [f"{label}:"]

        for item in evidence_items:
            lines.append(
                "\n".join(
                    [
                        f"- Citation ID: {item['citation_id']}",
                        f"  Source: {item['source_title']} ({item['source_url']})",
                        f"  Published: {item['published_at'] or 'unknown'}",
                        f"  Text: {item['text']}",
                    ]
                )
            )

        sections.append("\n".join(lines))

    return "\n\n".join(sections)
