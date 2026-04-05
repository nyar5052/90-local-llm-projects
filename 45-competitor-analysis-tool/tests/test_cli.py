"""Tests for Competitor Analysis Tool CLI."""

import json
import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner

from src.competitor_analyzer.cli import main


class TestCLI:
    @patch("src.competitor_analyzer.core.get_llm_client")
    def test_cli_full_report(self, mock_get_client):
        mock_chat = MagicMock(return_value=json.dumps({
            "strengths": ["s1"], "weaknesses": ["w1"],
            "opportunities": ["o1"], "threats": ["t1"],
        }))
        mock_check = MagicMock(return_value=True)
        mock_get_client.return_value = (mock_chat, mock_check)
        runner = CliRunner()
        result = runner.invoke(main, [
            "--company", "TestCo",
            "--competitors", "Comp1,Comp2",
            "--industry", "tech",
        ])
        assert result.exit_code == 0

    @patch("src.competitor_analyzer.core.get_llm_client")
    def test_cli_ollama_not_running(self, mock_get_client):
        mock_chat = MagicMock()
        mock_check = MagicMock(return_value=False)
        mock_get_client.return_value = (mock_chat, mock_check)
        runner = CliRunner()
        result = runner.invoke(main, [
            "--company", "TestCo",
            "--competitors", "Comp1",
            "--industry", "tech",
        ])
        assert result.exit_code != 0

    @patch("src.competitor_analyzer.core.get_llm_client")
    def test_cli_swot_only(self, mock_get_client):
        mock_chat = MagicMock(return_value=json.dumps({
            "strengths": ["s1"], "weaknesses": ["w1"],
            "opportunities": ["o1"], "threats": ["t1"],
        }))
        mock_check = MagicMock(return_value=True)
        mock_get_client.return_value = (mock_chat, mock_check)
        runner = CliRunner()
        result = runner.invoke(main, [
            "--company", "TestCo",
            "--competitors", "Comp1",
            "--industry", "tech",
            "--swot-only", "--no-features", "--no-pricing", "--no-actions",
        ])
        assert result.exit_code == 0
