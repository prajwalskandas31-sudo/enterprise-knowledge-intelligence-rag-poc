from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import os
from pydantic import BaseModel


class DocumentContent(BaseModel):
    file_name: str
    file_path: str
    extension: str
    text: str
    page_count: int = 1
    metadata: Dict[str, Any] = {}


class BaseExtractor(ABC):
    """Abstract base class for document text extractors."""

    @abstractmethod
    def extract(self, file_path: str) -> DocumentContent:
        """Extract text and metadata from document file."""
        pass


class TextExtractor(BaseExtractor):
    """Extracts content from plain text (.txt) files."""

    def extract(self, file_path: str) -> DocumentContent:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        file_name = os.path.basename(file_path)
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()

        return DocumentContent(
            file_name=file_name,
            file_path=file_path,
            extension=".txt",
            text=text,
            page_count=1,
            metadata={"character_count": len(text), "file_size_bytes": os.path.getsize(file_path)},
        )


class MarkdownExtractor(BaseExtractor):
    """Extracts content from Markdown (.md) files."""

    def extract(self, file_path: str) -> DocumentContent:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        file_name = os.path.basename(file_path)
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()

        headers = [line.strip() for line in text.splitlines() if line.startswith("#")]

        return DocumentContent(
            file_name=file_name,
            file_path=file_path,
            extension=".md",
            text=text,
            page_count=1,
            metadata={
                "character_count": len(text),
                "headers": headers,
                "file_size_bytes": os.path.getsize(file_path),
            },
        )


class PDFExtractor(BaseExtractor):
    """Extracts text content and page details from PDF files using pypdf."""

    def extract(self, file_path: str) -> DocumentContent:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        file_name = os.path.basename(file_path)
        extracted_pages: List[str] = []
        page_count = 0

        try:
            import pypdf
            reader = pypdf.PdfReader(file_path)
            page_count = len(reader.pages)
            for idx, page in enumerate(reader.pages):
                page_text = page.extract_text() or ""
                extracted_pages.append(f"--- [Page {idx + 1}] ---\n" + page_text)
            full_text = "\n\n".join(extracted_pages)
        except Exception as e:
            # Fallback if pypdf extraction fails
            full_text = f"PDF extraction fallback: Could not extract binary content via pypdf ({str(e)})."
            page_count = 1

        return DocumentContent(
            file_name=file_name,
            file_path=file_path,
            extension=".pdf",
            text=full_text,
            page_count=page_count,
            metadata={"character_count": len(full_text), "file_size_bytes": os.path.getsize(file_path)},
        )


class ExtractorFactory:
    """Factory to resolve the appropriate document extractor based on file extension."""

    @staticmethod
    def get_extractor(file_path: str) -> BaseExtractor:
        ext = os.path.splitext(file_path)[1].lower()
        if ext == ".pdf":
            return PDFExtractor()
        elif ext in [".md", ".markdown"]:
            return MarkdownExtractor()
        elif ext in [".txt", ".log", ".csv", ".json"]:
            return TextExtractor()
        else:
            # Default to text extractor for unknown plain text files
            return TextExtractor()
