from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import os
import json
import numpy as np
from pydantic import BaseModel
from src.chunking.chunker import Chunk


class SearchResult(BaseModel):
    chunk: Chunk
    score: float


class BaseVectorStore(ABC):
    """Abstract base class for vector store providers."""

    @abstractmethod
    def add_chunks(self, chunks: List[Chunk], embeddings: List[List[float]]) -> None:
        """Add text chunks and corresponding embedding vectors to vector store index."""
        pass

    @abstractmethod
    def search(
        self, query_vector: List[float], top_k: int = 3, similarity_threshold: float = -1.0
    ) -> List[SearchResult]:
        """Perform vector similarity search against indexed chunks."""
        pass

    @abstractmethod
    def delete_document(self, doc_id: str) -> bool:
        """Delete all chunks associated with a document ID."""
        pass

    @abstractmethod
    def list_documents(self) -> List[Dict[str, Any]]:
        """List all indexed documents with stats."""
        pass

    @abstractmethod
    def save_to_disk(self, file_path: str) -> None:
        """Persist index to disk."""
        pass

    @abstractmethod
    def load_from_disk(self, file_path: str) -> None:
        """Load index from disk."""
        pass


class InMemoryVectorStore(BaseVectorStore):
    """In-memory vector store with Cosine Similarity search and JSON persistence."""

    def __init__(self):
        self._chunks: List[Chunk] = []
        self._embeddings: List[np.ndarray] = []

    def add_chunks(self, chunks: List[Chunk], embeddings: List[List[float]]) -> None:
        if len(chunks) != len(embeddings):
            raise ValueError("Number of chunks must match number of embeddings.")

        for chunk, emb in zip(chunks, embeddings):
            vec = np.array(emb, dtype=np.float32)
            norm = np.linalg.norm(vec)
            if norm > 0:
                vec = vec / norm
            self._chunks.append(chunk)
            self._embeddings.append(vec)

    def search(
        self, query_vector: List[float], top_k: int = 3, similarity_threshold: float = -1.0
    ) -> List[SearchResult]:
        if not self._embeddings or not self._chunks:
            return []

        q_vec = np.array(query_vector, dtype=np.float32)
        q_norm = np.linalg.norm(q_vec)
        if q_norm > 0:
            q_vec = q_vec / q_norm

        matrix = np.array(self._embeddings, dtype=np.float32)
        # Cosine similarity on normalized vectors is dot product
        similarities = np.dot(matrix, q_vec)

        # Sort descending
        top_indices = np.argsort(similarities)[::-1]

        results: List[SearchResult] = []
        for idx in top_indices:
            score = float(similarities[idx])
            if score >= similarity_threshold:
                results.append(SearchResult(chunk=self._chunks[idx], score=score))
            if len(results) >= top_k:
                break

        return results

    def delete_document(self, doc_id: str) -> bool:
        new_chunks = []
        new_embeddings = []
        deleted = False

        for chunk, emb in zip(self._chunks, self._embeddings):
            if chunk.doc_id == doc_id or chunk.file_name == doc_id:
                deleted = True
            else:
                new_chunks.append(chunk)
                new_embeddings.append(emb)

        self._chunks = new_chunks
        self._embeddings = new_embeddings
        return deleted

    def list_documents(self) -> List[Dict[str, Any]]:
        doc_stats: Dict[str, Dict[str, Any]] = {}
        for chunk in self._chunks:
            doc_id = chunk.doc_id
            if doc_id not in doc_stats:
                doc_stats[doc_id] = {
                    "doc_id": doc_id,
                    "file_name": chunk.file_name,
                    "chunk_count": 0,
                    "metadata": chunk.metadata,
                }
            doc_stats[doc_id]["chunk_count"] += 1
        return list(doc_stats.values())

    def save_to_disk(self, file_path: str) -> None:
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        data = {
            "chunks": [chunk.model_dump() for chunk in self._chunks],
            "embeddings": [emb.tolist() for emb in self._embeddings],
        }
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def load_from_disk(self, file_path: str) -> None:
        if not os.path.exists(file_path):
            return

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self._chunks = [Chunk(**item) for item in data.get("chunks", [])]
        self._embeddings = [np.array(emb, dtype=np.float32) for emb in data.get("embeddings", [])]
