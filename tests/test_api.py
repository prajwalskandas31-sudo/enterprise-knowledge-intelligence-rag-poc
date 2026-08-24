import unittest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from src.api.main import app


class TestAPI(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)

    def test_api_health(self):
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "healthy")
        self.assertIn("documents_indexed", data)
        self.assertIn("cortex_configured", data)

    def test_api_config(self):
        response = self.client.get("/api/config")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("chunk_size", data)
        self.assertIn("embedding_provider", data)
        self.assertIn("snowflake_semantic_view", data)

    def test_api_ingest_text_and_rag_query(self):
        # Ingest inline text
        ingest_resp = self.client.post(
            "/api/ingest-text",
            json={
                "file_name": "api_test_doc.txt",
                "text_content": "Enterprise security policy requires multi-factor authentication for remote access.",
            },
        )
        self.assertEqual(ingest_resp.status_code, 200)

        # Query API for document question (routes to RAG)
        query_resp = self.client.post(
            "/api/query",
            json={"query": "What does the security policy say about remote access?", "mode": "rag"},
        )
        self.assertEqual(query_resp.status_code, 200)
        query_data = query_resp.json()
        self.assertEqual(query_data["source"], "rag")
        self.assertGreaterEqual(len(query_data["citations"]), 1)

    @patch("requests.post")
    def test_api_cortex_query_routing(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "message": {
                "role": "analyst",
                "content": [
                    {"type": "text", "text": "Highest average revenue city is New York."},
                    {"type": "sql", "statement": "SELECT city, AVG(annual_revenue) FROM customers GROUP BY city ORDER BY 2 DESC LIMIT 1;"}
                ]
            },
            "request_id": "req-cortex-api-1"
        }
        mock_post.return_value = mock_response

        query_resp = self.client.post(
            "/api/query",
            json={"query": "Which city has the highest average customer revenue?"},
        )
        self.assertEqual(query_resp.status_code, 200)
        query_data = query_resp.json()
        self.assertEqual(query_data["source"], "cortex_analyst")
        self.assertIn("New York", query_data["answer"])
        self.assertIn("SELECT city", query_data["sql"])
        self.assertEqual(query_data["request_id"], "req-cortex-api-1")


if __name__ == "__main__":
    unittest.main()
