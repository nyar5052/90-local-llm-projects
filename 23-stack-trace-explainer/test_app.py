"""Tests for Stack Trace Explainer."""

import pytest
from unittest.mock import patch
from click.testing import CliRunner

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app import main, detect_language, explain_trace, read_trace_from_file

PYTHON_TRACE = """Traceback (most recent call last):
  File "app.py", line 42, in main
    result = process(data)
  File "app.py", line 28, in process
    return data["key"]
KeyError: 'key'
"""

JAVA_TRACE = """Exception in thread "main" java.lang.NullPointerException
    at com.example.App.process(App.java:42)
    at com.example.App.main(App.java:15)
"""

JS_TRACE = """TypeError: Cannot read property 'map' of undefined
    at Object.<anonymous> (/app/src/index.js:15:20)
    at Module._compile (node:internal/modules/cjs/loader:1105:14)
"""


class TestDetectLanguage:
    def test_detect_python(self):
        assert detect_language(PYTHON_TRACE) == "python"

    def test_detect_java(self):
        assert detect_language(JAVA_TRACE) == "java"

    def test_detect_javascript(self):
        assert detect_language(JS_TRACE) == "javascript"

    def test_detect_unknown(self):
        assert detect_language("some random text") == "unknown"


class TestReadTraceFromFile:
    def test_read_existing_file(self, tmp_path):
        trace_file = tmp_path / "error.txt"
        trace_file.write_text(PYTHON_TRACE, encoding="utf-8")
        content = read_trace_from_file(str(trace_file))
        assert "KeyError" in content

    def test_read_nonexistent_file(self):
        with pytest.raises(SystemExit):
            read_trace_from_file("nonexistent_error.txt")


class TestExplainTrace:
    @patch("app.chat")
    def test_explain_python_trace(self, mock_chat):
        mock_chat.return_value = "This is a KeyError. The key 'key' does not exist in the dictionary."
        result = explain_trace(PYTHON_TRACE, "python")
        assert result is not None
        mock_chat.assert_called_once()

    @patch("app.chat")
    def test_explain_with_language_hint(self, mock_chat):
        mock_chat.return_value = "NullPointerException explanation"
        explain_trace(JAVA_TRACE, "java")
        call_args = str(mock_chat.call_args)
        assert "java" in call_args


class TestMainCLI:
    @patch("app.check_ollama_running", return_value=True)
    @patch("app.chat")
    def test_with_trace_file(self, mock_chat, mock_ollama, tmp_path):
        mock_chat.return_value = "## Error Explanation\nKeyError means the key was not found."
        trace_file = tmp_path / "error.txt"
        trace_file.write_text(PYTHON_TRACE, encoding="utf-8")

        runner = CliRunner()
        result = runner.invoke(main, ["--trace", str(trace_file)])
        assert result.exit_code == 0

    @patch("app.check_ollama_running", return_value=True)
    @patch("app.chat")
    def test_with_text_argument(self, mock_chat, mock_ollama):
        mock_chat.return_value = "Error explanation here."
        runner = CliRunner()
        result = runner.invoke(main, ["--text", PYTHON_TRACE])
        assert result.exit_code == 0

    @patch("app.check_ollama_running", return_value=False)
    def test_ollama_not_running(self, mock_ollama):
        runner = CliRunner()
        result = runner.invoke(main, ["--text", "error"])
        assert result.exit_code != 0

    def test_no_input(self):
        runner = CliRunner()
        with patch("app.check_ollama_running", return_value=True):
            result = runner.invoke(main, [])
            assert result.exit_code != 0
