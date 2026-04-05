"""Tests for Code Snippet Search CLI."""

import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner

from src.code_search.cli import cli


class TestCLI:
    @patch("src.code_search.cli.check_ollama_running", return_value=True)
    @patch("src.code_search.cli.chat")
    def test_basic_search(self, mock_chat, mock_ollama, tmp_path):
        mock_chat.return_value = "Found relevant code in utils.py"
        (tmp_path / "utils.py").write_text("def helper(): pass", encoding="utf-8")

        runner = CliRunner()
        result = runner.invoke(cli, ["search", "--dir", str(tmp_path), "--query", "helper function"])
        assert result.exit_code == 0

    @patch("src.code_search.cli.check_ollama_running", return_value=False)
    def test_ollama_not_running(self, mock_ollama, tmp_path):
        runner = CliRunner()
        result = runner.invoke(cli, ["search", "--dir", str(tmp_path), "--query", "test"])
        assert result.exit_code != 0

    def test_bookmarks_empty(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["bookmarks"])
        assert result.exit_code == 0

    def test_help(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "Code Snippet Search" in result.output
