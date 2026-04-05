"""Tests for the Report Generator CLI."""

import csv
import os
import pytest
from unittest.mock import patch
from click.testing import CliRunner

from src.report_generator.cli import main


@pytest.fixture
def sample_csv(tmp_path):
    filepath = tmp_path / "sales.csv"
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Region", "Product", "Revenue", "Units"])
        writer.writerow(["North", "Widget A", "15000", "120"])
        writer.writerow(["South", "Widget B", "22000", "200"])
    return str(filepath)


class TestCLI:
    """Tests for the Click CLI entrypoint."""

    def test_cli_missing_data_option(self):
        runner = CliRunner()
        result = runner.invoke(main, ["--topic", "Test"])
        assert result.exit_code != 0

    def test_cli_missing_topic_option(self):
        runner = CliRunner()
        result = runner.invoke(main, ["--data", "some.csv"])
        assert result.exit_code != 0

    @patch("src.report_generator.cli.check_ollama_running", return_value=True)
    @patch("src.report_generator.core.chat")
    def test_cli_end_to_end(self, mock_chat, mock_ollama, sample_csv, tmp_path):
        mock_chat.return_value = "# Generated Report\n\nAnalysis here."
        outpath = str(tmp_path / "result.md")
        runner = CliRunner()
        result = runner.invoke(
            main, ["--topic", "Q4 Sales", "--data", sample_csv, "--output", outpath]
        )
        assert result.exit_code == 0
        assert os.path.exists(outpath)

    def test_cli_nonexistent_data_file(self):
        runner = CliRunner()
        result = runner.invoke(main, ["--topic", "Test", "--data", "no_such_file.csv"])
        assert result.exit_code != 0

    @patch("src.report_generator.cli.check_ollama_running", return_value=True)
    @patch("src.report_generator.core.chat")
    def test_cli_template_option(self, mock_chat, mock_ollama, sample_csv, tmp_path):
        mock_chat.return_value = "# Technical Report"
        outpath = str(tmp_path / "tech.md")
        runner = CliRunner()
        result = runner.invoke(
            main, ["--topic", "Tech", "--data", sample_csv, "--output", outpath, "--template", "technical"]
        )
        assert result.exit_code == 0
