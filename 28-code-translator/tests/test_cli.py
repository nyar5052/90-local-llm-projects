"""Tests for Code Translator CLI."""

import pytest
from unittest.mock import patch
from click.testing import CliRunner

from src.code_translator.cli import cli


class TestCLI:
    @patch("src.code_translator.cli.check_ollama_running", return_value=True)
    @patch("src.code_translator.cli.chat")
    def test_translate_file(self, mock_chat, mock_ollama, tmp_path):
        mock_chat.return_value = "```javascript\nfunction greet() { console.log('hello'); }\n```"
        src = tmp_path / "script.py"
        src.write_text("def greet():\n    print('hello')\n", encoding="utf-8")

        runner = CliRunner()
        result = runner.invoke(cli, ["translate", "--file", str(src), "--target", "javascript"])
        assert result.exit_code == 0

    @patch("src.code_translator.cli.check_ollama_running", return_value=True)
    @patch("src.code_translator.cli.chat")
    def test_translate_with_output(self, mock_chat, mock_ollama, tmp_path):
        mock_chat.return_value = "function greet() { console.log('hello'); }"
        src = tmp_path / "script.py"
        src.write_text("def greet(): print('hello')", encoding="utf-8")
        out = tmp_path / "script.js"

        runner = CliRunner()
        result = runner.invoke(cli, ["translate", "--file", str(src), "--target", "javascript", "--output", str(out)])
        assert result.exit_code == 0
        assert out.exists()

    @patch("src.code_translator.cli.check_ollama_running", return_value=False)
    def test_ollama_not_running(self, mock_ollama, tmp_path):
        src = tmp_path / "test.py"
        src.write_text("x=1", encoding="utf-8")
        runner = CliRunner()
        result = runner.invoke(cli, ["translate", "--file", str(src), "--target", "go"])
        assert result.exit_code != 0

    def test_help(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "Code Translator" in result.output
