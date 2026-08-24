# Enterprise Knowledge Intelligence RAG POC 🧠⚡

An open-source, modular, provider-agnostic **Retrieval-Augmented Generation (RAG)** Proof-of-Concept built from scratch in Python without external managed cloud dependencies. Designed for educational clarity in FDP (Faculty Development Program) workshops and developer training.

> [!TIP]
> **100% Free Tier & Local Zero-Cost Guarantee**: By default, this entire application runs **100% locally and completely free of charge**. It uses open-source embedding models (`sentence-transformers`), local text extractors (`pypdf`), local in-memory vector storage (`numpy`), and an offline grounded synthesis engine (`MockLLMProvider` or local `Ollama`). No cloud accounts, paid API keys, or subscriptions are required to run this repository.

Every major component—from text extraction and chunking to vector similarity indexing, prompt engineering, and LLM synthesis—is implemented explicitly in clean Python so developers can understand the mechanics step-by-step before mapping them one-to-one against Snowflake and Cortex AI capabilities.

---

## 🌟 Key Features

- **100% Free & Offline Execution**: Works out of the box with zero external API keys using local sentence transformers (`all-MiniLM-L6-v2`) or deterministic mock providers.
- **Provider-Agnostic Architecture**: Swap LLM providers (`Mock`, `Ollama`, or optional `OpenAI`), Embedding models (`SentenceTransformers` or `Mock`), or Vector Stores via configuration.
- **Explicit RAG Pipeline**: Clean, un-abstracted Python pipeline (no complex LangChain / LlamaIndex black boxes) showing exact data flow.
- **Interactive Web Interface**: Sleek dark-mode single-page Web App with real-time pipeline execution visualization, document uploader, similarity score indicators, and citation inspector.
- **FastAPI REST API**: Comprehensive RESTful endpoints for document upload, raw text ingestion, vector query execution, index management, and health metrics.
- **Sample Dataset & Full Test Suite**: Pre-loaded enterprise security & HR policy documents, plus complete unit test suite (`unittest`).
- **Snowflake Cortex AI Mapping Guide**: Dedicated mapping document (`docs/snowflake-cortex-mapping.md`) contrasting local code with `CORTEX.SEARCH`, `CORTEX.COMPLETE`, `PARSE_DOCUMENT`, and `VECTOR` types.

---

## 💰 Free Tier & Cost Breakdown

| Component | Default Configuration | Cost | Can it incur charges? |
| :--- | :--- | :--- | :--- |
| **Embedding Generation** | `SentenceTransformerProvider` (`all-MiniLM-L6-v2`) | **$0.00 (Free Local)** | ❌ No (Runs 100% locally on CPU/GPU) |
| **Vector Storage** | `InMemoryVectorStore` + `data/vector_store.json` | **$0.00 (Free Local)** | ❌ No (Uses local memory & JSON file) |
| **LLM Generation** | `MockLLMProvider` or local `Ollama` | **$0.00 (Free Local)** | ❌ No (Runs local synthesis offline) |
| **Text Extraction** | `pypdf`, `TextExtractor`, `MarkdownExtractor` | **$0.00 (Free Local)** | ❌ No (Uses local Python packages) |
| **Web Server & UI** | FastAPI + Vanilla HTML/JS/CSS | **$0.00 (Free Local)** | ❌ No (Served locally on localhost:8000) |
| **Paid Fallbacks (Optional)** | `OPENAI_API_KEY` (Only if explicitly set in `.env`) | Paid API (Optional) | ⚠️ Only if you explicitly add a paid key |

---

## 🏗️ System Architecture & Request Lifecycle

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      INGESTION & INDEXING PHASE                         │
│                                                                         │
│  [ Raw PDF / TXT / MD ]  ──> [ Text Extractor ]                         │
│                                      │                                  │
│                                      v                                  │
│                            [ Recursive Chunker ] (500 chars)            │
│                                      │                                  │
│                                      v                                  │
│                            [ Embedding Provider ] (Local Free)          │
│                                      │                                  │
│                                      v                                  │
│                            [ Cosine Vector Store ] (JSON / Memory)      │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                       QUERY & GENERATION PHASE                          │
│                                                                         │
│  [ User Query ] ──> [ Query Embedding ] ──> [ Cosine Vector Search ]    │
│                                                        │                │
│                                                        v                │
│  [ Grounded LLM Response ] <── [ LLM Provider ] <── [ Context Assembler ]│
└─────────────────────────────────────────────────────────────────────────┘
```

### Request Lifecycle
1. **Document Ingestion**: File is uploaded or read from disk. `ExtractorFactory` selects the matching extractor (`PDFExtractor`, `MarkdownExtractor`, `TextExtractor`).
2. **Chunking**: `RecursiveCharacterChunker` recursively splits document text using natural paragraph, line, and sentence boundaries while preserving document ID, character offsets, and metadata.
3. **Embedding Generation**: `EmbeddingProvider` transforms text chunks into dense floating-point vector representations.
4. **Vector Storage**: Vectors and chunk metadata are indexed in `InMemoryVectorStore` and serialized to disk (`data/vector_store.json`).
5. **Similarity Search**: User query is embedded into a vector; `InMemoryVectorStore` computes Cosine Similarity dot products (`(A · B) / (||A|| * ||B||)`) and selects the Top-K relevant chunks.
6. **Context Assembly & Prompting**: `ContextAssembler` formats chunks into a context block with citations and character budget control. `PromptBuilder` wraps it in a grounded prompt template.
7. **LLM Generation**: `LLMProvider` generates an accurate, non-hallucinated answer attributed to source documents.

---

## 📁 Repository Directory Structure

```
.
├── App.md                              # Core project requirements specification
├── README.md                           # Comprehensive project documentation
├── Dockerfile                          # Container deployment specification
├── docker-compose.yml                  # Multi-container orchestration spec
├── requirements.txt                    # Python dependencies
├── .env.example                        # Environment variables template
├── config.py                           # Application configuration manager
├── data/
│   ├── samples/                        # Pre-loaded enterprise sample documents
│   └── vector_store.json               # Serialized vector index data
├── docs/
│   └── snowflake-cortex-mapping.md     # 1-to-1 Snowflake & Cortex AI capability map
├── src/
│   ├── api/                            # REST API server
│   │   ├── main.py                     # FastAPI application entrypoint
│   │   ├── models.py                   # Pydantic request/response models
│   │   └── routes.py                   # API endpoint route handlers
│   ├── chunking/                       # Text chunking logic
│   │   └── chunker.py                  # Recursive character chunker implementation
│   ├── embeddings/                     # Embedding providers
│   │   └── provider.py                 # Local, Mock, and OpenAI embedding providers
│   ├── ingestion/                      # Document text extraction
│   │   └── extractor.py                # PDF, TXT, and MD text extractors
│   ├── llm/                            # LLM generation providers
│   │   └── provider.py                 # Mock, OpenAI, and Ollama LLM providers
│   ├── rag/                            # RAG pipeline orchestration
│   │   ├── context_assembler.py        # Context formatting and citation management
│   │   ├── pipeline.py                 # End-to-end RAG pipeline orchestrator
│   │   ├── prompt_builder.py           # Grounded prompt template builder
│   │   └── retriever.py                # Vector store search retriever
│   └── ui/                             # Frontend user interface
│       └── index.html                  # Interactive Single-Page Web App
└── tests/                              # Unit test suite
    ├── test_api.py                     # REST API test cases
    ├── test_chunker.py                 # Text chunker test cases
    ├── test_extractor.py               # Document extractor test cases
    ├── test_pipeline.py                # End-to-end RAG pipeline test cases
    └── test_vector_store.py            # Vector store index test cases
```

---

## 🚀 Quickstart Guide

### Option 1: Run Locally (Python 3.10+)

1. **Clone the repository & create virtual environment**:
   ```bash
   git clone <repo-url>
   cd <repo-dir>
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Linux/macOS:
   source venv/bin/activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment** (Optional):
   ```bash
   cp .env.example .env
   ```

4. **Launch Application**:
   ```bash
   python -m src.api.main
   ```
   Open your browser to **`http://localhost:8000`** to access the Web UI, or **`http://localhost:8000/docs`** for Interactive Swagger API documentation.

---

### Option 2: Run via Docker

```bash
docker-compose up --build
```
Access the application at `http://localhost:8000`.

---

## 🧪 Running Automated Tests

Run the test suite using Python's built-in test runner:
```bash
python -m unittest discover tests
```

---

## ❄️ Snowflake & Cortex AI Alignment

For FDP workshop attendees transitioning from Python RAG code to Snowflake Cortex AI, read the dedicated mapping guide in [`docs/snowflake-cortex-mapping.md`](file:///c:/Users/skand/OneDrive/Desktop/FDP%20-%20Snowflake%20-%20Cortex%20AI%20-%20SVIT%20-%2024.8.26/Apps/Cortex%20AI%20-%20Own%20POC%20-%20V1%20-%20Antigravity/docs/snowflake-cortex-mapping.md).

---

## 📜 License

Open-source under the MIT License. Built for educational and workshop training purposes.
