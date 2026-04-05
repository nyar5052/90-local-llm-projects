"""Tests for CSV Data Analyzer CLI."""

import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner

from src.csv_analyzer.cli import main


class TestCLI:
    @patch("src.csv_analyzer.core.get_llm_client")
    def test_cli_with_valid_file_and_query(self, mock_get_client, sample_csv):
        mock_chat = MagicMock(return_value="The data shows interesting trends.")
        mock_check = MagicMock(return_value=True)
        mock_get_client.return_value = (mock_chat, mock_check)
        runner = CliRunner()
        result = runner.invoke(main, ["--file", sample_csv, "--query", "Summarize"])
        assert result.exit_code == 0

    def test_cli_without_query(self, sample_csv):
        runner = CliRunner()
        result = runner.invoke(main, ["--file", sample_csv, "--no-preview"])
        assert result.exit_code == 0

    def test_cli_nonexistent_file(self):
        runner = CliRunner()
        result = runner.invoke(main, ["--file", "nonexistent.csv", "--no-preview"])
        assert result.exit_code != 0

    def test_cli_export(self, sample_csv, tmp_path):
        output = str(tmp_path / "out.json")
        runner = CliRunner()
        result = runner.invoke(main, [
            "--file", sample_csv, "--no-preview", "--no-types",
            "--no-correlations", "--no-charts", "--export", output,
        ])
        assert result.exit_code == 0
