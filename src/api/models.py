from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class QueryApiRequest(BaseModel):
    query: str = Field(..., description="User question or query text", example="What is the data retention policy?")
    top_k: Optional[int] = Field(default=3, description="Number of top context chunks to retrieve")
    similarity_threshold: Optional[float] = Field(default=-1.0, description="Minimum cosine similarity score threshold")


class IngestTextRequest(BaseModel):
    file_name: str = Field(..., description="Document filename", example="hr_policy.txt")
    text_content: str = Field(..., description="Raw text content to ingest")


class DocumentSummary(BaseModel):
    doc_id: str
    file_name: str
    chunk_count: int
    metadata: Dict[str, Any] = {}


class HealthResponse(BaseModel):
    status: str
    app_name: str
    embedding_provider: str
    llm_provider: str
    documents_indexed: int
