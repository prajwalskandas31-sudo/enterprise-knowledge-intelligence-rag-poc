# Educational Mapping: Enterprise RAG Architecture vs. Snowflake Cortex AI

This document provides a conceptual 1-to-1 mapping between the custom, open-source Python RAG implementation built in this repository and the native, managed capabilities provided by **Snowflake** and **Snowflake Cortex AI**.

The purpose of this guide is educational: by understanding how each fundamental RAG component works in pure Python, FDP workshop attendees can evaluate what Snowflake replaces natively, what Cortex simplifies via serverless SQL/Python functions, and what remains the application developer's responsibility.

---

## 1. High-Level Architectural Mapping Summary

| Architectural Component | Local Open-Source Implementation (This Repository) | Snowflake / Cortex AI Managed Equivalent | Scope Category |
| :--- | :--- | :--- | :--- |
| **Document Ingestion & Storage** | Local filesystem (`data/samples/`) | **Snowflake Internal / External Stages** (`@my_stage`) | Snowflake Native |
| **Text Extraction** | `pypdf`, `TextExtractor`, `MarkdownExtractor` | **`SNOWFLAKE.CORTEX.PARSE_DOCUMENT`** | Cortex Managed |
| **Text Chunking** | `RecursiveCharacterChunker` (Python regex / hierarchy) | **Snowflake Vector Functions / Splitters** or Custom UDF / Python procedure | Mixed / App Responsibility |
| **Embedding Generation** | `SentenceTransformerProvider` (`all-MiniLM-L6-v2`) | **`SNOWFLAKE.CORTEX.EMBED_TEXT_768`** / `EMBED_TEXT_1024` | Cortex Managed |
| **Vector Indexing & Search** | `InMemoryVectorStore` + Cosine Similarity (`numpy`) | **`VECTOR` Data Type** + **`CORTEX SEARCH` Index** | Snowflake & Cortex |
| **Context Assembly & Budget** | `ContextAssembler` + Character Length Budget | Python / SQL Stored Procedure in Snowflake | App Responsibility |
| **Prompt Engineering** | `PromptBuilder` (Grounded system prompt templates) | SQL / Python String Templating passed to Cortex | App Responsibility |
| **LLM Inference / Synthesis** | `MockLLMProvider` / OpenAI / Ollama | **`SNOWFLAKE.CORTEX.COMPLETE`** (`llama3.1-70b`, `mistral-large`, `snowflake-arctic`) | Cortex Managed |
| **User Interface** | Single-Page Web App (FastAPI + Vanilla JS/CSS) | **Streamlit in Snowflake (SiS)** | Snowflake Native |

---

## 2. Deep-Dive Component Comparisons

### A. Document Storage & Ingestion
- **This Repository (`src/ingestion/`)**: Stores files on the local disk (`data/samples/`) and parses text directly into memory using Python file handles.
- **Snowflake Equivalent (`STAGES`)**: Documents reside in Snowflake Stages (`CREATE STAGE my_doc_stage`). Stages support encryption, role-based governance (RBAC), automatic file compression, and cloud-provider integration (AWS S3, Azure Blob, GCP GCS).
- **Difference Note**: Local disk offers immediate simplicity without cloud accounts, whereas Snowflake Stages provide enterprise access control, auditing, and multi-tenant security out of the box.

### B. Text Extraction & Parsing
- **This Repository (`PDFExtractor`, `MarkdownExtractor`)**: Uses open-source Python libraries (`pypdf`, standard file parsing) to convert raw bytes to text strings.
- **Snowflake Equivalent (`SNOWFLAKE.CORTEX.PARSE_DOCUMENT`)**: Cortex provides a serverless document parsing function that processes binary PDFs or docs stored in a stage and outputs layout-aware text or structured JSON.
- **Difference Note**: Managed `PARSE_DOCUMENT` handles OCR, tables, and multi-page layouts automatically without requiring local binaries or custom Python extraction wrappers.

### C. Embedding Generation
- **This Repository (`src/embeddings/provider.py`)**: Runs PyTorch/SentenceTransformers locally on CPU/GPU (`all-MiniLM-L6-v2`) generating 384-dimensional floating point vectors.
- **Snowflake Equivalent (`SNOWFLAKE.CORTEX.EMBED_TEXT_768`)**: A serverless SQL function that generates vector embeddings directly inside database queries:
  ```sql
  SELECT SNOWFLAKE.CORTEX.EMBED_TEXT_768('e5-base-v2', chunk_text) FROM document_chunks;
  ```
- **Difference Note**: Local embeddings require managing Python model downloads, dependencies, and memory footprint. Cortex managed embedding functions run serverlessly inside Snowflake's security perimeter with auto-scaling hardware.

### D. Vector Storage & Similarity Retrieval
- **This Repository (`src/vector_store/store.py`)**: Uses numpy array operations to perform brute-force Cosine Similarity (`(A · B) / (||A|| * ||B||)`) over in-memory vectors, serialized to JSON.
- **Snowflake Equivalent (`VECTOR(FLOAT, 768)` & `CORTEX SEARCH`)**:
  - Snowflake provides a native `VECTOR` column data type to store high-dimensional arrays in database tables.
  - **`CORTEX SEARCH`** provides a fully managed vector index service supporting hybrid search (Combining Keyword/BM25 search + Semantic Vector similarity) with metadata filtering (`VECTOR_COSINE_SIMILARITY`).
- **Difference Note**: In-memory numpy search works for small educational datasets (< 100,000 vectors). `CORTEX SEARCH` scales to billions of enterprise vectors, maintains real-time index synchronization with database tables, and provides hybrid search out of the box.

### E. LLM Inference & Response Generation
- **This Repository (`src/llm/provider.py`)**: Connects to local Mock LLMs, OpenAI REST endpoints, or local Ollama instances.
- **Snowflake Equivalent (`SNOWFLAKE.CORTEX.COMPLETE`)**: Executes state-of-the-art open models (Llama 3.1 405B, Mistral, Arctic, Claude) directly via SQL or Python SDK without sending data outside Snowflake:
  ```sql
  SELECT SNOWFLAKE.CORTEX.COMPLETE(
      'llama3.1-70b',
      CONCAT('Context: ', context_text, ' Question: ', user_query)
  );
  ```
- **Difference Note**: Cortex LLM generation eliminates external API key management, API rate limits, egress bandwidth costs, and third-party vendor compliance reviews.

### F. User Interface & Visualization
- **This Repository (`src/ui/index.html`)**: Interactive single-page web app built with Vanilla HTML/JS/CSS served directly by FastAPI.
- **Snowflake Equivalent (`Streamlit in Snowflake`)**: Enterprise data applications built using Python Streamlit framework hosted natively inside Snowflake accounts with RBAC integration.

---

## 3. Key Takeaways for Workshop Attendees

1. **No Magic in RAG**: RAG is conceptually simple—extract text, split into chunks, compute vector similarity, format prompt context, and query an LLM.
2. **Managed vs. Custom**: Managed services like Snowflake Cortex reduce thousands of lines of infrastructure code (vector indexing, model serving, GPU infrastructure) down to simple SQL functions.
3. **Application Control**: Even with managed LLM services, prompt engineering, context selection budget, domain-specific chunking strategies, and business logic remain key application developer responsibilities.
