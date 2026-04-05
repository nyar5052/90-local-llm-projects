"""Tests for API Doc Generator."""

import pytest
from unittest.mock import patch
from click.testing import CliRunner

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app import main, extract_functions, find_python_files, format_extracted_info


SAMPLE_CODE = '''"""Sample module."""

def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b

class Calculator:
    """A simple calculator."""
    
    def multiply(self, x: float, y: float) -> float:
        """Multiply two numbers."""
        return x * y
    
    def divide(self, x: float, y: float) -> float:
        """Divide x by y."""
        if y == 0:
            raise ValueError("Cannot divide by zero")
        return x / y

async def fetch_data(url: str) -> dict:
    """Fetch data from a URL."""
    pass
'''


class TestExtractFunctions:
    def test_extracts_functions(self, tmp_path):
        f = tmp_path / "sample.py"
        f.write_text(SAMPLE_CODE, encoding="utf-8")
        items = extract_functions(str(f))
        names = [i["name"] for i in items]
        assert "add" in names
        assert "Calculator" in names
        assert "fetch_data" in names

    def test_function_args(self, tmp_path):
        f = tmp_path / "sample.py"
        f.write_text(SAMPLE_CODE, encoding="utf-8")
        items = extract_functions(str(f))
        add_func = [i for i in items if i["name"] == "add"][0]
        assert len(add_func["args"]) == 2
        assert add_func["args"][0]["name"] == "a"
        assert add_func["returns"] == "int"

    def test_class_methods(self, tmp_path):
        f = tmp_path / "sample.py"
        f.write_text(SAMPLE_CODE, encoding="utf-8")
        items = extract_functions(str(f))
        calc = [i for i in items if i["name"] == "Calculator"][0]
        method_names = [m["name"] for m in calc["methods"]]
        assert "multiply" in method_names
        assert "divide" in method_names

    def test_async_function(self, tmp_path):
        f = tmp_path / "sample.py"
        f.write_text(SAMPLE_CODE, encoding="utf-8")
        items = extract_functions(str(f))
        fetch = [i for i in items if i["name"] == "fetch_data"][0]
        assert fetch["is_async"] is True

    def test_syntax_error(self, tmp_path):
        f = tmp_path / "bad.py"
        f.write_text("def broken(:\n  pass", encoding="utf-8")
        items = extract_functions(str(f))
        assert items == []


class TestFindPythonFiles:
    def test_find_single_file(self, tmp_path):
        f = tmp_path / "test.py"
        f.write_text("x = 1", encoding="utf-8")
        files = find_python_files(str(f))
        assert len(files) == 1

    def test_find_in_directory(self, tmp_path):
        (tmp_path / "a.py").write_text("x=1", encoding="utf-8")
        (tmp_path / "b.py").write_text("y=2", encoding="utf-8")
        (tmp_path / "c.txt").write_text("z=3", encoding="utf-8")
        files = find_python_files(str(tmp_path))
        assert len(files) == 2

    def test_nonexistent_path(self):
        with pytest.raises(SystemExit):
            find_python_files("nonexistent_path_xyz")


class TestFormatExtractedInfo:
    def test_formats_function(self):
        items = [{"type": "function", "name": "add", "lineno": 1,
                  "args": [{"name": "a", "annotation": "int"}],
                  "returns": "int", "docstring": "Add numbers.", "is_async": False}]
        result = format_extracted_info("test.py", items)
        assert "add" in result
        assert "int" in result


class TestMainCLI:
    @patch("app.check_ollama_running", return_value=True)
    @patch("app.chat")
    def test_generate_docs(self, mock_chat, mock_ollama, tmp_path):
        mock_chat.return_value = "# API Docs\n## add(a, b)\nAdds two numbers."
        f = tmp_path / "sample.py"
        f.write_text(SAMPLE_CODE, encoding="utf-8")

        runner = CliRunner()
        result = runner.invoke(main, ["--source", str(f)])
        assert result.exit_code == 0

    @patch("app.check_ollama_running", return_value=True)
    @patch("app.chat")
    def test_output_to_file(self, mock_chat, mock_ollama, tmp_path):
        mock_chat.return_value = "# API Documentation"
        f = tmp_path / "sample.py"
        f.write_text(SAMPLE_CODE, encoding="utf-8")
        out = tmp_path / "docs.md"

        runner = CliRunner()
        result = runner.invoke(main, ["--source", str(f), "--output", str(out)])
        assert result.exit_code == 0
        assert out.exists()

    @patch("app.check_ollama_running", return_value=False)
    def test_ollama_not_running(self, mock_ollama, tmp_path):
        f = tmp_path / "sample.py"
        f.write_text("x=1", encoding="utf-8")
        runner = CliRunner()
        result = runner.invoke(main, ["--source", str(f)])
        assert result.exit_code != 0
