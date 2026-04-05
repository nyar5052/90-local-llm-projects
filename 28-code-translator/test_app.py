"""Tests for Code Translator."""

import pytest
from unittest.mock import patch
from click.testing import CliRunner

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app import main, detect_source_language, read_source_file, translate_code, SUPPORTED_LANGUAGES


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


class TestReadSourceFile:
    def test_read_existing(self, tmp_path):
        f = tmp_path / "test.py"
        f.write_text("def add(a, b): return a + b", encoding="utf-8")
        content = read_source_file(str(f))
        assert "add" in content

    def test_read_nonexistent(self):
        with pytest.raises(SystemExit):
            read_source_file("nonexistent_xyz.py")


class TestTranslateCode:
    @patch("app.chat")
    def test_translate_python_to_js(self, mock_chat):
        mock_chat.return_value = "```javascript\nfunction add(a, b) { return a + b; }\n```"
        result = translate_code("def add(a, b): return a + b", "python", "javascript")
        assert result is not None
        mock_chat.assert_called_once()

    @patch("app.chat")
    def test_translate_prompt_includes_languages(self, mock_chat):
        mock_chat.return_value = "translated code"
        translate_code("x = 1", "python", "go")
        call_args = str(mock_chat.call_args)
        assert "Python" in call_args
        assert "Go" in call_args


class TestSupportedLanguages:
    def test_all_languages_have_ext(self):
        for lang, info in SUPPORTED_LANGUAGES.items():
            assert "ext" in info
            assert info["ext"].startswith(".")

    def test_all_languages_have_name(self):
        for lang, info in SUPPORTED_LANGUAGES.items():
            assert "name" in info
            assert len(info["name"]) > 0


class TestMainCLI:
    @patch("app.check_ollama_running", return_value=True)
    @patch("app.chat")
    def test_translate_file(self, mock_chat, mock_ollama, tmp_path):
        mock_chat.return_value = "```javascript\nfunction greet() { console.log('hello'); }\n```"
        src = tmp_path / "script.py"
        src.write_text("def greet():\n    print('hello')\n", encoding="utf-8")

        runner = CliRunner()
        result = runner.invoke(main, ["--file", str(src), "--target", "javascript"])
        assert result.exit_code == 0

    @patch("app.check_ollama_running", return_value=True)
    @patch("app.chat")
    def test_translate_with_output(self, mock_chat, mock_ollama, tmp_path):
        mock_chat.return_value = "function greet() { console.log('hello'); }"
        src = tmp_path / "script.py"
        src.write_text("def greet(): print('hello')", encoding="utf-8")
        out = tmp_path / "script.js"

        runner = CliRunner()
        result = runner.invoke(main, ["--file", str(src), "--target", "javascript", "--output", str(out)])
        assert result.exit_code == 0
        assert out.exists()

    @patch("app.check_ollama_running", return_value=False)
    def test_ollama_not_running(self, mock_ollama, tmp_path):
        src = tmp_path / "test.py"
        src.write_text("x=1", encoding="utf-8")
        runner = CliRunner()
        result = runner.invoke(main, ["--file", str(src), "--target", "go"])
        assert result.exit_code != 0

    def test_missing_required_options(self):
        runner = CliRunner()
        result = runner.invoke(main, [])
        assert result.exit_code != 0
