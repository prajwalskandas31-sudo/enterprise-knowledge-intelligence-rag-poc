from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class QueryApiRequest(BaseModel):
    query: str = Field(..., description="User question or query text", example="What is the data retention policy?")
    top_k: Optional[int] = Field(default=3, description="Number of top context chunks to retrieve")
    similarity_threshold: Optional[float] = Field(default=-1.0, description="Minimum cosine similarity score threshold")
    mode: Optional[str] = Field(default="auto", description="Execution mode: 'auto', 'cortex_analyst', or 'rag'")


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
    cortex_configured: bool = False
    cortex_semantic_view: Optional[str] = None


class UnifiedQueryResponse(BaseModel):
    source: str  # "cortex_analyst" | "rag"
    query: str
    answer: str
    sql: Optional[str] = None
    query_results: Optional[Dict[str, Any]] = None
    request_id: Optional[str] = None
    verified_query_used: bool = False
    confidence: Optional[Dict[str, Any]] = None
    citations: List[Dict[str, Any]] = Field(default_factory=list)
    retrieved_chunks: List[Dict[str, Any]] = Field(default_factory=list)
    formatted_context: Optional[str] = None
    embedding_model: Optional[str] = None
    llm_model: Optional[str] = None
    total_time_ms: float = 0.0
    retrieval_time_ms: float = 0.0
    generation_time_ms: float = 0.0
    routing_reasoning: Optional[str] = None
