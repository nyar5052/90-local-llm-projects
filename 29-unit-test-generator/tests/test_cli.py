"""Tests for Unit Test Generator CLI."""

import pytest
from unittest.mock import patch
from click.testing import CliRunner

from src.test_gen.cli import cli


SAMPLE_CODE = '''def add(a, b):
    return a + b

def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b
'''


class TestCLI:
    @patch("src.test_gen.cli.check_ollama_running", return_value=True)
    @patch("src.test_gen.cli.chat")
    def test_generate_tests(self, mock_chat, mock_ollama, tmp_path):
        mock_chat.return_value = "```python\ndef test_add(): assert True\n```"
        f = tmp_path / "utils.py"
        f.write_text(SAMPLE_CODE, encoding="utf-8")

        runner = CliRunner()
        result = runner.invoke(cli, ["generate", "--file", str(f)])
        assert result.exit_code == 0

    @patch("src.test_gen.cli.check_ollama_running", return_value=True)
    @patch("src.test_gen.cli.chat")
    def test_output_to_file(self, mock_chat, mock_ollama, tmp_path):
        mock_chat.return_value = "def test_add(): assert True"
        f = tmp_path / "utils.py"
        f.write_text(SAMPLE_CODE, encoding="utf-8")
        out = tmp_path / "test_utils.py"

        runner = CliRunner()
        result = runner.invoke(cli, ["generate", "--file", str(f), "--output", str(out)])
        assert result.exit_code == 0
        assert out.exists()

    @patch("src.test_gen.cli.check_ollama_running", return_value=False)
    def test_ollama_not_running(self, mock_ollama, tmp_path):
        f = tmp_path / "utils.py"
        f.write_text("x=1", encoding="utf-8")
        runner = CliRunner()
        result = runner.invoke(cli, ["generate", "--file", str(f)])
        assert result.exit_code != 0

    def test_analyze(self, tmp_path):
        f = tmp_path / "utils.py"
        f.write_text(SAMPLE_CODE, encoding="utf-8")
        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "--file", str(f)])
        assert result.exit_code == 0

    def test_help(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "Unit Test Generator" in result.output
