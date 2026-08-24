import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from src.config import settings
from src.api.routes import router as api_router, pipeline

app = FastAPI(
    title=settings.app_name,
    description="Educational Enterprise Knowledge Intelligence RAG POC without managed cloud dependencies",
    version="1.0.0",
)

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Router
app.include_router(api_router)

# Mount static UI assets
ui_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ui")
if os.path.exists(ui_dir):
    app.mount("/static", StaticFiles(directory=ui_dir), name="static")


@app.get("/", include_in_schema=False)
def serve_ui():
    index_path = os.path.join(ui_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Enterprise Knowledge Intelligence API is running. UI index.html not found.", "docs": "/docs"}


@app.on_event("startup")
def startup_event():
    # Auto-ingest sample data directory if empty index
    docs = pipeline.vector_store.list_documents()
    if not docs and os.path.exists(settings.data_dir):
        print(f"[Startup] Ingesting sample documents from '{settings.data_dir}'...")
        for root, _, files in os.walk(settings.data_dir):
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext in [".pdf", ".txt", ".md", ".markdown"]:
                    full_path = os.path.join(root, file)
                    try:
                        res = pipeline.ingest_document(full_path)
                        print(f"  └ Ingested {file} ({res.chunks_created} chunks in {res.processing_time_ms}ms)")
                    except Exception as e:
                        print(f"  └ Error ingesting {file}: {e}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.api.main:app", host="0.0.0.0", port=settings.port, reload=settings.debug)
