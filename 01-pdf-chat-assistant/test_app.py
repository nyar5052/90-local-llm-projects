"""Tests for PDF Chat Assistant."""

import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app import (
    chunk_text,
    find_relevant_chunks,
    ask_question,
    extract_text_from_pdf,
    main,
)


class TestChunkText:
    """Tests for text chunking functionality."""

    def test_short_text_single_chunk(self):
        text = "This is a short text."
        chunks = chunk_text(text, chunk_size=100)
        assert len(chunks) == 1
        assert chunks[0] == text

    def test_long_text_multiple_chunks(self):
        text = "A" * 5000
        chunks = chunk_text(text, chunk_size=2000, overlap=200)
        assert len(chunks) > 1
        assert all(len(c) <= 2000 for c in chunks)

    def test_chunk_overlap(self):
        text = "ABCDEFGHIJ" * 100
        chunks = chunk_text(text, chunk_size=200, overlap=50)
        if len(chunks) >= 2:
            end_of_first = chunks[0][-50:]
            start_of_second = chunks[1][:50]
            assert end_of_first == start_of_second


class TestFindRelevantChunks:
    """Tests for relevant chunk finding."""

    def test_finds_matching_chunks(self):
        chunks = [
            "Python is a programming language",
            "Cooking recipes for dinner",
            "Python data science tools",
        ]
        result = find_relevant_chunks("What is Python?", chunks, top_k=2)
        assert len(result) == 2
        assert "Python" in result[0]

    def test_returns_top_k(self):
        chunks = ["chunk1", "chunk2", "chunk3", "chunk4"]
        result = find_relevant_chunks("test", chunks, top_k=2)
        assert len(result) == 2

    def test_empty_chunks(self):
        result = find_relevant_chunks("test", [], top_k=3)
        assert result == []


class TestAskQuestion:
    """Tests for the ask_question function."""

    @patch("app.chat")
    def test_ask_returns_answer(self, mock_chat):
        mock_chat.return_value = "The answer is 42."
        result = ask_question("What is the answer?", ["context chunk"], [])
        assert result == "The answer is 42."
        mock_chat.assert_called_once()

    @patch("app.chat")
    def test_ask_includes_history(self, mock_chat):
        mock_chat.return_value = "Follow-up answer."
        history = [
            {"role": "user", "content": "First question"},
            {"role": "assistant", "content": "First answer"},
        ]
        result = ask_question("Second question?", ["context"], history)
        assert result == "Follow-up answer."
        call_args = mock_chat.call_args
        messages = call_args[0][0]
        assert len(messages) == 3  # history (2) + new question (1)


class TestExtractTextFromPdf:
    """Tests for PDF text extraction."""

    def test_file_not_found(self):
        with pytest.raises(SystemExit):
            extract_text_from_pdf("nonexistent.pdf")

    @patch("app.extract_text_from_pdf")
    def test_extraction_returns_text(self, mock_extract):
        mock_extract.return_value = "[Page 1]\nHello World"
        result = mock_extract("test.pdf")
        assert "Hello World" in result


class TestCLI:
    """Tests for the CLI interface."""

    @patch("app.check_ollama_running", return_value=False)
    def test_cli_exits_when_ollama_down(self, mock_check):
        runner = CliRunner()
        result = runner.invoke(main, ["--pdf", __file__])
        assert result.exit_code != 0
