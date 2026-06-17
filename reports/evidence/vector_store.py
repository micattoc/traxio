from pinecone import Pinecone, ServerlessSpec

from llama_index.core import StorageContext, VectorStoreIndex
from llama_index.embeddings.azure_openai import AzureOpenAIEmbedding
from llama_index.vector_stores.pinecone import PineconeVectorStore


class VectorStoreComponents:
    def __init__(self, vector_store, storage_context, embed_model):
        self.vector_store = vector_store
        self.storage_context = storage_context
        self.embed_model = embed_model


def get_azure_embedding_model(settings):
    return AzureOpenAIEmbedding(
        model=settings.azure_openai_embedding_model,
        deployment_name=settings.azure_openai_embedding_deployment,
        api_key=settings.azure_openai_api_key,
        azure_endpoint=settings.azure_openai_endpoint,
        api_version=settings.azure_openai_api_version,
    )


def get_pinecone_client(settings):
    return Pinecone(api_key=settings.pinecone_api_key)


def check_pinecone_index_exists(settings):
    """Connect to Pinecone and check if configured index name exists."""
    client = get_pinecone_client(settings)
    index_list = client.list_indexes()

    if hasattr(index_list, "names"):
        existing_indexes = index_list.names()
    else:
        existing_indexes = [
            index["name"] if isinstance(index, dict) else index.name
            for index in index_list
        ]

    if settings.pinecone_index_name not in existing_indexes:
        # Create index if not already present in Pinecone
        client.create_index(
            name=settings.pinecone_index_name,
            dimension=settings.pinecone_dimension,
            metric="cosine",
            spec=ServerlessSpec(
                cloud=settings.pinecone_cloud,
                region=settings.pinecone_region,
            ),
        )

    return client.Index(settings.pinecone_index_name)


def get_vector_store_components(settings):
    """Return attributes required to setup a vector store."""
    pinecone_index = check_pinecone_index_exists(settings)
    vector_store = PineconeVectorStore(pinecone_index=pinecone_index)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    embed_model = get_azure_embedding_model(settings)

    return VectorStoreComponents(
        vector_store=vector_store,
        storage_context=storage_context,
        embed_model=embed_model,
    )


def build_vector_store_index(settings, documents):
    """Embed new documents into Pinecone vector store using LlamaIndex."""
    components = get_vector_store_components(settings)

    return VectorStoreIndex.from_documents(
        documents,
        storage_context=components.storage_context,
        embed_model=components.embed_model,
    )


def load_vector_store_index(settings):
    """Wrap Pinecone index as a LlamaIndex for retrieval."""
    components = get_vector_store_components(settings)

    return VectorStoreIndex.from_vector_store(
        vector_store=components.vector_store,
        storage_context=components.storage_context,
        embed_model=components.embed_model,
    )
