from .config import get_evidence_settings
from .types import RetrievedEvidence
from llama_index.core.vector_stores import (
        FilterOperator,
        MetadataFilter,
        MetadataFilters,
    )
from .vector_store import load_vector_store_index


def retrieve_evidence(query, company, product, run_id=None, source_type=None):
    settings = get_evidence_settings()

    if not settings.is_configured:
        return []

    # Establish filters used in LlamaIndex retrieval
    filters = [
        MetadataFilter(key="company", value=company, operator=FilterOperator.EQ),
        MetadataFilter(key="product", value=product, operator=FilterOperator.EQ),
    ]

    if run_id:
        filters.append(
            MetadataFilter(key="run_id", value=run_id, operator=FilterOperator.EQ)
        )

    if source_type:
        filters.append(
            MetadataFilter(key="source_type", value=source_type, operator=FilterOperator.EQ)
        )

    index = load_vector_store_index(settings)

    retriever = index.as_retriever(
        similarity_top_k=settings.top_k,
        filters=MetadataFilters(filters=filters),
    )

    nodes = retriever.retrieve(query)

    return [
        RetrievedEvidence(
            text=node.node.get_content(),
            score=node.score,
            metadata=node.node.metadata,
        )
        for node in nodes
    ]


"""Keyword-style query for each type of evidence to be extracted from vector store."""

def retrieve_timeline_evidence(company, product, run_id=None):
    return retrieve_evidence(
        query=f"{product} {company} launch announcement release funding partnership acquisition timeline",
        company=company,
        product=product,
        run_id=run_id,
    )


def retrieve_theme_evidence(company, product, run_id=None):
    return retrieve_evidence(
        query=f"{product} {company} positioning themes messaging tagline description market category",
        company=company,
        product=product,
        run_id=run_id,
    )


def retrieve_user_perception_evidence(company, product, run_id=None):
    return retrieve_evidence(
        query=f"{product} {company} user comments reviews feedback sentiment public reaction",
        company=company,
        product=product,
        run_id=run_id,
    )


def retrieve_claim_support(claim, company, product, run_id=None):
    return retrieve_evidence(
        query=claim,
        company=company,
        product=product,
        run_id=run_id,
    )
