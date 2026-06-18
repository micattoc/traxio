import os

from .types import EvidenceSettings


def get_evidence_settings():
    return EvidenceSettings(
        azure_openai_api_key=os.getenv("AZURE_OPENAI_API_KEY", ""),
        azure_openai_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT", ""),
        azure_openai_embedding_api_version=os.getenv(
            "AZURE_OPENAI_EMBEDDING_API_VERSION",
            os.getenv("AZURE_OPENAI_API_VERSION", ""),
        ),
        azure_openai_embedding_model=os.getenv("AZURE_OPENAI_EMBEDDING_MODEL", ""),
        azure_openai_embedding_deployment=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", ""),
        pinecone_api_key=os.getenv("PINECONE_API_KEY", ""),
        pinecone_index_name=os.getenv("PINECONE_INDEX_NAME", ""),
        pinecone_cloud=os.getenv("PINECONE_CLOUD", "aws"),
        pinecone_region=os.getenv("PINECONE_REGION", "us-east-1"),
        pinecone_dimension=int(os.getenv("PINECONE_DIMENSION", "1536")),
        top_k=int(os.getenv("EVIDENCE_RETRIEVAL_TOP_K", "5")),
    )
