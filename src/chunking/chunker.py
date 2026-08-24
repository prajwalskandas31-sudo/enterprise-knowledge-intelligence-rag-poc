from abc import ABC, abstractmethod
from typing import List, Dict, Any
import uuid
from pydantic import BaseModel, Field
from src.ingestion.extractor import DocumentContent


class Chunk(BaseModel):
    chunk_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    doc_id: str
    file_name: str
    chunk_index: int
    text: str
    start_char: int
    end_char: int
    metadata: Dict[str, Any] = {}


class BaseChunker(ABC):
    """Abstract base class for document chunkers."""

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    @abstractmethod
    def split_document(self, doc: DocumentContent) -> List[Chunk]:
        """Split document into text chunks."""
        pass


class RecursiveCharacterChunker(BaseChunker):
    """Splits text recursively using hierarchy of separators (paragraphs, lines, sentences, words)."""

    SEPARATORS = ["\n\n", "\n", ". ", " ", ""]

    def _split_recursive(self, text: str, sep_index: int = 0) -> List[str]:
        if not text:
            return []

        if len(text) <= self.chunk_size:
            return [text.strip()]

        if sep_index >= len(self.SEPARATORS):
            # Hard cutoff if no separator matched
            chunks = []
            for i in range(0, len(text), max(1, self.chunk_size - self.chunk_overlap)):
                chunks.append(text[i : i + self.chunk_size])
            return [c.strip() for c in chunks if c.strip()]

        sep = self.SEPARATORS[sep_index]
        if sep not in text and sep != "":
            return self._split_recursive(text, sep_index + 1)

        splits = text.split(sep) if sep != "" else list(text)
        final_chunks: List[str] = []
        current_chunk: List[str] = []
        current_length = 0

        for split in splits:
            # If an individual split is larger than chunk_size, recursively split it
            if len(split) > self.chunk_size:
                if current_chunk:
                    joined = sep.join(current_chunk).strip()
                    if joined:
                        final_chunks.append(joined)
                    current_chunk = []
                    current_length = 0
                sub_chunks = self._split_recursive(split, sep_index + 1)
                final_chunks.extend(sub_chunks)
                continue

            split_len = len(split) + (len(sep) if current_chunk else 0)
            if current_length + split_len > self.chunk_size and current_chunk:
                joined = sep.join(current_chunk).strip()
                if joined:
                    final_chunks.append(joined)
                
                # Maintain overlap
                overlap_text = joined[-self.chunk_overlap:] if self.chunk_overlap > 0 else ""
                current_chunk = [overlap_text, split] if overlap_text else [split]
                current_length = sum(len(s) for s in current_chunk) + len(sep) * (len(current_chunk) - 1)
            else:
                current_chunk.append(split)
                current_length += split_len

        if current_chunk:
            final_joined = sep.join(current_chunk).strip()
            if final_joined:
                final_chunks.append(final_joined)

        return final_chunks

    def split_text(self, text: str) -> List[str]:
        return self._split_recursive(text, 0)

    def split_document(self, doc: DocumentContent) -> List[Chunk]:
        raw_chunks = self.split_text(doc.text)
        result: List[Chunk] = []
        
        current_offset = 0
        doc_id = doc.file_name

        for idx, text_block in enumerate(raw_chunks):
            start_pos = doc.text.find(text_block, current_offset)
            if start_pos == -1:
                start_pos = current_offset
            end_pos = start_pos + len(text_block)
            current_offset = max(current_offset, start_pos + 1)

            chunk_meta = {
                "file_path": doc.file_path,
                "extension": doc.extension,
                "total_chunks": len(raw_chunks),
                **doc.metadata,
            }

            result.append(
                Chunk(
                    doc_id=doc_id,
                    file_name=doc.file_name,
                    chunk_index=idx,
                    text=text_block,
                    start_char=start_pos,
                    end_char=end_pos,
                    metadata=chunk_meta,
                )
            )

        return result
