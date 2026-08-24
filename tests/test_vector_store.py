import os
import unittest
import tempfile
from src.chunking.chunker import Chunk
from src.vector_store.store import InMemoryVectorStore


class TestVectorStore(unittest.TestCase):

    def test_vector_store_add_search(self):
        store = InMemoryVectorStore()

        c1 = Chunk(doc_id="doc1.txt", file_name="doc1.txt", chunk_index=0, text="Password security policy", start_char=0, end_char=24)
        c2 = Chunk(doc_id="doc2.txt", file_name="doc2.txt", chunk_index=0, text="Remote work guidelines", start_char=0, end_char=22)

        vec1 = [1.0, 0.0, 0.0]
        vec2 = [0.0, 1.0, 0.0]

        store.add_chunks([c1, c2], [vec1, vec2])

        # Search close to vec1
        query_vec = [0.9, 0.1, 0.0]
        results = store.search(query_vec, top_k=2)

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].chunk.doc_id, "doc1.txt")
        self.assertGreater(results[0].score, results[1].score)

    def test_vector_store_persistence(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            save_file = os.path.join(tmp_dir, "store.json")
            store = InMemoryVectorStore()

            c1 = Chunk(doc_id="doc1.txt", file_name="doc1.txt", chunk_index=0, text="Saved data", start_char=0, end_char=10)
            store.add_chunks([c1], [[0.5, 0.5, 0.0]])
            store.save_to_disk(save_file)

            loaded_store = InMemoryVectorStore()
            loaded_store.load_from_disk(save_file)

            docs = loaded_store.list_documents()
            self.assertEqual(len(docs), 1)
            self.assertEqual(docs[0]["doc_id"], "doc1.txt")


if __name__ == "__main__":
    unittest.main()
