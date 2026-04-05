"""Tests for IT Helpdesk Bot."""

import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app import get_response, display_categories, main, CATEGORIES, SYSTEM_PROMPT


class TestCategories:
    """Tests for support categories."""

    def test_all_categories_exist(self):
        assert len(CATEGORIES) == 7

    def test_categories_have_name_and_description(self):
        for key, (name, desc) in CATEGORIES.items():
            assert len(name) > 0
            assert len(desc) > 0

    def test_category_keys_are_sequential(self):
        keys = sorted(CATEGORIES.keys())
        assert keys == [str(i) for i in range(1, 8)]


class TestGetResponse:
    """Tests for the get_response function."""

    @patch("app.chat")
    def test_returns_response(self, mock_chat):
        mock_chat.return_value = "Have you tried restarting your computer?"
        result = get_response("My computer is slow", [])
        assert result == "Have you tried restarting your computer?"

    @patch("app.chat")
    def test_includes_history(self, mock_chat):
        mock_chat.return_value = "Follow-up answer."
        history = [
            {"role": "user", "content": "First message"},
            {"role": "assistant", "content": "First response"},
        ]
        get_response("Second message", history)
        call_args = mock_chat.call_args
        messages = call_args[0][0]
        assert len(messages) == 3

    @patch("app.chat")
    def test_uses_system_prompt(self, mock_chat):
        mock_chat.return_value = "Response"
        get_response("Help me", [])
        call_args = mock_chat.call_args
        assert call_args[1]["system_prompt"] == SYSTEM_PROMPT


class TestSystemPrompt:
    """Tests for the system prompt configuration."""

    def test_system_prompt_is_it_expert(self):
        assert "IT" in SYSTEM_PROMPT or "helpdesk" in SYSTEM_PROMPT.lower()

    def test_system_prompt_mentions_troubleshooting(self):
        assert "troubleshooting" in SYSTEM_PROMPT.lower() or "diagnose" in SYSTEM_PROMPT.lower()


class TestCLI:
    """Tests for the CLI interface."""

    @patch("app.check_ollama_running", return_value=False)
    def test_exits_when_ollama_down(self, mock_check):
        runner = CliRunner()
        result = runner.invoke(main, [])
        assert result.exit_code != 0
