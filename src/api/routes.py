import os
import shutil
from typing import List
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from src.config import settings
from src.api.models import QueryApiRequest, IngestTextRequest, HealthResponse, DocumentSummary
from src.rag.pipeline import RAGPipeline, RAGQueryResult, IngestResult

router = APIRouter(prefix="/api", tags=["RAG Endpoints"])

# Global singleton RAG pipeline instance
pipeline = RAGPipeline()


@router.get("/health", response_model=HealthResponse)
def health_check():
    docs = pipeline.vector_store.list_documents()
    return HealthResponse(
        status="healthy",
        app_name=settings.app_name,
        embedding_provider=settings.embedding_provider,
        llm_provider=settings.llm_provider,
        documents_indexed=len(docs),
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
    }


@router.post("/query", response_model=RAGQueryResult)
def query_rag(request: QueryApiRequest):
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query string cannot be empty.")
    
    result = pipeline.query(
        query_text=request.query,
        top_k=request.top_k or settings.top_k,
        similarity_threshold=request.similarity_threshold if request.similarity_threshold is not None else settings.similarity_threshold,
    )
    return result


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
