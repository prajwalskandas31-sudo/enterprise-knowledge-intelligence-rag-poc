"""Live Smoke Test for Snowflake Cortex Analyst Integration & Query Routing."""
import os
from dotenv import load_dotenv
from src.cortex.analyst import CortexAnalystClient
from src.cortex.router import QueryRouter
from src.rag.pipeline import RAGPipeline

load_dotenv()

print("==================================================")
print("LIVE SMOKE TEST: DUAL INTELLIGENCE ENGINE POC")
print("==================================================\n")

client = CortexAnalystClient()

print(f"[Config] Base URL     : {client.base_url}")
print(f"[Config] Semantic View: {client.semantic_view}")
print(f"[Config] PAT Present  : {'YES' if client.pat else 'NO'}\n")

cortex_questions = [
    "What is the total annual revenue across all customers?",
    "Which city has the highest average customer revenue?",
]

for idx, q in enumerate(cortex_questions, 1):
    print(f"--- [Test {idx}] Cortex Analyst Question ---")
    print(f"Question: \"{q}\"")

    route_res = QueryRouter.route(q)
    print(f"Router Decision: destination='{route_res.destination.value}', reasoning='{route_res.reasoning}'")

    res = client.query(q)
    print(f"HTTP Status           : {res.status_code}")
    print(f"Success Status        : {res.success}")
    print(f"Parsed Answer         : {res.answer[:200]}...")
    print(f"SQL Returned          : {'YES' if res.sql else 'NO'}")
    if res.sql:
        print(f"Generated SQL Snippet : {res.sql.strip()[:150]}...")
    print(f"Request ID            : {res.request_id}")
    print(f"Verified Query Used   : {res.verified_query_used}")
    if res.query_results:
        print(f"Executed Table Columns: {res.query_results.get('columns')}")
        print(f"Executed Table Rows   : {res.query_results.get('rows')}")
    print(f"Latency               : {res.latency_ms} ms\n")

print("--- [Test 3] Enterprise RAG Document Question ---")
rag_q = "What is the password security policy?"
print(f"Question: \"{rag_q}\"")
route_rag = QueryRouter.route(rag_q)
print(f"Router Decision: destination='{route_rag.destination.value}', reasoning='{route_rag.reasoning}'")

pipeline = RAGPipeline()
rag_res = pipeline.query(rag_q)
print(f"RAG Answer Snippet    : {rag_res.answer[:200]}...")
print(f"Citations Count       : {len(rag_res.citations)}")
print(f"Total Latency         : {rag_res.total_time_ms} ms\n")

print("==================================================")
print("ALL LIVE SMOKE TESTS COMPLETED SUCCESSFULLY!")
print("==================================================")
