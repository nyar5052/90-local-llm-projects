"""Tests for IT Helpdesk Bot core logic."""

import pytest
from unittest.mock import patch

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.helpdesk_bot.core import get_response, CATEGORIES, SYSTEM_PROMPT
from src.helpdesk_bot.utils import search_knowledge_base, get_solution_template, DEFAULT_KB


class TestCategories:
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
    @patch("src.helpdesk_bot.core.chat")
    def test_returns_response(self, mock_chat):
        mock_chat.return_value = "Have you tried restarting your computer?"
        result = get_response("My computer is slow", [])
        assert result == "Have you tried restarting your computer?"

    @patch("src.helpdesk_bot.core.chat")
    def test_includes_history(self, mock_chat):
        mock_chat.return_value = "Follow-up answer."
        history = [
            {"role": "user", "content": "First message"},
            {"role": "assistant", "content": "First response"},
        ]
        get_response("Second message", history)
        messages = mock_chat.call_args[0][0]
        assert len(messages) == 3

    @patch("src.helpdesk_bot.core.chat")
    def test_uses_system_prompt(self, mock_chat):
        mock_chat.return_value = "Response"
        get_response("Help me", [])
        assert mock_chat.call_args[1]["system_prompt"] == SYSTEM_PROMPT


class TestKnowledgeBase:
    def test_search_returns_results(self):
        results = search_knowledge_base("password", DEFAULT_KB)
        assert len(results) >= 1
        assert any("Password" in r["topic"] for r in results)

    def test_search_no_results(self):
        results = search_knowledge_base("xyznonexistent", DEFAULT_KB)
        assert len(results) == 0


class TestSolutionTemplates:
    def test_hardware_template(self):
        t = get_solution_template("hardware")
        assert t is not None
        assert "Hardware" in t

    def test_unknown_category(self):
        assert get_solution_template("quantum") is None


class TestSystemPrompt:
    def test_system_prompt_is_it_expert(self):
        assert "IT" in SYSTEM_PROMPT or "helpdesk" in SYSTEM_PROMPT.lower()

    def test_system_prompt_mentions_troubleshooting(self):
        assert "troubleshooting" in SYSTEM_PROMPT.lower() or "diagnose" in SYSTEM_PROMPT.lower()
