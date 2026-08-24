import os
import unittest
import tempfile
from src.ingestion.extractor import TextExtractor, MarkdownExtractor, ExtractorFactory


class TestExtractors(unittest.TestCase):

    def test_text_extractor(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            file_path = os.path.join(tmp_dir, "sample.txt")
            content = "Hello Enterprise Knowledge RAG."
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)

            extractor = TextExtractor()
            doc = extractor.extract(file_path)

            self.assertEqual(doc.file_name, "sample.txt")
            self.assertEqual(doc.text, content)
            self.assertEqual(doc.extension, ".txt")
            self.assertEqual(doc.page_count, 1)

    def test_markdown_extractor(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            file_path = os.path.join(tmp_dir, "sample.md")
            content = "# Title\n\n## Section 1\nThis is markdown text."
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)

            extractor = MarkdownExtractor()
            doc = extractor.extract(file_path)

            self.assertEqual(doc.file_name, "sample.md")
            self.assertEqual(doc.text, content)
            self.assertEqual(doc.extension, ".md")
            self.assertIn("# Title", doc.metadata["headers"])

    def test_extractor_factory(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            txt_file = os.path.join(tmp_dir, "test.txt")
            with open(txt_file, "w", encoding="utf-8") as f:
                f.write("Data")

            md_file = os.path.join(tmp_dir, "test.md")
            with open(md_file, "w", encoding="utf-8") as f:
                f.write("# Title")

            self.assertIsInstance(ExtractorFactory.get_extractor(txt_file), TextExtractor)
            self.assertIsInstance(ExtractorFactory.get_extractor(md_file), MarkdownExtractor)


if __name__ == "__main__":
    unittest.main()
