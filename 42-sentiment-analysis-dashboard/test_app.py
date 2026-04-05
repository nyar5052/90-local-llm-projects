"""Tests for Sentiment Analysis Dashboard."""

import os
import json
import pytest
from unittest.mock import patch
from click.testing import CliRunner

from app import main, read_text_file, analyze_sentiment, display_summary


@pytest.fixture
def sample_reviews(tmp_path):
    """Create a sample reviews file."""
    file_path = tmp_path / "reviews.txt"
    file_path.write_text(
        "This product is amazing! Best purchase ever.\n"
        "Terrible quality, broke after one day.\n"
        "It's okay, nothing special but works fine.\n"
    )
    return str(file_path)


class TestReadTextFile:
    def test_read_valid_file(self, sample_reviews):
        lines = read_text_file(sample_reviews)
        assert len(lines) == 3
        assert "amazing" in lines[0]

    def test_read_nonexistent_file(self):
        with pytest.raises(SystemExit):
            read_text_file("nonexistent.txt")

    def test_read_empty_file(self, tmp_path):
        empty = tmp_path / "empty.txt"
        empty.write_text("")
        with pytest.raises(SystemExit):
            read_text_file(str(empty))


class TestAnalyzeSentiment:
    @patch("app.chat")
    def test_positive_sentiment(self, mock_chat):
        mock_chat.return_value = json.dumps({
            "sentiment": "positive",
            "confidence": 0.95,
            "key_phrases": ["amazing", "best purchase"],
            "summary": "Very positive review expressing high satisfaction.",
        })
        result = analyze_sentiment("This product is amazing!")
        assert result["sentiment"] == "positive"
        assert result["confidence"] == 0.95

    @patch("app.chat")
    def test_negative_sentiment(self, mock_chat):
        mock_chat.return_value = json.dumps({
            "sentiment": "negative",
            "confidence": 0.88,
            "key_phrases": ["terrible", "broke"],
            "summary": "Negative review about product quality.",
        })
        result = analyze_sentiment("Terrible quality, broke after one day.")
        assert result["sentiment"] == "negative"

    @patch("app.chat")
    def test_malformed_response_fallback(self, mock_chat):
        mock_chat.return_value = "I think this is positive but I'm not sure"
        result = analyze_sentiment("Some text")
        assert result["sentiment"] == "neutral"
        assert result["confidence"] == 0.5


class TestCLI:
    @patch("app.check_ollama_running", return_value=True)
    @patch("app.chat")
    def test_cli_table_format(self, mock_chat, mock_check, sample_reviews):
        mock_chat.return_value = json.dumps({
            "sentiment": "positive", "confidence": 0.9,
            "key_phrases": ["good"], "summary": "Positive"
        })
        runner = CliRunner()
        result = runner.invoke(main, ["--file", sample_reviews, "--format", "table"])
        assert result.exit_code == 0

    @patch("app.check_ollama_running", return_value=False)
    def test_cli_ollama_not_running(self, mock_check, sample_reviews):
        runner = CliRunner()
        result = runner.invoke(main, ["--file", sample_reviews])
        assert result.exit_code != 0
