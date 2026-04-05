"""Tests for Sentiment Analysis Dashboard CLI."""

import json
import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner

from src.sentiment_analyzer.cli import main


class TestCLI:
    @patch("src.sentiment_analyzer.core.get_llm_client")
    def test_cli_table_format(self, mock_get_client, sample_reviews):
        mock_chat = MagicMock(return_value=json.dumps({
            "sentiment": "positive", "confidence": 0.9,
            "key_phrases": ["good"], "summary": "Positive",
        }))
        mock_check = MagicMock(return_value=True)
        mock_get_client.return_value = (mock_chat, mock_check)
        runner = CliRunner()
        result = runner.invoke(main, ["--file", sample_reviews, "--format", "table"])
        assert result.exit_code == 0

    @patch("src.sentiment_analyzer.core.get_llm_client")
    def test_cli_ollama_not_running(self, mock_get_client):
        mock_chat = MagicMock()
        mock_check = MagicMock(return_value=False)
        mock_get_client.return_value = (mock_chat, mock_check)
        runner = CliRunner()
        result = runner.invoke(main, ["--file", "test.txt"])
        assert result.exit_code != 0
