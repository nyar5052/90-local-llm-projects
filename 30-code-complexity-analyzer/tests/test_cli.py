"""Tests for Code Complexity Analyzer CLI."""

import pytest
from unittest.mock import patch
from click.testing import CliRunner

from src.complexity_analyzer.cli import cli


SIMPLE_CODE = '''def add(a, b):
    """Add two numbers."""
    return a + b
'''

FULL_MODULE = '''"""Sample module."""

def simple():
    return 1

def medium(x):
    if x > 0:
        return x
    elif x < 0:
        return -x
    else:
        return 0
'''


class TestCLI:
    def test_summary_no_ai(self, tmp_path):
        f = tmp_path / "simple.py"
        f.write_text(SIMPLE_CODE, encoding="utf-8")
        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "--file", str(f), "--no-ai"])
        assert result.exit_code == 0

    @patch("src.complexity_analyzer.cli.check_ollama_running", return_value=True)
    @patch("src.complexity_analyzer.cli.chat")
    def test_detailed_report(self, mock_chat, mock_ollama, tmp_path):
        mock_chat.return_value = "## Suggestions\nCode looks clean."
        f = tmp_path / "module.py"
        f.write_text(FULL_MODULE, encoding="utf-8")
        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "--file", str(f), "--report", "detailed"])
        assert result.exit_code == 0

    @patch("src.complexity_analyzer.cli.check_ollama_running", return_value=False)
    def test_ollama_not_running(self, mock_ollama, tmp_path):
        f = tmp_path / "test.py"
        f.write_text("x=1", encoding="utf-8")
        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "--file", str(f)])
        assert result.exit_code != 0

    def test_help(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "Code Complexity Analyzer" in result.output

    def test_trends_empty(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["trends"])
        assert result.exit_code == 0
