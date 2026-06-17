from dataclasses import dataclass, field
from typing import Any

# Defining class for checking environment variables required for evidence indexing.
@dataclass(frozen=True)
class EvidenceSettings:
    azure_openai_api_key: str
    azure_openai_endpoint: str
    azure_openai_api_version: str
    azure_openai_embedding_model: str
    azure_openai_embedding_deployment: str
    pinecone_api_key: str
    pinecone_index_name: str
    pinecone_cloud: str
    pinecone_region: str
    pinecone_dimension: int
    top_k: int

    @property
    def missing_required_values(self):
        required_values = {
            "AZURE_OPENAI_API_KEY": self.azure_openai_api_key,
            "AZURE_OPENAI_ENDPOINT": self.azure_openai_endpoint,
            "AZURE_OPENAI_API_VERSION": self.azure_openai_api_version,
            "AZURE_OPENAI_EMBEDDING_MODEL": self.azure_openai_embedding_model,
            "AZURE_OPENAI_EMBEDDING_DEPLOYMENT": self.azure_openai_embedding_deployment,
            "PINECONE_API_KEY": self.pinecone_api_key,
            "PINECONE_INDEX_NAME": self.pinecone_index_name,
        }

        return [
            name
            for name, value in required_values.items()
            if not value
        ]

    @property
    def is_configured(self):
        return not self.missing_required_values


# Defining types used to represent properties of evidence (based on stage).

@dataclass(frozen=True)
class EvidenceDocumentPayload:
    text: str
    metadata: dict[str, Any]


@dataclass(frozen=True)
class EvidenceIndexResult:
    run_id: str
    indexed_source_count: int
    warnings: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class RetrievedEvidence:
    text: str
    score: float | None
    metadata: dict[str, Any]
