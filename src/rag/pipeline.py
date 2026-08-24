import time
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from src.config import settings
from src.ingestion.extractor import ExtractorFactory, DocumentContent
from src.chunking.chunker import RecursiveCharacterChunker, Chunk
from src.embeddings.provider import BaseEmbeddingProvider, EmbeddingProviderFactory
from src.vector_store.store import BaseVectorStore, InMemoryVectorStore, SearchResult
from src.llm.provider import BaseLLMProvider, LLMProviderFactory, LLMResponse
from src.rag.retriever import Retriever
from src.rag.context_assembler import ContextAssembler, Citation, AssembledContext
from src.rag.prompt_builder import PromptBuilder


class IngestResult(BaseModel):
    file_name: str
    file_path: str
    extension: str
    page_count: int
    chunks_created: int
    processing_time_ms: float


class RAGQueryResult(BaseModel):
    query: str
    answer: str
    citations: List[Citation]
    retrieved_chunks: List[Dict[str, Any]]
    formatted_context: str
    embedding_model: str
    llm_model: str
    total_time_ms: float
    retrieval_time_ms: float
    generation_time_ms: float


class RAGPipeline:
    """Orchestrates end-to-end RAG workflow: Ingestion, Indexing, Retrieval, and Generation."""

    def __init__(
        self,
        embedding_provider: Optional[BaseEmbeddingProvider] = None,
        vector_store: Optional[BaseVectorStore] = None,
        llm_provider: Optional[BaseLLMProvider] = None,
        chunk_size: int = settings.chunk_size,
        chunk_overlap: int = settings.chunk_overlap,
    ):
        self.embedding_provider = (
            embedding_provider
            if embedding_provider
            else EmbeddingProviderFactory.get_provider(
                provider_type=settings.embedding_provider,
                model_name=settings.embedding_model_name,
                api_key=settings.openai_api_key,
            )
        )
        
        # If vector_store is not provided, instantiate default and load disk state if available
        if vector_store is None:
            self.vector_store = InMemoryVectorStore()
            if hasattr(self.vector_store, "load_from_disk"):
                self.vector_store.load_from_disk(settings.vector_store_path)
        else:
            self.vector_store = vector_store

        self.llm_provider = (
            llm_provider
            if llm_provider
            else LLMProviderFactory.get_provider(
                provider_type=settings.llm_provider,
                model_name=settings.llm_model_name,
                api_key=settings.openai_api_key,
                ollama_url=settings.ollama_base_url,
            )
        )

        self.chunker = RecursiveCharacterChunker(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        self.retriever = Retriever(embedding_provider=self.embedding_provider, vector_store=self.vector_store)
        self.context_assembler = ContextAssembler()

    def ingest_document(self, file_path: str) -> IngestResult:
        start_time = time.time()

        # 1. Text Extraction
        extractor = ExtractorFactory.get_extractor(file_path)
        doc_content = extractor.extract(file_path)

        # 2. Chunking
        chunks = self.chunker.split_document(doc_content)

        if chunks:
            # 3. Embedding Generation
            texts = [c.text for c in chunks]
            embeddings = self.embedding_provider.embed_batch(texts)

            # 4. Vector Storage
            self.vector_store.add_chunks(chunks, embeddings)

            # Save vector store state
            if hasattr(self.vector_store, "save_to_disk"):
                self.vector_store.save_to_disk(settings.vector_store_path)

        duration_ms = (time.time() - start_time) * 1000

        return IngestResult(
            file_name=doc_content.file_name,
            file_path=doc_content.file_path,
            extension=doc_content.extension,
            page_count=doc_content.page_count,
            chunks_created=len(chunks),
            processing_time_ms=round(duration_ms, 2),
        )

    def query(
        self,
        query_text: str,
        top_k: int = settings.top_k,
        similarity_threshold: float = settings.similarity_threshold,
    ) -> RAGQueryResult:
        start_total = time.time()

        # 1. Retrieval Phase
        start_retrieval = time.time()
        search_results = self.retriever.retrieve(
            query=query_text, top_k=top_k, similarity_threshold=similarity_threshold
        )
        retrieval_ms = (time.time() - start_retrieval) * 1000

        # 2. Context Assembly
        assembled: AssembledContext = self.context_assembler.assemble(search_results)

        # 3. Prompt Construction
        prompt = PromptBuilder.build_prompt(query=query_text, formatted_context=assembled.formatted_context)

        # 4. LLM Generation Phase
        start_gen = time.time()
        llm_response: LLMResponse = self.llm_provider.generate(
            prompt=prompt, system_prompt=PromptBuilder.DEFAULT_SYSTEM_PROMPT
        )
        generation_ms = (time.time() - start_gen) * 1000

        total_ms = (time.time() - start_total) * 1000

        retrieved_chunk_details = [
            {
                "chunk_id": res.chunk.chunk_id,
                "file_name": res.chunk.file_name,
                "chunk_index": res.chunk.chunk_index,
                "score": round(res.score, 4),
                "text": res.chunk.text,
            }
            for res in search_results
        ]

        return RAGQueryResult(
            query=query_text,
            answer=llm_response.content,
            citations=assembled.citations,
            retrieved_chunks=retrieved_chunk_details,
            formatted_context=assembled.formatted_context,
            embedding_model=getattr(self.embedding_provider, "model_name", "MockEmbedding"),
            llm_model=llm_response.model,
            total_time_ms=round(total_ms, 2),
            retrieval_time_ms=round(retrieval_ms, 2),
            generation_time_ms=round(generation_ms, 2),
        )
