# Enterprise Knowledge Intelligence RAG Architecture Overview

## RAG Pipeline Summary
Retrieval-Augmented Generation (RAG) empowers Large Language Models (LLMs) by augmenting their prompts with domain-specific context retrieved dynamically from a vector store.

## Key Component Responsibilities
1. **Text Extractor**: Reads heterogeneous document types (PDF, Markdown, TXT) into normalized plain text.
2. **Recursive Chunker**: Splits document text into smaller, semantically coherent passages (e.g. 500 characters) while preserving character offset metadata and sentence boundaries.
3. **Embedding Provider**: Maps textual passages into dense high-dimensional numeric vector spaces (e.g., 384 dimensions via sentence-transformers).
4. **Vector Store**: Indexes vector embeddings and executes rapid similarity searches (using Cosine Similarity metrics) to identify top-k relevant context chunks.
5. **Context Assembler**: Formats retrieved passages into an explicit context block with citations while maintaining token/character length constraints.
6. **LLM Provider**: Receives the grounded prompt containing user query + context to synthesize accurate, non-hallucinated answers.
