"""Tests for Trend Analysis Tool."""

import json
import pytest
from pathlib import Path
from unittest.mock import patch
from click.testing import CliRunner

from app import main, load_text_files, extract_topics, analyze_sentiment_trends


@pytest.fixture
def sample_articles_dir(tmp_path):
    """Create a directory with sample article files."""
    (tmp_path / "article1.txt").write_text(
        "AI and machine learning are transforming healthcare. "
        "New deep learning models show promise in early diagnosis."
    )
    (tmp_path / "article2.txt").write_text(
        "Cybersecurity threats continue to rise. Organizations must "
        "invest in zero-trust architectures to protect their data."
    )
    (tmp_path / "article3.txt").write_text(
        "Remote work trends show that hybrid models are becoming "
        "the new standard. Companies report higher productivity."
    )
    return str(tmp_path)


class TestLoadTextFiles:
    def test_load_valid_directory(self, sample_articles_dir):
        docs = load_text_files(sample_articles_dir)
        assert len(docs) == 3
        assert all("content" in d for d in docs)
        assert all("filename" in d for d in docs)

    def test_load_nonexistent_directory(self):
        with pytest.raises(SystemExit):
            load_text_files("nonexistent_dir")

    def test_load_empty_directory(self, tmp_path):
        with pytest.raises(SystemExit):
            load_text_files(str(tmp_path))

    def test_skips_non_text_files(self, tmp_path):
        (tmp_path / "image.png").write_bytes(b"\x89PNG")
        (tmp_path / "article.txt").write_text("Valid content here.")
        docs = load_text_files(str(tmp_path))
        assert len(docs) == 1


class TestExtractTopics:
    @patch("app.chat")
    def test_extract_topics_success(self, mock_chat):
        mock_chat.return_value = json.dumps({
            "topics": [
                {"name": "AI in Healthcare", "frequency": "high", "trend": "emerging",
                 "description": "AI applications in medical diagnosis", "related_docs": ["article1.txt"]},
                {"name": "Cybersecurity", "frequency": "medium", "trend": "growing",
                 "description": "Rising security threats", "related_docs": ["article2.txt"]},
            ],
            "overall_theme": "Technology trends in enterprise",
        })
        docs = [{"filename": "a.txt", "content": "test content", "size": 12, "modified": 0}]
        result = extract_topics(docs)
        assert len(result["topics"]) == 2
        assert result["topics"][0]["name"] == "AI in Healthcare"

    @patch("app.chat")
    def test_extract_topics_malformed_response(self, mock_chat):
        mock_chat.return_value = "Here are some trends I noticed..."
        docs = [{"filename": "a.txt", "content": "content", "size": 7, "modified": 0}]
        result = extract_topics(docs)
        assert "topics" in result


class TestAnalyzeSentimentTrends:
    @patch("app.chat")
    def test_sentiment_analysis(self, mock_chat):
        mock_chat.return_value = json.dumps({
            "overall_sentiment": "mixed",
            "sentiment_distribution": {"positive": 2, "negative": 1, "neutral": 0},
            "sentiment_shifts": ["Shift from negative to positive on AI topic"],
            "key_positive_themes": ["AI progress"],
            "key_negative_themes": ["Security concerns"],
        })
        docs = [{"filename": "a.txt", "content": "good content", "size": 12, "modified": 0}]
        result = analyze_sentiment_trends(docs)
        assert result["overall_sentiment"] == "mixed"
        assert result["sentiment_distribution"]["positive"] == 2


class TestCLI:
    @patch("app.check_ollama_running", return_value=True)
    @patch("app.chat")
    def test_cli_analyze_directory(self, mock_chat, mock_check, sample_articles_dir):
        mock_chat.return_value = json.dumps({
            "topics": [{"name": "AI", "frequency": "high", "trend": "emerging",
                        "description": "AI trends", "related_docs": []}],
            "overall_theme": "Tech trends",
        })
        runner = CliRunner()
        result = runner.invoke(main, ["--dir", sample_articles_dir, "--timeframe", "last month"])
        assert result.exit_code == 0

    @patch("app.check_ollama_running", return_value=False)
    def test_cli_ollama_not_running(self, mock_check, sample_articles_dir):
        runner = CliRunner()
        result = runner.invoke(main, ["--dir", sample_articles_dir])
        assert result.exit_code != 0
