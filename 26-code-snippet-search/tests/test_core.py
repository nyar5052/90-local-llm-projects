"""Tests for Code Snippet Search core module."""

import pytest
import json
import os
from unittest.mock import patch, MagicMock

from src.code_search.core import (
    scan_directory,
    build_search_context,
    search_code,
    score_relevance,
    rank_files,
    detect_language,
    load_bookmarks,
    save_bookmark,
    remove_bookmark,
    load_config,
    get_file_hash,
    save_index_cache,
    load_index_cache,
)


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

    def test_includes_language(self, tmp_path):
        (tmp_path / "app.py").write_text("x=1", encoding="utf-8")
        files = scan_directory(str(tmp_path), {".py"})
        assert files[0]["language"] == "python"

    def test_includes_hash(self, tmp_path):
        (tmp_path / "app.py").write_text("x=1", encoding="utf-8")
        files = scan_directory(str(tmp_path), {".py"})
        assert files[0]["hash"] != ""


class TestBuildSearchContext:
    def test_builds_context(self):
        files = [
            {"path": "a.py", "content": "print('hello')", "lines": 1, "language": "python"},
            {"path": "b.py", "content": "x = 1", "lines": 1, "language": "python"},
        ]
        result = build_search_context(files)
        assert "a.py" in result
        assert "b.py" in result

    def test_respects_max_chars(self):
        files = [{"path": f"f{i}.py", "content": "x" * 200, "lines": 1, "language": "python"} for i in range(100)]
        result = build_search_context(files, max_chars=500)
        assert len(result) <= 600


class TestRelevanceScoring:
    def test_keyword_in_path_scores_higher(self):
        f = {"path": "auth/login.py", "content": "x = 1"}
        score = score_relevance("login", f)
        assert score > 0

    def test_keyword_in_content(self):
        f = {"path": "app.py", "content": "def authenticate(): pass"}
        score = score_relevance("authenticate", f)
        assert score > 0

    def test_no_match_scores_zero(self):
        f = {"path": "app.py", "content": "x = 1"}
        score = score_relevance("zzzznotfound", f)
        assert score == 0.0


class TestRankFiles:
    def test_ranks_by_relevance(self):
        files = [
            {"path": "utils.py", "content": "helper function"},
            {"path": "auth.py", "content": "def login(): authenticate()"},
        ]
        ranked = rank_files(files, "login")
        assert ranked[0]["path"] == "auth.py"


class TestDetectLanguage:
    def test_python(self):
        assert detect_language("test.py") == "python"

    def test_javascript(self):
        assert detect_language("app.js") == "javascript"

    def test_unknown(self):
        assert detect_language("file.xyz") == "text"


class TestSearchCode:
    def test_search_returns_results(self, tmp_path):
        mock_chat = MagicMock(return_value="Found in main.py: authentication logic at line 10")
        (tmp_path / "main.py").write_text("def authenticate(): pass", encoding="utf-8")
        result = search_code(str(tmp_path), "authentication", mock_chat)
        assert result is not None
        mock_chat.assert_called_once()

    def test_empty_dir_returns_message(self, tmp_path):
        mock_chat = MagicMock()
        result = search_code(str(tmp_path), "test", mock_chat)
        assert "No code files" in result


class TestBookmarks:
    def test_save_and_load(self, tmp_path):
        bf = str(tmp_path / "bookmarks.json")
        save_bookmark({"query": "test"}, bf)
        bmarks = load_bookmarks(bf)
        assert len(bmarks) == 1
        assert bmarks[0]["query"] == "test"

    def test_remove_bookmark(self, tmp_path):
        bf = str(tmp_path / "bookmarks.json")
        save_bookmark({"query": "one"}, bf)
        save_bookmark({"query": "two"}, bf)
        assert remove_bookmark(0, bf)
        bmarks = load_bookmarks(bf)
        assert len(bmarks) == 1

    def test_load_nonexistent(self, tmp_path):
        bf = str(tmp_path / "none.json")
        assert load_bookmarks(bf) == []


class TestIndexCache:
    def test_save_and_load(self, tmp_path):
        cache_path = str(tmp_path / "cache.json")
        files = [{"path": "a.py", "hash": "abc", "lines": 10, "language": "python"}]
        save_index_cache(files, cache_path)
        cached = load_index_cache(cache_path)
        assert cached is not None
        assert len(cached["files"]) == 1

    def test_load_nonexistent(self, tmp_path):
        assert load_index_cache(str(tmp_path / "none.json")) is None


class TestLoadConfig:
    def test_defaults(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        config = load_config("nonexistent.yaml")
        assert config["max_files"] == 100
