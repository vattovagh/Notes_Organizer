"""Tests for the dependency-free parts. Run: python -m unittest discover tests"""

import unittest

from classify_note import classify_text
from rag.chunking import chunk_text
from rag.metrics import first_relevant_rank, retrieval_scores


class ClassifyTests(unittest.TestCase):
    def test_whole_word_only(self):
        self.assertEqual(classify_text("monkey summary"), "Other")

    def test_plural_matches(self):
        self.assertEqual(classify_text("solve these equations"), "Mathematics")

    def test_uppercase_keywords_match(self):
        self.assertEqual(classify_text("DNA and protein"), "Science")
        self.assertEqual(classify_text("REST API and syntax"), "Computer Science")

    def test_empty_is_other(self):
        self.assertEqual(classify_text("   "), "Other")


class ChunkTests(unittest.TestCase):
    def test_empty(self):
        self.assertEqual(chunk_text("  \n "), [])

    def test_short_text_single_chunk(self):
        self.assertEqual(chunk_text("a b c", max_words=10, overlap=2), ["a b c"])

    def test_overlap_and_coverage(self):
        words = [str(i) for i in range(25)]
        chunks = chunk_text(" ".join(words), max_words=10, overlap=3)
        self.assertEqual(chunks[0].split(), words[0:10])
        self.assertEqual(chunks[1].split(), words[7:17])
        self.assertEqual(chunks[-1].split()[-1], "24")
        self.assertTrue(all(len(c.split()) <= 10 for c in chunks))

    def test_bad_args(self):
        with self.assertRaises(ValueError):
            chunk_text("a b", max_words=5, overlap=5)


class MetricTests(unittest.TestCase):
    def test_rank(self):
        self.assertEqual(first_relevant_rank(["a", "b", "c"], ["c", "x"]), 3)
        self.assertEqual(first_relevant_rank(["a"], ["z"]), 0)

    def test_scores(self):
        scores = retrieval_scores([1, 2, 0, 5], k=4)
        self.assertEqual(scores["hit@4"], 0.5)
        self.assertAlmostEqual(scores["mrr"], (1 + 0.5 + 0 + 0.2) / 4)

    def test_empty(self):
        self.assertEqual(retrieval_scores([], 4), {"hit@4": 0.0, "mrr": 0.0})


if __name__ == "__main__":
    unittest.main()
