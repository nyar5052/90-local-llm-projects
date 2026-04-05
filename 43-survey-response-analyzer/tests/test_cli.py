"""Tests for Survey Response Analyzer CLI."""

import json
import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner

from src.survey_analyzer.cli import main


class TestCLI:
    @patch("src.survey_analyzer.core.get_llm_client")
    def test_cli_brief_report(self, mock_get_client, sample_survey):
        mock_chat = MagicMock(return_value=json.dumps({
            "themes": [{"name": "Support", "count": 2, "description": "Help", "sentiment": "mixed"}],
            "total_responses": 4,
        }))
        mock_check = MagicMock(return_value=True)
        mock_get_client.return_value = (mock_chat, mock_check)
        runner = CliRunner()
        result = runner.invoke(main, ["--file", sample_survey, "--report", "brief", "--no-recommendations"])
        assert result.exit_code == 0

    @patch("src.survey_analyzer.core.get_llm_client")
    def test_cli_ollama_not_running(self, mock_get_client):
        mock_chat = MagicMock()
        mock_check = MagicMock(return_value=False)
        mock_get_client.return_value = (mock_chat, mock_check)
        runner = CliRunner()
        result = runner.invoke(main, ["--file", "test.csv"])
        assert result.exit_code != 0
