import unittest
from src.ingestion.extractor import DocumentContent
from src.chunking.chunker import RecursiveCharacterChunker


class TestChunker(unittest.TestCase):

    def test_chunker_basic_split(self):
        long_text = "Paragraph one content. " * 30 + "\n\n" + "Paragraph two content. " * 30
        doc = DocumentContent(
            file_name="test_doc.txt",
            file_path="/tmp/test_doc.txt",
            extension=".txt",
            text=long_text,
        )

        chunker = RecursiveCharacterChunker(chunk_size=200, chunk_overlap=20)
        chunks = chunker.split_document(doc)

        self.assertGreater(len(chunks), 1)
        for idx, c in enumerate(chunks):
            self.assertEqual(c.doc_id, "test_doc.txt")
            self.assertEqual(c.chunk_index, idx)
            self.assertLessEqual(len(c.text), 250)
            self.assertGreaterEqual(c.start_char, 0)
            self.assertGreater(c.end_char, c.start_char)


if __name__ == "__main__":
    unittest.main()
