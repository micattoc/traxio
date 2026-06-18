from uuid import uuid4

from .config import get_evidence_settings
from .documents import build_documents
from .types import EvidenceIndexResult
from .vector_store import build_vector_store_index


def index_approved_sources(approved_sources, company, product, run_id=None):
    """Index all sources which have been approved (based on Input Guard)."""
    run_id = run_id or str(uuid4())
    settings = get_evidence_settings()

    if not approved_sources:
        return EvidenceIndexResult(
            run_id=run_id,
            indexed_source_count=0,
            warnings=["No approved sources were available for evidence indexing."],
        )

    if not settings.is_configured:
        missing_values = ", ".join(settings.missing_required_values)
        return EvidenceIndexResult(
            run_id=run_id,
            indexed_source_count=0,
            warnings=[f"Evidence indexing skipped. Missing settings: {missing_values}."],
        )

    # Create LlamaIndex documents
    documents = build_documents(
        approved_sources=approved_sources,
        company=company,
        product=product,
        run_id=run_id,
    )

    # Embed new LlamaIndex documents into Pinecone vector store
    try:
        build_vector_store_index(settings, documents)
    except Exception as error:
        return EvidenceIndexResult(
            run_id=run_id,
            indexed_source_count=0,
            warnings=[f"Evidence indexing failed: {error}"],
        )

    return EvidenceIndexResult(
        run_id=run_id,
        indexed_source_count=len(approved_sources),
    )
