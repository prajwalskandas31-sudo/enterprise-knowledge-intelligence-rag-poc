# Enterprise Knowledge Intelligence RAG & Snowflake Cortex Analyst POC 🧠⚡

An open-source, modular, dual-engine **Retrieval-Augmented Generation (RAG)** and **Snowflake Cortex Analyst** Proof-of-Concept built from scratch in Python. Designed for enterprise intelligence demonstrations, Faculty Development Programs (FDP), and developer training.

> [!TIP]
> **100% Free Tier & Local Zero-Cost Guarantee**: By default, this entire application runs **100% locally and completely free of charge**. It uses open-source embedding models (`sentence-transformers`), local text extractors (`pypdf`), local vector storage (`numpy`), and an offline grounded synthesis engine (`MockLLMProvider` or local `Ollama`). When configured with a Snowflake PAT token, it seamlessly executes live SQL queries against Snowflake Cortex Analyst.

---

## 🌐 Live Repository & Hosted Application Links

- **GitHub Repository**: [https://github.com/prajwalskandas31-sudo/enterprise-knowledge-intelligence-rag-poc](https://github.com/prajwalskandas31-sudo/enterprise-knowledge-intelligence-rag-poc)
- **Hosted Web Interface (GitHub Pages)**: [https://prajwalskandas31-sudo.github.io/enterprise-knowledge-intelligence-rag-poc/](https://prajwalskandas31-sudo.github.io/enterprise-knowledge-intelligence-rag-poc/)
- **Session Presentation Guide**: [`SESSION_GUIDE.md`](file:///c:/Users/skand/OneDrive/Desktop/FDP%20-%20Snowflake%20-%20Cortex%20AI%20-%20SVIT%20-%2024.8.26/Apps/Cortex%20AI%20-%20Own%20POC%20-%20V1%20-%20Antigravity/SESSION_GUIDE.md) *(Contains step-by-step speaker notes, pre-loaded file descriptions, and demo script)*

---

## 🛠️ Technology Stack & Component Mapping

The following table breaks down every technology used in this POC and the exact action or feature it performs:

| Technology / Library | Component Layer | Action / Feature Performed |
| :--- | :--- | :--- |
| **FastAPI** | Backend API Framework | Provides high-performance RESTful API endpoints (`/api/query`, `/api/upload`, `/api/documents`, `/api/health`). |
| **Uvicorn** | ASGI Web Server | Runs the asynchronous Python backend server listening on port `8000`. |
| **Snowflake Cortex Analyst REST API** | Structured Natural Language Engine | Translates natural language analytics questions into valid, optimized SQL statements using semantic view models. |
| **Snowflake SQL REST API (`/api/v2/statements`)** | Live SQL Execution | Executes Cortex Analyst generated SQL directly on Snowflake Data Warehouse and returns real-time tabular rows and column metadata. |
| **Sentence-Transformers (`all-MiniLM-L6-v2`)** | Vector Embedding Engine | Generates 384-dimensional dense vector embeddings locally on CPU/GPU (100% free, no external API keys required). |
| **NumPy** | Vector Search Engine | Computes high-speed Cosine Similarity dot-product matrix operations (`(A · B) / (||A|| * ||B||)`) to retrieve Top-K relevant context chunks. |
| **HTML5 / CSS3 / Vanilla JavaScript** | Single-Page Application (SPA) Frontend | Implements a responsive dark-mode UI with glassmorphism styling, live tabular data renderer, intent routing badge, and context inspector. |
| **Pydantic v2** | Schema Validation | Validates request payloads and structures unified response objects (`UnifiedQueryResponse`, `QueryApiRequest`). |
| **PyPDF & Python-Multipart** | Ingestion & Text Extraction | Extracts raw text from PDF, Markdown, and TXT files and handles multipart file uploads in real-time. |
| **Python `unittest` & `httpx`** | Test Automation | Executes comprehensive unit test suite (19/19 passing tests) and API integration verification. |

---

## 🌟 Key Features

- **Dual Intelligence Routing**: Automatically routes quantitative analytics questions to Snowflake Cortex Analyst and document knowledge questions to Enterprise RAG.
- **Live Tabular SQL Data Table**: Displays live query result tables (columns and rows) directly on screen for Cortex Analyst queries, along with toggleable generated SQL statement viewer.
- **100% Free & Offline RAG Mode**: Works out of the box with zero external API keys using local sentence transformers (`all-MiniLM-L6-v2`).
- **Interactive Web Interface**: Sleek dark-mode single-page Web App with pipeline visualization, real-time file dropzone, similarity score badges, and citation inspector.
- **Pre-Loaded Sample Datasets**: Pre-packed with enterprise security policies, HR remote work rules, and RAG architecture documents in `data/samples/`.
- **Presenter & Session Guide**: Includes [`SESSION_GUIDE.md`](file:///c:/Users/skand/OneDrive/Desktop/FDP%20-%20Snowflake%20-%20Cortex%20AI%20-%20SVIT%20-%2024.8.26/Apps/Cortex%20AI%20-%20Own%20POC%20-%20V1%20-%20Antigravity/SESSION_GUIDE.md) to help presenters speak about the pre-loaded files and conduct live demo sessions.

---

## 📂 Pre-Loaded Resource Files & Repository Structure

All necessary resource files to power both RAG and Snowflake Cortex functions are pre-packaged in the repository:

```
.
├── SESSION_GUIDE.md                    # Step-by-step speaker guide & demo script
├── README.md                           # Comprehensive documentation & tech map
├── Dockerfile                          # Container deployment specification
├── docker-compose.yml                  # Multi-container orchestration spec
├── requirements.txt                    # Python dependencies
├── .env.example                        # Credentials template (copy to .env)
├── test_live_smoke.py                  # Live end-to-end smoke test runner
├── data/
│   ├── samples/                        # Pre-loaded resource files powering RAG:
│   │   ├── enterprise_security_policy.md # Security, password, MFA & incident SLAs
│   │   ├── hr_remote_work_guidelines.txt # Hybrid WFH policy & $500 hardware stipend
│   │   └── rag_architecture_overview.md  # Vector RAG architecture overview
│   └── vector_store.json               # Local vector storage index data
├── src/
│   ├── api/                            # FastAPI server, schemas & route handlers
│   ├── chunking/                       # Recursive character chunker logic
│   ├── cortex/                         # Snowflake Cortex Analyst client & SQL API executor
│   ├── embeddings/                     # Local sentence transformer vector embedding provider
│   ├── ingestion/                      # PDF, TXT, and Markdown text extractors
│   ├── llm/                            # Grounded LLM synthesis providers
│   ├── rag/                            # RAG retriever, context assembler & prompt builder
│   └── ui/                             # HTML5/CSS3/JS Web UI with tabular result renderer
└── tests/                              # Automated unittest test suite
```

---

## 🚀 Quickstart Guide & Credentials Setup

### 1. Clone the Repository & Setup Environment
```bash
git clone https://github.com/prajwalskandas31-sudo/enterprise-knowledge-intelligence-rag-poc.git
cd enterprise-knowledge-intelligence-rag-poc
python -m venv venv

# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Configure Credentials (.env)
Copy `.env.example` to `.env` and fill in your Snowflake credentials:
```bash
cp .env.example .env
```
Open `.env` and replace `SNOWFLAKE_PAT` with your token:
```env
SNOWFLAKE_BASE_URL="https://YOUR_ACCOUNT.snowflakecomputing.com"
SNOWFLAKE_PAT="your_snowflake_programmatic_access_token_here"
SNOWFLAKE_SEMANTIC_VIEW="FDP_CORTEX_POC.RAW_DATA.CUSTOMER_ANALYTICS"
```

### 3. Launch the Server
```bash
python -m src.api.main
```
Open your browser at **`http://localhost:8000`** to interact with the Dual Engine UI.

---

## 🧪 Testing & Live Demonstration

- **Run Automated Unit Tests**:
  ```bash
  python -m unittest discover tests
  ```
- **Run Live Snowflake Cortex Smoke Test**:
  ```bash
  python test_live_smoke.py
  ```

---

## 📜 License

Open-source under the MIT License. Built for enterprise AI education and training.
