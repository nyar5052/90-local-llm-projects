"""Tests for Unit Test Generator core module."""

import pytest
import os
from unittest.mock import MagicMock

from src.test_gen.core import (
    extract_code_info,
    generate_tests,
    analyze_coverage,
    organize_test_structure,
    load_config,
    _detect_edge_cases,
)
import ast


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

    def test_detects_edge_cases(self, tmp_path):
        f = tmp_path / "math_utils.py"
        f.write_text(SAMPLE_CODE, encoding="utf-8")
        info = extract_code_info(str(f))
        divide_func = [fn for fn in info["functions"] if fn["name"] == "divide"][0]
        assert len(divide_func["edge_cases"]) > 0


class TestAnalyzeCoverage:
    def test_coverage_analysis(self, tmp_path):
        f = tmp_path / "math_utils.py"
        f.write_text(SAMPLE_CODE, encoding="utf-8")
        info = extract_code_info(str(f))
        coverage = analyze_coverage(info)
        assert coverage["total_functions"] == 2
        assert coverage["total_methods"] == 2
        assert coverage["total_testable"] == 4
        assert coverage["estimated_tests"] == 12


class TestOrganizeTestStructure:
    def test_structure(self, tmp_path):
        f = tmp_path / "math_utils.py"
        f.write_text(SAMPLE_CODE, encoding="utf-8")
        info = extract_code_info(str(f))
        structure = organize_test_structure(info)
        assert len(structure["test_files"]) >= 1


class TestGenerateTests:
    def test_generates_tests(self, tmp_path):
        mock_chat = MagicMock(return_value="```python\nimport pytest\ndef test_add():\n    assert True\n```")
        f = tmp_path / "math_utils.py"
        f.write_text(SAMPLE_CODE, encoding="utf-8")
        result = generate_tests(str(f), mock_chat)
        assert result is not None
        mock_chat.assert_called_once()

    def test_uses_specified_framework(self, tmp_path):
        mock_chat = MagicMock(return_value="```python\nimport unittest\n```")
        f = tmp_path / "math_utils.py"
        f.write_text(SAMPLE_CODE, encoding="utf-8")
        generate_tests(str(f), mock_chat, framework="unittest")
        call_args = str(mock_chat.call_args)
        assert "unittest" in call_args


class TestLoadConfig:
    def test_defaults(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        config = load_config("nonexistent.yaml")
        assert config["default_framework"] == "pytest"
