from typing import List
from src.embeddings.provider import BaseEmbeddingProvider
from src.vector_store.store import BaseVectorStore, SearchResult


class Retriever:
    """Retrieves relevant text chunks from the vector store for a given query."""

    def __init__(self, embedding_provider: BaseEmbeddingProvider, vector_store: BaseVectorStore):
        self.embedding_provider = embedding_provider
        self.vector_store = vector_store

    def retrieve(self, query: str, top_k: int = 3, similarity_threshold: float = -1.0) -> List[SearchResult]:
        if not query.strip():
            return []

        query_vector = self.embedding_provider.embed_text(query)
        results = self.vector_store.search(
            query_vector=query_vector,
            top_k=top_k,
            similarity_threshold=similarity_threshold,
        )
        return results
