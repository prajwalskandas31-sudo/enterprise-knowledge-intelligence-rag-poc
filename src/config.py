import os
from typing import Optional
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()


class Settings(BaseModel):
    app_name: str = os.getenv("APP_NAME", "Enterprise Knowledge Intelligence RAG POC")
    app_env: str = os.getenv("APP_ENV", "development")
    debug: bool = os.getenv("DEBUG", "true").lower() == "true"
    port: int = int(os.getenv("PORT", "8000"))

    # Providers
    embedding_provider: str = os.getenv("EMBEDDING_PROVIDER", "sentence-transformers")
    embedding_model_name: str = os.getenv("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")

    llm_provider: str = os.getenv("LLM_PROVIDER", "mock")
    llm_model_name: str = os.getenv("LLM_MODEL_NAME", "gpt-3.5-turbo")

    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY", None)
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

    # Chunking & Retrieval
    chunk_size: int = int(os.getenv("CHUNK_SIZE", "500"))
    chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", "50"))
    top_k: int = int(os.getenv("TOP_K", "3"))
    similarity_threshold: float = float(os.getenv("SIMILARITY_THRESHOLD", "0.0"))

    # Storage
    vector_store_path: str = os.getenv("VECTOR_STORE_PATH", "data/vector_store.json")
    data_dir: str = os.getenv("DATA_DIR", "data/samples")


settings = Settings()
