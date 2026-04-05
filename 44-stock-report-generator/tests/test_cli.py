"""Tests for Stock Report Generator CLI."""

import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner

from src.stock_reporter.cli import main


class TestCLI:
    @patch("src.stock_reporter.core.get_llm_client")
    def test_cli_valid_input(self, mock_get_client, sample_stock_csv):
        mock_chat = MagicMock(return_value="# Report\n\nBullish trend observed.")
        mock_check = MagicMock(return_value=True)
        mock_get_client.return_value = (mock_chat, mock_check)
        runner = CliRunner()
        result = runner.invoke(main, ["--file", sample_stock_csv, "--ticker", "AAPL"])
        assert result.exit_code == 0

    @patch("src.stock_reporter.core.get_llm_client")
    def test_cli_ollama_not_running(self, mock_get_client, sample_stock_csv):
        mock_chat = MagicMock()
        mock_check = MagicMock(return_value=False)
        mock_get_client.return_value = (mock_chat, mock_check)
        runner = CliRunner()
        result = runner.invoke(main, ["--file", sample_stock_csv, "--ticker", "AAPL"])
        assert result.exit_code != 0
