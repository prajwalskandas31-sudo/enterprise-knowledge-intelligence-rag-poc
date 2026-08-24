import unittest
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

    def test_api_config(self):
        response = self.client.get("/api/config")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("chunk_size", data)
        self.assertIn("embedding_provider", data)

    def test_api_ingest_text_and_query(self):
        # Ingest inline text
        ingest_resp = self.client.post(
            "/api/ingest-text",
            json={
                "file_name": "api_test_doc.txt",
                "text_content": "Enterprise data retention policy requires retaining financial records for 7 years.",
            },
        )
        self.assertEqual(ingest_resp.status_code, 200)
        ingest_data = ingest_resp.json()
        self.assertGreaterEqual(ingest_data["chunks_created"], 1)

        # Query API
        query_resp = self.client.post(
            "/api/query",
            json={"query": "How long must financial records be retained?", "top_k": 2},
        )
        self.assertEqual(query_resp.status_code, 200)
        query_data = query_resp.json()
        self.assertEqual(query_data["query"], "How long must financial records be retained?")
        self.assertGreaterEqual(len(query_data["citations"]), 1)


if __name__ == "__main__":
    unittest.main()
