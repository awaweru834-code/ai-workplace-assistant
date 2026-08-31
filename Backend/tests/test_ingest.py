"""
test_ingest.py — Unit tests for the pure helper functions in ingest.py.
No PDF files, Pinecone, or network calls needed.
"""

import os
os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")
os.environ.setdefault("PINECONE_API_KEY", "test-key")

import pytest
from ingest import clean_text, split_into_chunks


class TestCleanText:
    def test_collapses_multiple_spaces(self):
        assert clean_text("hello   world") == "hello world"

    def test_collapses_newlines(self):
        assert clean_text("line1\n\nline2") == "line1 line2"

    def test_strips_leading_trailing_whitespace(self):
        assert clean_text("  hello  ") == "hello"

    def test_empty_string(self):
        assert clean_text("") == ""

    def test_mixed_whitespace(self):
        result = clean_text("  foo\t\nbar  baz  ")
        assert result == "foo bar baz"


class TestSplitIntoChunks:
    def test_short_text_produces_one_chunk(self):
        text = " ".join(["word"] * 10)
        chunks = split_into_chunks(text, chunk_words=500, overlap_words=50)
        assert len(chunks) == 1
        assert chunks[0] == text

    def test_long_text_produces_multiple_chunks(self):
        text = " ".join([f"word{i}" for i in range(1100)])
        chunks = split_into_chunks(text, chunk_words=500, overlap_words=50)
        assert len(chunks) >= 2

    def test_chunks_do_not_exceed_word_limit(self):
        text = " ".join([f"w{i}" for i in range(2000)])
        chunks = split_into_chunks(text, chunk_words=500, overlap_words=50)
        for chunk in chunks:
            assert len(chunk.split()) <= 500

    def test_overlap_repeats_words(self):
        """The last `overlap_words` of chunk N should start chunk N+1."""
        words = [f"w{i}" for i in range(600)]
        text = " ".join(words)
        chunks = split_into_chunks(text, chunk_words=500, overlap_words=50)
        assert len(chunks) >= 2
        tail_of_first = chunks[0].split()[-50:]
        head_of_second = chunks[1].split()[:50]
        assert tail_of_first == head_of_second

    def test_empty_text_returns_no_chunks(self):
        chunks = split_into_chunks("", chunk_words=500, overlap_words=50)
        assert chunks == []

    def test_exact_chunk_size_produces_one_chunk(self):
        text = " ".join(["x"] * 500)
        chunks = split_into_chunks(text, chunk_words=500, overlap_words=50)
        assert len(chunks) == 1
