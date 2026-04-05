"""Tests for Regex Generator."""

import pytest
from unittest.mock import patch
from click.testing import CliRunner

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app import cli, generate_regex, explain_regex, run_regex_test


class TestRunRegexTest:
    def test_matching_pattern(self):
        results = run_regex_test(r"\d+", ["abc123", "hello", "42"])
        assert results[0]["matches"] is True
        assert results[1]["matches"] is False
        assert results[2]["matches"] is True

    def test_email_pattern(self):
        pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
        results = run_regex_test(pattern, ["user@example.com", "invalid", "a@b.co"])
        assert results[0]["matches"] is True
        assert results[1]["matches"] is False
        assert results[2]["matches"] is True

    def test_invalid_pattern(self):
        results = run_regex_test(r"[invalid", ["test"])
        assert len(results) == 0

    def test_empty_strings(self):
        results = run_regex_test(r".*", ["", "hello"])
        assert results[0]["matches"] is True
        assert results[1]["matches"] is True

    def test_match_text_extraction(self):
        results = run_regex_test(r"\d+", ["abc123def"])
        assert results[0]["match_text"] == "123"


class TestGenerateRegex:
    @patch("app.chat")
    def test_generates_regex(self, mock_chat):
        mock_chat.return_value = "Pattern: `[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}`"
        result = generate_regex("email addresses")
        assert result is not None
        mock_chat.assert_called_once()

    @patch("app.chat")
    def test_prompt_includes_description(self, mock_chat):
        mock_chat.return_value = "Pattern: `\\d{3}-\\d{4}`"
        generate_regex("phone numbers")
        call_args = str(mock_chat.call_args)
        assert "phone numbers" in call_args


class TestExplainRegex:
    @patch("app.chat")
    def test_explains_pattern(self, mock_chat):
        mock_chat.return_value = "This pattern matches one or more digits."
        result = explain_regex(r"\d+")
        assert result is not None
        mock_chat.assert_called_once()

    @patch("app.chat")
    def test_explains_complex_pattern(self, mock_chat):
        mock_chat.return_value = "This matches email addresses."
        explain_regex(r"[a-z]+@[a-z]+\.[a-z]{2,}")
        call_args = str(mock_chat.call_args)
        assert "@" in call_args


class TestCLI:
    @patch("app.check_ollama_running", return_value=True)
    @patch("app.chat")
    def test_generate_command(self, mock_chat, mock_ollama):
        mock_chat.return_value = "Pattern: `\\d+`\nMatches digits."
        runner = CliRunner()
        result = runner.invoke(cli, ["generate", "numbers"])
        assert result.exit_code == 0

    @patch("app.check_ollama_running", return_value=True)
    @patch("app.chat")
    def test_explain_command(self, mock_chat, mock_ollama):
        mock_chat.return_value = "Matches one or more lowercase letters."
        runner = CliRunner()
        result = runner.invoke(cli, ["explain", "[a-z]+"])
        assert result.exit_code == 0

    def test_test_command(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["test", r"\d+", "abc123", "hello"])
        assert result.exit_code == 0

    @patch("app.check_ollama_running", return_value=False)
    def test_ollama_not_running(self, mock_ollama):
        runner = CliRunner()
        result = runner.invoke(cli, ["generate", "email"])
        assert result.exit_code != 0
