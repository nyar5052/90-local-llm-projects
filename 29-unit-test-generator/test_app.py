"""Tests for Unit Test Generator."""

import pytest
from unittest.mock import patch
from click.testing import CliRunner

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app import main, extract_code_info, generate_tests


SAMPLE_CODE = '''"""Math utilities module."""

def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b

def divide(a: float, b: float) -> float:
    """Divide a by b."""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b

class StringUtils:
    """String utility methods."""
    
    def reverse(self, text: str) -> str:
        """Reverse a string."""
        return text[::-1]
    
    def is_palindrome(self, text: str) -> bool:
        """Check if text is a palindrome."""
        cleaned = text.lower().replace(" ", "")
        return cleaned == cleaned[::-1]
'''


class TestExtractCodeInfo:
    def test_extracts_functions(self, tmp_path):
        f = tmp_path / "math_utils.py"
        f.write_text(SAMPLE_CODE, encoding="utf-8")
        info = extract_code_info(str(f))
        func_names = [fn["name"] for fn in info["functions"]]
        assert "add" in func_names
        assert "divide" in func_names

    def test_extracts_classes(self, tmp_path):
        f = tmp_path / "math_utils.py"
        f.write_text(SAMPLE_CODE, encoding="utf-8")
        info = extract_code_info(str(f))
        class_names = [c["name"] for c in info["classes"]]
        assert "StringUtils" in class_names

    def test_extracts_method_names(self, tmp_path):
        f = tmp_path / "math_utils.py"
        f.write_text(SAMPLE_CODE, encoding="utf-8")
        info = extract_code_info(str(f))
        string_utils = [c for c in info["classes"] if c["name"] == "StringUtils"][0]
        method_names = [m["name"] for m in string_utils["methods"]]
        assert "reverse" in method_names
        assert "is_palindrome" in method_names

    def test_extracts_args(self, tmp_path):
        f = tmp_path / "math_utils.py"
        f.write_text(SAMPLE_CODE, encoding="utf-8")
        info = extract_code_info(str(f))
        add_func = [fn for fn in info["functions"] if fn["name"] == "add"][0]
        assert "a" in add_func["args"]
        assert "b" in add_func["args"]

    def test_handles_syntax_error(self, tmp_path):
        f = tmp_path / "bad.py"
        f.write_text("def broken(:\n  pass", encoding="utf-8")
        info = extract_code_info(str(f))
        assert info["functions"] == []
        assert info["source"] is not None

    def test_extracts_docstrings(self, tmp_path):
        f = tmp_path / "math_utils.py"
        f.write_text(SAMPLE_CODE, encoding="utf-8")
        info = extract_code_info(str(f))
        add_func = [fn for fn in info["functions"] if fn["name"] == "add"][0]
        assert "Add two numbers" in add_func["docstring"]


class TestGenerateTests:
    @patch("app.chat")
    def test_generates_tests(self, mock_chat, tmp_path):
        mock_chat.return_value = "```python\nimport pytest\nfrom math_utils import add\n\ndef test_add():\n    assert add(1, 2) == 3\n```"
        f = tmp_path / "math_utils.py"
        f.write_text(SAMPLE_CODE, encoding="utf-8")
        result = generate_tests(str(f))
        assert result is not None
        mock_chat.assert_called_once()

    @patch("app.chat")
    def test_uses_specified_framework(self, mock_chat, tmp_path):
        mock_chat.return_value = "```python\nimport unittest\n```"
        f = tmp_path / "math_utils.py"
        f.write_text(SAMPLE_CODE, encoding="utf-8")
        generate_tests(str(f), framework="unittest")
        call_args = str(mock_chat.call_args)
        assert "unittest" in call_args


class TestMainCLI:
    @patch("app.check_ollama_running", return_value=True)
    @patch("app.chat")
    def test_generate_tests(self, mock_chat, mock_ollama, tmp_path):
        mock_chat.return_value = "```python\ndef test_add(): assert True\n```"
        f = tmp_path / "utils.py"
        f.write_text(SAMPLE_CODE, encoding="utf-8")

        runner = CliRunner()
        result = runner.invoke(main, ["--file", str(f)])
        assert result.exit_code == 0

    @patch("app.check_ollama_running", return_value=True)
    @patch("app.chat")
    def test_output_to_file(self, mock_chat, mock_ollama, tmp_path):
        mock_chat.return_value = "def test_add(): assert True"
        f = tmp_path / "utils.py"
        f.write_text(SAMPLE_CODE, encoding="utf-8")
        out = tmp_path / "test_utils.py"

        runner = CliRunner()
        result = runner.invoke(main, ["--file", str(f), "--output", str(out)])
        assert result.exit_code == 0
        assert out.exists()

    @patch("app.check_ollama_running", return_value=False)
    def test_ollama_not_running(self, mock_ollama, tmp_path):
        f = tmp_path / "utils.py"
        f.write_text("x=1", encoding="utf-8")
        runner = CliRunner()
        result = runner.invoke(main, ["--file", str(f)])
        assert result.exit_code != 0
