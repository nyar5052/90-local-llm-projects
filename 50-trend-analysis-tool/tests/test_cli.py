"""Tests for the CLI interface (src.trend_analyzer.cli)."""

import json
import pytest
from unittest.mock import patch, MagicMock

from click.testing import CliRunner

from src.trend_analyzer.cli import main


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
    return str(tmp_path)


TOPICS_JSON = json.dumps({
    "topics": [
        {
            "name": "AI",
            "frequency": "high",
            "trend": "emerging",
            "description": "AI trends",
            "related_docs": [],
        }
    ],
    "overall_theme": "Tech trends",
})

SENTIMENT_JSON = json.dumps({
    "overall_sentiment": "positive",
    "sentiment_distribution": {"positive": 2, "negative": 0, "neutral": 0},
    "sentiment_shifts": [],
    "key_positive_themes": ["AI"],
    "key_negative_themes": [],
})


class TestCLIAnalyze:
    @patch("src.trend_analyzer.cli.check_ollama_running", return_value=True)
    @patch("src.trend_analyzer.core.chat")
    def test_analyze_basic(self, mock_chat, mock_check, sample_articles_dir):
        mock_chat.return_value = TOPICS_JSON
        runner = CliRunner()
        result = runner.invoke(
            main, ["analyze", "--dir", sample_articles_dir, "--timeframe", "last month"]
        )
        assert result.exit_code == 0

    @patch("src.trend_analyzer.cli.check_ollama_running", return_value=True)
    @patch("src.trend_analyzer.core.chat")
    def test_analyze_no_sentiment(self, mock_chat, mock_check, sample_articles_dir):
        mock_chat.return_value = TOPICS_JSON
        runner = CliRunner()
        result = runner.invoke(
            main, ["analyze", "--dir", sample_articles_dir, "--no-sentiment"]
        )
        assert result.exit_code == 0

    @patch("src.trend_analyzer.cli.check_ollama_running", return_value=False)
    def test_analyze_ollama_not_running(self, mock_check, sample_articles_dir):
        runner = CliRunner()
        result = runner.invoke(main, ["analyze", "--dir", sample_articles_dir])
        assert result.exit_code != 0


class TestCLITopics:
    @patch("src.trend_analyzer.cli.check_ollama_running", return_value=True)
    @patch("src.trend_analyzer.core.chat")
    def test_topics_command(self, mock_chat, mock_check, sample_articles_dir):
        mock_chat.return_value = TOPICS_JSON
        runner = CliRunner()
        result = runner.invoke(main, ["topics", "--dir", sample_articles_dir])
        assert result.exit_code == 0


class TestCLISentiment:
    @patch("src.trend_analyzer.cli.check_ollama_running", return_value=True)
    @patch("src.trend_analyzer.core.chat")
    def test_sentiment_command(self, mock_chat, mock_check, sample_articles_dir):
        mock_chat.return_value = SENTIMENT_JSON
        runner = CliRunner()
        result = runner.invoke(main, ["sentiment", "--dir", sample_articles_dir])
        assert result.exit_code == 0


class TestCLIEmerging:
    @patch("src.trend_analyzer.cli.check_ollama_running", return_value=True)
    @patch("src.trend_analyzer.core.chat")
    def test_emerging_command(self, mock_chat, mock_check, sample_articles_dir):
        mock_chat.return_value = TOPICS_JSON
        runner = CliRunner()
        result = runner.invoke(
            main, ["emerging", "--dir", sample_articles_dir, "--threshold", "0.5"]
        )
        assert result.exit_code == 0


class TestCLISchedule:
    def test_schedule_command(self):
        runner = CliRunner()
        result = runner.invoke(main, ["schedule"])
        assert result.exit_code == 0
        assert "Schedule" in result.output or "Enabled" in result.output or "schedule" in result.output.lower()
