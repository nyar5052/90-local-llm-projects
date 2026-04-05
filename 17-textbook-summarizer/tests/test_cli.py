"""Tests for the Textbook Summarizer CLI."""

import pytest
from unittest.mock import patch
from click.testing import CliRunner

from src.textbook_summarizer.cli import main


MOCK_SUMMARY = "## Summary\nThis chapter covers thermodynamics."


@pytest.fixture
def sample_file(tmp_path):
    filepath = tmp_path / "chapter.txt"
    filepath.write_text(
        "Chapter 3: Thermodynamics\n\nThermodynamics content here.",
        encoding="utf-8",
    )
    return str(filepath)


class TestCLI:
    @patch("src.textbook_summarizer.cli.check_ollama_running", return_value=True)
    @patch("src.textbook_summarizer.core.generate", return_value=MOCK_SUMMARY)
    def test_cli_with_valid_file(self, mock_generate, mock_ollama, sample_file):
        runner = CliRunner()
        result = runner.invoke(main, ["--file", sample_file, "--style", "concise"])
        assert result.exit_code == 0

    def test_cli_missing_file_option(self):
        runner = CliRunner()
        result = runner.invoke(main, [])
        assert result.exit_code != 0

    def test_cli_nonexistent_file(self):
        runner = CliRunner()
        result = runner.invoke(main, ["--file", "no_such_file.txt"])
        assert result.exit_code != 0

    def test_cli_invalid_style(self):
        runner = CliRunner()
        result = runner.invoke(main, ["--file", "dummy.txt", "--style", "wrong"])
        assert result.exit_code != 0

    @patch("src.textbook_summarizer.cli.check_ollama_running", return_value=False)
    def test_cli_ollama_not_running(self, mock_ollama, sample_file):
        runner = CliRunner()
        result = runner.invoke(main, ["--file", sample_file])
        assert result.exit_code != 0
