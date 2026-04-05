"""Tests for Code Snippet Search."""

import pytest
from unittest.mock import patch
from click.testing import CliRunner

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app import main, scan_directory, build_search_context, search_code


class TestScanDirectory:
    def test_scans_python_files(self, tmp_path):
        (tmp_path / "main.py").write_text("print('hello')", encoding="utf-8")
        (tmp_path / "utils.py").write_text("x = 1", encoding="utf-8")
        (tmp_path / "data.txt").write_text("text", encoding="utf-8")
        files = scan_directory(str(tmp_path), {".py"})
        assert len(files) == 2

    def test_ignores_git_dir(self, tmp_path):
        git_dir = tmp_path / ".git"
        git_dir.mkdir()
        (git_dir / "config").write_text("git config", encoding="utf-8")
        (tmp_path / "app.py").write_text("x=1", encoding="utf-8")
        files = scan_directory(str(tmp_path), {".py"})
        assert len(files) == 1
        assert all(".git" not in f["path"] for f in files)

    def test_max_files_limit(self, tmp_path):
        for i in range(10):
            (tmp_path / f"file{i}.py").write_text(f"x = {i}", encoding="utf-8")
        files = scan_directory(str(tmp_path), {".py"}, max_files=3)
        assert len(files) == 3

    def test_empty_directory(self, tmp_path):
        files = scan_directory(str(tmp_path))
        assert len(files) == 0

    def test_file_content_read(self, tmp_path):
        (tmp_path / "app.py").write_text("def main(): pass", encoding="utf-8")
        files = scan_directory(str(tmp_path), {".py"})
        assert files[0]["content"] == "def main(): pass"


class TestBuildSearchContext:
    def test_builds_context(self):
        files = [
            {"path": "a.py", "content": "print('hello')", "lines": 1},
            {"path": "b.py", "content": "x = 1", "lines": 1},
        ]
        result = build_search_context(files)
        assert "a.py" in result
        assert "b.py" in result

    def test_respects_max_chars(self):
        files = [{"path": f"f{i}.py", "content": "x" * 200, "lines": 1} for i in range(100)]
        result = build_search_context(files, max_chars=500)
        assert len(result) <= 600  # some overhead for formatting


class TestSearchCode:
    @patch("app.chat")
    def test_search_returns_results(self, mock_chat, tmp_path):
        mock_chat.return_value = "Found in main.py: authentication logic at line 10"
        (tmp_path / "main.py").write_text("def authenticate(): pass", encoding="utf-8")
        result = search_code(str(tmp_path), "authentication")
        assert result is not None
        mock_chat.assert_called_once()


class TestMainCLI:
    @patch("app.check_ollama_running", return_value=True)
    @patch("app.chat")
    def test_basic_search(self, mock_chat, mock_ollama, tmp_path):
        mock_chat.return_value = "Found relevant code in utils.py"
        (tmp_path / "utils.py").write_text("def helper(): pass", encoding="utf-8")

        runner = CliRunner()
        result = runner.invoke(main, ["--dir", str(tmp_path), "--query", "helper function"])
        assert result.exit_code == 0

    @patch("app.check_ollama_running", return_value=False)
    def test_ollama_not_running(self, mock_ollama, tmp_path):
        runner = CliRunner()
        result = runner.invoke(main, ["--dir", str(tmp_path), "--query", "test"])
        assert result.exit_code != 0

    def test_invalid_directory(self):
        runner = CliRunner()
        with patch("app.check_ollama_running", return_value=True):
            result = runner.invoke(main, ["--dir", "nonexistent_xyz", "--query", "test"])
            assert result.exit_code != 0
