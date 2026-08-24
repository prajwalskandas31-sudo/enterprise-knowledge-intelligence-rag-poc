You are working inside my existing repository:

Enterprise Knowledge Intelligence RAG POC

IMPORTANT CONTEXT:
This repository is already a working POC created earlier. DO NOT rebuild it from scratch, replace the existing architecture, or unnecessarily refactor working functionality.

The goal now is to integrate Snowflake Cortex Analyst into the EXISTING application as a second intelligence capability alongside the existing enterprise-document RAG pipeline.

==================================================
1. CURRENT REPOSITORY
==================================================

The repository currently has approximately this structure:

src/
├── api/
│   ├── main.py
│   ├── models.py
│   ├── routes.py
│   └── __init__.py
├── chunking/
├── embeddings/
├── ingestion/
├── llm/
├── rag/
│   ├── context_assembler.py
│   ├── pipeline.py
│   ├── prompt_builder.py
│   ├── retriever.py
│   └── __init__.py
├── ui/
│   └── index.html
├── vector_store/
│   └── store.py
└── config.py

There are also:
- .env
- .env.example
- requirements.txt
- Dockerfile
- docker-compose.yml
- README.md
- App.md
- tests/

Existing RAG functionality MUST continue to work.

==================================================
2. SNOWFLAKE ENVIRONMENT
==================================================

I have already manually created and validated the Snowflake environment.

Snowflake account:
- Organization: DKQGJIE
- Account name: RM49461
- Account locator: VN97359
- Region: AZURE_CENTRALINDIA
- Role currently used for the POC: ACCOUNTADMIN
- Warehouse: COMPUTE_WH
- Database: FDP_CORTEX_POC
- Schema: RAW_DATA

The Cortex Analyst semantic view is:

FDP_CORTEX_POC.RAW_DATA.CUSTOMER_ANALYTICS

IMPORTANT:
Do not recreate the database, schema, table, semantic view, or sample data.
They already exist and Cortex Analyst has already been validated manually in Snowsight.

==================================================
3. CORTEX ANALYST API HAS ALREADY BEEN VALIDATED
==================================================

A standalone Python test outside the application successfully called Snowflake Cortex Analyst.

The request:

POST /api/v2/cortex/analyst/message

returned:

STATUS: 200

The test question was:

"Which city has the highest average customer revenue?"

Cortex Analyst successfully generated SQL similar to:

SELECT
    city,
    AVG(annual_revenue) AS avg_annual_revenue
FROM __customers
GROUP BY city
ORDER BY avg_annual_revenue DESC NULLS LAST
LIMIT 1;

The response also contained:
- analyst text
- generated SQL
- request_id
- verified_query_used confidence metadata
- model metadata
- warnings
- response metadata

Therefore:

DO NOT spend time trying to solve Cortex Analyst connectivity from scratch.

The REST API connectivity is already proven.

==================================================
4. AUTHENTICATION
==================================================

A Snowflake Programmatic Access Token (PAT) has already been generated manually.

The PAT is stored ONLY in the local .env file.

DO NOT:
- ask me to paste the PAT
- print the PAT
- hardcode the PAT
- commit the PAT
- place the PAT in README.md
- place the PAT in frontend JavaScript
- place the PAT in source control

The application must load it from environment variables.

The existing .gitignore MUST ensure .env is ignored.

Expected environment variables should be:

SNOWFLAKE_BASE_URL=https://DKQGJIE-RM49461.snowflakecomputing.com
SNOWFLAKE_ACCOUNT=DKQGJIE-RM49461
SNOWFLAKE_USER=PRAJWALSKANDAS31
SNOWFLAKE_PAT=<existing local secret>
SNOWFLAKE_ROLE=ACCOUNTADMIN
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
SNOWFLAKE_DATABASE=FDP_CORTEX_POC
SNOWFLAKE_SCHEMA=RAW_DATA
SNOWFLAKE_SEMANTIC_VIEW=FDP_CORTEX_POC.RAW_DATA.CUSTOMER_ANALYTICS

DO NOT overwrite or remove the existing PAT.

If an environment variable already exists under a slightly different name, inspect the existing configuration and normalize it rather than creating unnecessary duplicates.

==================================================
5. IMPLEMENT CORTEX ANALYST AS A SEPARATE SERVICE
==================================================

Add a clean Cortex Analyst integration.

Prefer:

src/cortex/
    __init__.py
    analyst.py

or another equally clean location consistent with the existing architecture.

Create a dedicated CortexAnalystClient/service responsible ONLY for communication with Snowflake Cortex Analyst.

Responsibilities:

1. Load configuration securely.
2. Construct the Cortex Analyst endpoint.
3. Authenticate using the PAT.
4. Send natural-language questions.
5. Specify the semantic view:
   FDP_CORTEX_POC.RAW_DATA.CUSTOMER_ANALYTICS
6. Parse the Cortex Analyst response.
7. Return a clean internal response model.

Do not mix Cortex Analyst HTTP logic into the frontend.

Do not put Snowflake credentials in frontend code.

==================================================
6. REQUEST FORMAT
==================================================

Use the Snowflake Cortex Analyst REST API.

Endpoint:

{SNOWFLAKE_BASE_URL}/api/v2/cortex/analyst/message

Use:

Authorization: Bearer <PAT>

Content-Type: application/json

X-Snowflake-Authorization-Token-Type: PROGRAMMATIC_ACCESS_TOKEN

The request should contain the user's natural-language question and the semantic view.

Example conceptual payload:

{
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": "Which city has the highest average customer revenue?"
        }
      ]
    }
  ],
  "semantic_view": "FDP_CORTEX_POC.RAW_DATA.CUSTOMER_ANALYTICS"
}

Use the exact API behavior that was already proven by the standalone test.

==================================================
7. NORMALIZE THE RESPONSE
==================================================

Do not expose raw Snowflake JSON directly to the frontend.

Create an internal response structure approximately like:

{
    "answer": "...",
    "sql": "...",
    "request_id": "...",
    "verified_query_used": true,
    "confidence": {...},
    "model_names": [...],
    "warnings": [...]
}

Handle cases where SQL or confidence metadata is absent.

Do not crash if optional fields are missing.

==================================================
8. PRESERVE EXISTING RAG
==================================================

THIS IS CRITICAL.

The current RAG pipeline must continue functioning exactly as before.

Do not replace:
- chunking
- embeddings
- vector store
- retriever
- context assembler
- prompt builder
- existing LLM provider

Cortex Analyst is an ADDITIONAL capability.

The final application should support both:

A. Enterprise document questions
→ existing RAG pipeline

B. Structured business-data questions
→ Snowflake Cortex Analyst

==================================================
9. ADD QUERY ROUTING
==================================================

Implement a lightweight query-routing/orchestration layer.

Do NOT blindly route every question to Cortex Analyst.

At minimum, distinguish:

STRUCTURED DATA / ANALYTICS QUESTIONS:

Examples:
- What is the total annual revenue?
- Which city has the highest average customer revenue?
- Which industry has the most customers?
- Show customers with revenue above 10 million.
- Which industry generates the most revenue?

These should route to Cortex Analyst.

DOCUMENT / KNOWLEDGE QUESTIONS:

Examples:
- What is our remote work policy?
- What does the enterprise security policy say about remote access?
- What are the HR guidelines?
- What does the security document say about VPN access?

These should route to the existing RAG pipeline.

The routing implementation should be simple, explainable, and easy to replace later.

Do NOT introduce another external LLM solely to perform routing unless the existing architecture already provides one and it is genuinely necessary.

==================================================
10. UNIFIED API
==================================================

Expose a unified backend endpoint through the existing FastAPI application.

Prefer extending the existing API rather than creating a second backend.

For example:

POST /api/query

Request:

{
    "question": "Which city has the highest average customer revenue?"
}

Response should identify the source:

{
    "source": "cortex_analyst",
    "answer": "...",
    "sql": "...",
    "request_id": "...",
    "verified_query_used": true
}

For a RAG question:

{
    "source": "rag",
    "answer": "...",
    "sources": [...]
}

Adapt this to the existing API conventions rather than breaking existing endpoints.

==================================================
11. FRONTEND
==================================================

Modify the EXISTING UI rather than building a new application.

The user should have a single chat/query interface.

When the query is answered by Cortex Analyst, clearly show:

Cortex Analyst / Snowflake

and display:
- natural-language answer
- optionally generated SQL in a collapsible section
- verified-query indicator when available

When answered by RAG, show:

Enterprise RAG

and display:
- answer
- document/source references according to the existing implementation

Do not expose:
- PAT
- Snowflake credentials
- internal authentication headers

==================================================
12. ERROR HANDLING
==================================================

Handle these cases cleanly:

401:
Authentication/network-policy problem

403:
Permission/role problem

400:
Invalid Cortex Analyst request or semantic model problem

404:
Invalid endpoint/account configuration

429:
Rate limiting

5xx:
Snowflake service failure

The frontend should show a useful human-readable error rather than a Python traceback.

Do not leak secrets in errors or logs.

==================================================
13. CONFIGURATION
==================================================

Update .env.example with placeholders only.

Example:

SNOWFLAKE_BASE_URL=
SNOWFLAKE_ACCOUNT=
SNOWFLAKE_USER=
SNOWFLAKE_PAT=
SNOWFLAKE_ROLE=ACCOUNTADMIN
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
SNOWFLAKE_DATABASE=FDP_CORTEX_POC
SNOWFLAKE_SCHEMA=RAW_DATA
SNOWFLAKE_SEMANTIC_VIEW=FDP_CORTEX_POC.RAW_DATA.CUSTOMER_ANALYTICS

Never put the actual PAT into .env.example.

Verify .gitignore contains:

.env

==================================================
14. DEPENDENCIES
==================================================

Inspect requirements.txt first.

Only add packages that are actually required.

The standalone test already uses:
- requests
- python-dotenv

Reuse existing dependencies where possible.

Do not unnecessarily introduce large frameworks.

==================================================
15. TESTS
==================================================

Add tests for the Cortex Analyst integration.

At minimum:

1. Configuration loading test
2. Request payload construction test
3. Cortex response parsing test
4. Successful analyst response test using mocked HTTP
5. Error response handling test
6. Query-routing tests
7. Unified API test

DO NOT make the test suite dependent on my real PAT.

Mock external Snowflake API calls in automated tests.

If a live integration test is useful, make it an explicitly separate optional test.

==================================================
16. LIVE SMOKE TEST
==================================================

After implementation, run a live smoke test using my existing local .env.

Use:

"What is the total annual revenue across all customers?"

Then:

"Which city has the highest average customer revenue?"

The implementation should successfully receive STATUS 200 from Cortex Analyst.

Do not print the PAT.

Show:
- HTTP status
- parsed answer
- whether SQL was returned
- request_id
- whether verified query metadata was present

Do not expose the authentication token.

==================================================
17. DO NOT BREAK EXISTING APPLICATION
==================================================

Before modifying anything:

1. Inspect the entire repository.
2. Understand existing architecture.
3. Identify current API contracts.
4. Identify existing frontend behavior.
5. Identify existing configuration handling.
6. Identify current tests.

Then make the smallest clean changes necessary.

Do not rewrite working files unnecessarily.

Do not replace the existing RAG implementation.

Do not delete existing functionality.

Do not rename large numbers of files.

==================================================
18. DOCUMENTATION
==================================================

Update README.md and/or App.md to explain the new architecture.

Include a section:

"Snowflake Cortex Analyst Integration"

Explain:

Natural Language
→ Cortex Analyst
→ Semantic View
→ SQL Generation
→ Snowflake Execution
→ Result

Also explain the distinction between:

Existing RAG:
Unstructured enterprise documents

Cortex Analyst:
Structured enterprise data

Explain that the application can now route questions to the appropriate intelligence layer.

Do not include secrets.

==================================================
19. FDP DEMONSTRATION QUALITY
==================================================

The implementation should make the architecture easy to demonstrate.

The final POC should clearly show:

1. Existing Enterprise RAG
2. Snowflake structured-data analytics
3. Cortex Analyst
4. Semantic View
5. Natural-language-to-SQL capability
6. Generated SQL transparency
7. Unified application experience

The goal is NOT merely to make an API call.

The goal is to demonstrate how an independently built enterprise AI application can integrate with Snowflake Cortex Analyst while retaining its own RAG architecture.

==================================================
20. IMPORTANT CONSTRAINTS
==================================================

DO NOT:

- use OpenAI for Cortex Analyst
- use Gemini for Cortex Analyst
- use Claude API directly
- implement our own NL-to-SQL engine
- call Snowflake generic AI_COMPLETE functions for this feature
- depend on Snowsight UI
- recreate the Snowflake semantic view
- recreate the Snowflake database
- hardcode credentials
- expose PAT in frontend
- commit .env
- replace existing RAG
- create a second unrelated application
- rewrite the entire repository

Cortex Analyst MUST be consumed through the Snowflake REST API that has already been validated successfully.

==================================================
21. IMPORTANT: VERIFY BEFORE FINISHING
==================================================

After implementation:

- run existing tests
- run new Cortex Analyst unit tests
- run application startup
- run live Cortex Analyst smoke test
- verify existing RAG still works
- verify one Cortex Analyst question works
- verify one RAG question works
- verify .env is ignored
- verify no PAT appears in tracked files
- inspect git diff
- summarize exactly what files were changed

If something fails, diagnose and fix it rather than stopping at the first error.

Do not claim success without actually running the tests.

==================================================
22. FINAL OUTPUT
==================================================

At the end, provide me with:

1. Files created
2. Files modified
3. Architecture changes
4. How Cortex Analyst is integrated
5. How query routing works
6. API endpoints added/modified
7. Tests executed and results
8. Live Cortex Analyst smoke-test result
9. Existing RAG regression-test result
10. Any remaining limitations
11. Exact commands I should use to run the application
12. A concise explanation I can use during my FDP presentation

MOST IMPORTANT:

Work with the existing repository.
Inspect first.
Implement incrementally.
Preserve working functionality.
Use the already-proven Cortex Analyst REST API integration.
Do not ask me to manually edit code unless absolutely necessary.

Begin by inspecting the repository and current architecture.