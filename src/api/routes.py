import os
import shutil
from typing import List
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from src.config import settings
from src.api.models import QueryApiRequest, IngestTextRequest, HealthResponse, DocumentSummary, UnifiedQueryResponse
from src.rag.pipeline import RAGPipeline, RAGQueryResult, IngestResult
from src.cortex.analyst import CortexAnalystClient
from src.cortex.router import QueryRouter, QueryDestination

router = APIRouter(prefix="/api", tags=["Enterprise Intelligence Endpoints"])

# Global singletons
pipeline = RAGPipeline()
cortex_client = CortexAnalystClient()


@router.get("/health", response_model=HealthResponse)
def health_check():
    docs = pipeline.vector_store.list_documents()
    return HealthResponse(
        status="healthy",
        app_name=settings.app_name,
        embedding_provider=settings.embedding_provider,
        llm_provider=settings.llm_provider,
        documents_indexed=len(docs),
        cortex_configured=cortex_client.is_configured(),
        cortex_semantic_view=settings.snowflake_semantic_view,
    )


@router.get("/config")
def get_configuration():
    return {
        "app_name": settings.app_name,
        "embedding_provider": settings.embedding_provider,
        "embedding_model": settings.embedding_model_name,
        "llm_provider": settings.llm_provider,
        "llm_model": settings.llm_model_name,
        "chunk_size": settings.chunk_size,
        "chunk_overlap": settings.chunk_overlap,
        "top_k": settings.top_k,
        "similarity_threshold": settings.similarity_threshold,
        "snowflake_base_url": settings.snowflake_base_url,
        "snowflake_account": settings.snowflake_account,
        "snowflake_user": settings.snowflake_user,
        "snowflake_role": settings.snowflake_role,
        "snowflake_warehouse": settings.snowflake_warehouse,
        "snowflake_database": settings.snowflake_database,
        "snowflake_schema": settings.snowflake_schema,
        "snowflake_semantic_view": settings.snowflake_semantic_view,
        "cortex_configured": cortex_client.is_configured(),
    }


@router.post("/query", response_model=UnifiedQueryResponse)
def query_intelligence(request: QueryApiRequest):
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query string cannot be empty.")
    
    route_res = QueryRouter.route(request.query, mode=request.mode)

    if route_res.destination == QueryDestination.CORTEX_ANALYST:
        cortex_res = cortex_client.query(request.query)
        return UnifiedQueryResponse(
            source="cortex_analyst",
            query=request.query,
            answer=cortex_res.answer,
            sql=cortex_res.sql,
            request_id=cortex_res.request_id,
            verified_query_used=cortex_res.verified_query_used,
            confidence=cortex_res.confidence,
            total_time_ms=cortex_res.latency_ms,
            routing_reasoning=route_res.reasoning,
        )

    # Route to Enterprise RAG pipeline
    rag_result = pipeline.query(
        query_text=request.query,
        top_k=request.top_k or settings.top_k,
        similarity_threshold=request.similarity_threshold if request.similarity_threshold is not None else settings.similarity_threshold,
    )

    citations_list = [c.model_dump() if hasattr(c, "model_dump") else c.dict() for c in rag_result.citations]

    return UnifiedQueryResponse(
        source="rag",
        query=request.query,
        answer=rag_result.answer,
        citations=citations_list,
        retrieved_chunks=rag_result.retrieved_chunks,
        formatted_context=rag_result.formatted_context,
        embedding_model=rag_result.embedding_model,
        llm_model=rag_result.llm_model,
        total_time_ms=rag_result.total_time_ms,
        retrieval_time_ms=rag_result.retrieval_time_ms,
        generation_time_ms=rag_result.generation_time_ms,
        routing_reasoning=route_res.reasoning,
    )


@router.post("/cortex/query")
def direct_cortex_query(request: QueryApiRequest):
    """Direct endpoint to query Snowflake Cortex Analyst bypassing auto router."""
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query string cannot be empty.")
    cortex_res = cortex_client.query(request.query)
    return cortex_res


@router.post("/upload", response_model=IngestResult)
async def upload_document(file: UploadFile = File(...)):
    allowed_exts = [".pdf", ".txt", ".md", ".markdown"]
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in allowed_exts:
        raise HTTPException(status_code=400, detail=f"Unsupported file format '{ext}'. Allowed formats: {allowed_exts}")

    upload_dir = settings.data_dir
    os.makedirs(upload_dir, exist_ok=True)
    target_path = os.path.join(upload_dir, file.filename)

    with open(target_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    result = pipeline.ingest_document(target_path)
    return result


@router.post("/ingest-text", response_model=IngestResult)
def ingest_raw_text(request: IngestTextRequest):
    upload_dir = settings.data_dir
    os.makedirs(upload_dir, exist_ok=True)
    target_path = os.path.join(upload_dir, request.file_name)

    with open(target_path, "w", encoding="utf-8") as f:
        f.write(request.text_content)

    result = pipeline.ingest_document(target_path)
    return result


@router.get("/documents", response_model=List[DocumentSummary])
def list_documents():
    docs = pipeline.vector_store.list_documents()
    return [
        DocumentSummary(
            doc_id=d["doc_id"],
            file_name=d["file_name"],
            chunk_count=d["chunk_count"],
            metadata=d.get("metadata", {}),
        )
        for d in docs
    ]


@router.delete("/documents/{doc_id}")
def delete_document(doc_id: str):
    success = pipeline.vector_store.delete_document(doc_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Document '{doc_id}' not found.")
    
    if hasattr(pipeline.vector_store, "save_to_disk"):
        pipeline.vector_store.save_to_disk(settings.vector_store_path)

    return {"message": f"Document '{doc_id}' successfully removed from vector store.", "status": "deleted"}
