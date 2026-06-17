from .types import EvidenceDocumentPayload
from llama_index.core import Document


def build_document_payloads(approved_sources, company, product, run_id):
    """Convert source attributes into metadata payloads."""
    payloads = []

    for approved_source in approved_sources:
        candidate = approved_source.candidate
        metadata = {
            "run_id": run_id,
            "company": company,
            "product": product,
            "source_url": candidate.url,
            "source_title": candidate.title,
            "source_type": candidate.source_type,
            "guard_summary": approved_source.guard_summary,
            **candidate.metadata,
        }

        payloads.append(
            EvidenceDocumentPayload(
                text=candidate.content,
                metadata=metadata,
            )
        )

    return payloads


def build_documents(approved_sources, company, product, run_id):
    """"Create LlamaIndex documents for each payload available."""
    payloads = build_document_payloads(
        approved_sources=approved_sources,
        company=company,
        product=product,
        run_id=run_id,
    )

    return [
        Document(
            text=payload.text,
            metadata=payload.metadata,
        )
        for payload in payloads
    ]
