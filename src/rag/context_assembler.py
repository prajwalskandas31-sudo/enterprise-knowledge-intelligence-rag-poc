from typing import List, Dict, Any
from pydantic import BaseModel
from src.vector_store.store import SearchResult


class Citation(BaseModel):
    file_name: str
    chunk_index: int
    score: float
    excerpt: str


class AssembledContext(BaseModel):
    formatted_context: str
    citations: List[Citation]
    chunk_count: int
    truncated: bool = False


class ContextAssembler:
    """Assembles retrieved chunks into a structured context block with citations and token budget control."""

    def __init__(self, max_context_chars: int = 4000):
        self.max_context_chars = max_context_chars

    def assemble(self, search_results: List[SearchResult]) -> AssembledContext:
        if not search_results:
            return AssembledContext(
                formatted_context="[No relevant context found in knowledge base]",
                citations=[],
                chunk_count=0,
                truncated=False,
            )

        context_blocks: List[str] = []
        citations: List[Citation] = []
        current_chars = 0
        truncated = False

        for idx, res in enumerate(search_results):
            chunk = res.chunk
            header = f"[Source {idx+1}: {chunk.file_name} | Chunk {chunk.chunk_index} | Relevance Score: {res.score:.3f}]"
            block = f"{header}\n{chunk.text}\n"

            if current_chars + len(block) > self.max_context_chars:
                truncated = True
                break

            context_blocks.append(block)
            citations.append(
                Citation(
                    file_name=chunk.file_name,
                    chunk_index=chunk.chunk_index,
                    score=res.score,
                    excerpt=chunk.text[:150] + ("..." if len(chunk.text) > 150 else ""),
                )
            )
            current_chars += len(block)

        formatted = "\n\n".join(context_blocks)

        return AssembledContext(
            formatted_context=formatted,
            citations=citations,
            chunk_count=len(citations),
            truncated=truncated,
        )
