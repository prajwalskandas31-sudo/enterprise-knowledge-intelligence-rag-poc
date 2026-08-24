from abc import ABC, abstractmethod
from typing import List, Optional
import hashlib
import numpy as np


class BaseEmbeddingProvider(ABC):
    """Abstract base class for text embedding providers."""

    @property
    @abstractmethod
    def dimension(self) -> int:
        """Returns the embedding vector dimension."""
        pass

    @abstractmethod
    def embed_text(self, text: str) -> List[float]:
        """Embed a single text string into a vector."""
        pass

    @abstractmethod
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Embed a batch of text strings into vectors."""
        pass


class MockEmbeddingProvider(BaseEmbeddingProvider):
    """Deterministic mock embedding provider for fast offline execution/testing."""

    def __init__(self, dim: int = 384):
        self._dim = dim

    @property
    def dimension(self) -> int:
        return self._dim

    def _hash_text(self, text: str) -> List[float]:
        # Hash text deterministically into a unit vector
        hash_obj = hashlib.sha256(text.encode("utf-8")).digest()
        seed = int.from_bytes(hash_obj[:4], byteorder="big")
        rng = np.random.RandomState(seed)
        vec = rng.randn(self._dim)
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec.tolist()

    def embed_text(self, text: str) -> List[float]:
        return self._hash_text(text)

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        return [self._hash_text(t) for t in texts]


class SentenceTransformerProvider(BaseEmbeddingProvider):
    """Local embedding provider using sentence-transformers (e.g., all-MiniLM-L6-v2)."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self._model = None
        self._dimension = 384

    def _load_model(self):
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                self._model = SentenceTransformer(self.model_name)
                self._dimension = self._model.get_sentence_embedding_dimension()
            except Exception as e:
                # Fallback to Mock if SentenceTransformer cannot load or network fails
                print(f"[Warning] Could not load SentenceTransformer '{self.model_name}': {e}. Falling back to Mock embedding provider.")
                self._model = MockEmbeddingProvider(dim=384)

    @property
    def dimension(self) -> int:
        self._load_model()
        if isinstance(self._model, MockEmbeddingProvider):
            return self._model.dimension
        return self._dimension

    def embed_text(self, text: str) -> List[float]:
        self._load_model()
        if isinstance(self._model, MockEmbeddingProvider):
            return self._model.embed_text(text)
        embedding = self._model.encode(text, convert_to_numpy=True)
        return embedding.tolist()

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        self._load_model()
        if isinstance(self._model, MockEmbeddingProvider):
            return self._model.embed_batch(texts)
        if not texts:
            return []
        embeddings = self._model.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()


class OpenAIEmbeddingProvider(BaseEmbeddingProvider):
    """OpenAI Embedding provider API integration."""

    def __init__(self, api_key: str, model_name: str = "text-embedding-3-small"):
        self.api_key = api_key
        self.model_name = model_name
        self._dim = 1536

    @property
    def dimension(self) -> int:
        return self._dim

    def embed_text(self, text: str) -> List[float]:
        return self.embed_batch([text])[0]

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        if not self.api_key:
            raise ValueError("OpenAI API Key is required for OpenAIEmbeddingProvider.")
        try:
            import httpx
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            payload = {"input": texts, "model": self.model_name}
            resp = httpx.post("https://api.openai.com/v1/embeddings", json=payload, headers=headers, timeout=30.0)
            resp.raise_for_status()
            data = resp.json()
            return [item["embedding"] for item in data["data"]]
        except Exception as e:
            print(f"[Error] OpenAI Embedding API failed: {e}. Returning mock embeddings.")
            return MockEmbeddingProvider(dim=1536).embed_batch(texts)


class EmbeddingProviderFactory:
    """Factory for embedding providers."""

    @staticmethod
    def get_provider(provider_type: str = "sentence-transformers", model_name: str = "all-MiniLM-L6-v2", api_key: Optional[str] = None) -> BaseEmbeddingProvider:
        provider_type = provider_type.lower()
        if provider_type == "mock":
            return MockEmbeddingProvider()
        elif provider_type == "openai":
            if not api_key:
                print("[Warning] No OpenAI API Key provided. Defaulting to Mock embedding provider.")
                return MockEmbeddingProvider()
            return OpenAIEmbeddingProvider(api_key=api_key, model_name=model_name)
        elif provider_type == "sentence-transformers":
            return SentenceTransformerProvider(model_name=model_name)
        else:
            return SentenceTransformerProvider(model_name=model_name)
