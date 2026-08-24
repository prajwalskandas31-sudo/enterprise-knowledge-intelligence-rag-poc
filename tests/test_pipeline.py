import os
import unittest
import tempfile
from src.embeddings.provider import MockEmbeddingProvider
from src.llm.provider import MockLLMProvider
from src.vector_store.store import InMemoryVectorStore
from src.rag.pipeline import RAGPipeline


class TestRAGPipeline(unittest.TestCase):

    def test_rag_pipeline_end_to_end(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            sample_file = os.path.join(tmp_dir, "security_policy.txt")
            with open(sample_file, "w", encoding="utf-8") as f:
                f.write("Password Security Policy: All employee passwords must be at least 14 characters long.")

            embed_provider = MockEmbeddingProvider()
            vector_store = InMemoryVectorStore()
            llm_provider = MockLLMProvider()

            pipeline = RAGPipeline(
                embedding_provider=embed_provider,
                vector_store=vector_store,
                llm_provider=llm_provider,
            )

            # Ingest document
            ingest_res = pipeline.ingest_document(sample_file)
            self.assertGreaterEqual(ingest_res.chunks_created, 1)
            self.assertEqual(ingest_res.file_name, "security_policy.txt")

            # Query RAG
            query_res = pipeline.query("What is the password length rule?", similarity_threshold=-1.0)
            self.assertEqual(query_res.query, "What is the password length rule?")
            self.assertGreaterEqual(len(query_res.citations), 1)
            self.assertIn("Password Security Policy", query_res.formatted_context)
            self.assertGreater(len(query_res.answer), 0)


if __name__ == "__main__":
    unittest.main()
