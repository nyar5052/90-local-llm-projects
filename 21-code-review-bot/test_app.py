"""Tests for Code Review Bot."""

import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


from app import main, build_review_prompt, detect_language, read_file


class TestDetectLanguage:
    def test_python_file(self):
        assert detect_language("script.py") == "python"

    def test_javascript_file(self):
        assert detect_language("app.js") == "javascript"

    def test_unknown_extension(self):
        assert detect_language("file.xyz") == "text"

    def test_no_extension(self):
        assert detect_language("Makefile") == "text"

    def test_java_file(self):
        assert detect_language("Main.java") == "java"


class TestBuildReviewPrompt:
    def test_basic_prompt(self):
        code = "print('hello')\nx = 1"
        result = build_review_prompt(code, "test.py", [])
        assert "test.py" in result
        assert "1: print('hello')" in result
        assert "2: x = 1" in result

    def test_with_focus_areas(self):
        code = "x = 1"
        result = build_review_prompt(code, "test.py", ["security", "performance"])
        assert "security" in result
        assert "performance" in result

    def test_empty_focus(self):
        code = "x = 1"
        result = build_review_prompt(code, "test.py", [])
        assert "Focus especially" not in result


class TestReadFile:
    def test_nonexistent_file(self):
        with pytest.raises(SystemExit):
            read_file("nonexistent_file_xyz.py")

    def test_read_existing_file(self, tmp_path):
        test_file = tmp_path / "test.py"
        test_file.write_text("print('hello')", encoding="utf-8")
        content = read_file(str(test_file))
        assert content == "print('hello')"


class TestMainCLI:
    @patch("app.check_ollama_running", return_value=True)
    @patch("app.chat")
    def test_review_with_file(self, mock_chat, mock_ollama, tmp_path):
        mock_chat.return_value = "## Review\n- No issues found. Code looks clean."
        test_file = tmp_path / "sample.py"
        test_file.write_text("def add(a, b):\n    return a + b\n", encoding="utf-8")

        runner = CliRunner()
        result = runner.invoke(main, ["--file", str(test_file)])
        assert result.exit_code == 0
        mock_chat.assert_called_once()

    @patch("app.check_ollama_running", return_value=True)
    @patch("app.chat")
    def test_review_with_focus(self, mock_chat, mock_ollama, tmp_path):
        mock_chat.return_value = "## Security Review\n- No vulnerabilities found."
        test_file = tmp_path / "sample.py"
        test_file.write_text("x = 1\n", encoding="utf-8")

        runner = CliRunner()
        result = runner.invoke(main, ["--file", str(test_file), "--focus", "security"])
        assert result.exit_code == 0
        call_args = mock_chat.call_args
        assert "security" in str(call_args)

    @patch("app.check_ollama_running", return_value=False)
    def test_ollama_not_running(self, mock_ollama, tmp_path):
        test_file = tmp_path / "sample.py"
        test_file.write_text("x = 1\n", encoding="utf-8")

        runner = CliRunner()
        result = runner.invoke(main, ["--file", str(test_file)])
        assert result.exit_code != 0

    def test_missing_file_option(self):
        runner = CliRunner()
        result = runner.invoke(main, [])
        assert result.exit_code != 0
