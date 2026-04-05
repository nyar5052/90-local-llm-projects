"""Tests for Code Translator core module."""

import pytest
import os
from unittest.mock import MagicMock

from src.code_translator.core import (
    detect_source_language,
    get_language_name,
    get_language_ext,
    read_source_file,
    translate_code,
    validate_syntax,
    compare_codes,
    batch_translate_files,
    load_config,
    SUPPORTED_LANGUAGES,
)


class TestDetectSourceLanguage:
    def test_python(self):
        assert detect_source_language("script.py") == "python"

    def test_javascript(self):
        assert detect_source_language("app.js") == "javascript"

    def test_java(self):
        assert detect_source_language("Main.java") == "java"

    def test_go(self):
        assert detect_source_language("main.go") == "go"

    def test_rust(self):
        assert detect_source_language("lib.rs") == "rust"

    def test_unknown(self):
        assert detect_source_language("file.xyz") == ""

    def test_typescript(self):
        assert detect_source_language("index.ts") == "typescript"


class TestLanguageHelpers:
    def test_get_language_name(self):
        assert get_language_name("python") == "Python"
        assert get_language_name("unknown") == "unknown"

    def test_get_language_ext(self):
        assert get_language_ext("python") == ".py"
        assert get_language_ext("unknown") == ".txt"


class TestReadSourceFile:
    def test_read_existing(self, tmp_path):
        f = tmp_path / "test.py"
        f.write_text("def add(a, b): return a + b", encoding="utf-8")
        content = read_source_file(str(f))
        assert "add" in content

    def test_read_nonexistent(self):
        with pytest.raises(FileNotFoundError):
            read_source_file("nonexistent_xyz.py")


class TestTranslateCode:
    def test_translate_python_to_js(self):
        mock_chat = MagicMock(return_value="```javascript\nfunction add(a, b) { return a + b; }\n```")
        result = translate_code("def add(a, b): return a + b", "python", "javascript", mock_chat)
        assert result is not None
        mock_chat.assert_called_once()

    def test_translate_prompt_includes_languages(self):
        mock_chat = MagicMock(return_value="translated code")
        translate_code("x = 1", "python", "go", mock_chat)
        call_args = str(mock_chat.call_args)
        assert "Python" in call_args
        assert "Go" in call_args


class TestValidateSyntax:
    def test_valid_python(self):
        result = validate_syntax("x = 1 + 2", "python")
        assert result["valid"] is True

    def test_invalid_python(self):
        result = validate_syntax("def broken(:", "python")
        assert result["valid"] is False

    def test_unbalanced_js(self):
        result = validate_syntax("function() { if (true) {", "javascript")
        assert result["valid"] is False

    def test_balanced_js(self):
        result = validate_syntax("function() { return 1; }", "javascript")
        assert result["valid"] is True


class TestCompareCodes:
    def test_basic_comparison(self):
        result = compare_codes("line1\nline2", "line1\nline2\nline3")
        assert result["source_lines"] == 2
        assert result["target_lines"] == 3
        assert result["line_ratio"] == 1.5


class TestBatchTranslate:
    def test_batch_success(self, tmp_path):
        src = tmp_path / "test.py"
        src.write_text("x = 1", encoding="utf-8")
        out_dir = str(tmp_path / "output")

        mock_chat = MagicMock(return_value="var x = 1;")
        results = batch_translate_files([str(src)], "javascript", mock_chat, out_dir)
        assert len(results) == 1
        assert results[0]["status"] == "success"

    def test_batch_error(self, tmp_path):
        mock_chat = MagicMock()
        results = batch_translate_files(["nonexistent.py"], "javascript", mock_chat, str(tmp_path / "out"))
        assert results[0]["status"] == "error"


class TestSupportedLanguages:
    def test_all_languages_have_ext(self):
        for lang, info in SUPPORTED_LANGUAGES.items():
            assert "ext" in info
            assert info["ext"].startswith(".")

    def test_all_languages_have_name(self):
        for lang, info in SUPPORTED_LANGUAGES.items():
            assert "name" in info
            assert len(info["name"]) > 0


class TestLoadConfig:
    def test_defaults(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        config = load_config("nonexistent.yaml")
        assert config["max_code_chars"] == 5000
