"""Tests for the Research Paper QA CLI."""

import pytest
from unittest.mock import patch
from click.testing import CliRunner

from src.research_qa.cli import main


class TestCLI:
    def test_cli_missing_paper_option(self):
        runner = CliRunner()
        result = runner.invoke(main, [])
        assert result.exit_code != 0

    def test_cli_nonexistent_paper_file(self):
        runner = CliRunner()
        result = runner.invoke(main, ["--paper", "does_not_exist.txt"])
        assert result.exit_code != 0

    @patch("src.research_qa.cli.check_ollama_running", return_value=False)
    def test_cli_ollama_not_running(self, mock_check, tmp_path):
        paper = tmp_path / "paper.txt"
        paper.write_text("Some paper content.")
        runner = CliRunner()
        result = runner.invoke(main, ["--paper", str(paper)])
        assert result.exit_code != 0
