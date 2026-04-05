"""Tests for Gift Recommendation Bot."""

import pytest
from unittest.mock import patch
from click.testing import CliRunner

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app import (
    generate_recommendations,
    get_gift_details,
    main,
    OCCASIONS,
    RELATIONSHIPS,
    SYSTEM_PROMPT,
)


class TestConfiguration:
    """Tests for app configuration."""

    def test_occasions_defined(self):
        assert "birthday" in OCCASIONS
        assert "christmas" in OCCASIONS
        assert "wedding" in OCCASIONS
        assert len(OCCASIONS) >= 10

    def test_relationships_defined(self):
        assert "partner" in RELATIONSHIPS
        assert "friend" in RELATIONSHIPS
        assert "parent" in RELATIONSHIPS
        assert len(RELATIONSHIPS) >= 5

    def test_system_prompt_is_gift_expert(self):
        assert "gift" in SYSTEM_PROMPT.lower()


class TestGenerateRecommendations:
    """Tests for recommendation generation."""

    @patch("app.chat")
    def test_basic_recommendations(self, mock_chat):
        mock_chat.return_value = "1. Custom Photo Album ($30)\n2. Gourmet Basket ($45)"
        result = generate_recommendations("birthday", "friend", 50)
        assert "Album" in result or "Basket" in result

    @patch("app.chat")
    def test_includes_budget(self, mock_chat):
        mock_chat.return_value = "Recommendations..."
        generate_recommendations("christmas", "partner", 100)
        messages = mock_chat.call_args[0][0]
        assert "$100" in messages[0]["content"]

    @patch("app.chat")
    def test_includes_interests(self, mock_chat):
        mock_chat.return_value = "Recommendations..."
        generate_recommendations("birthday", "friend", 50, interests="gaming,cooking")
        messages = mock_chat.call_args[0][0]
        assert "gaming" in messages[0]["content"].lower()

    @patch("app.chat")
    def test_includes_age(self, mock_chat):
        mock_chat.return_value = "Recommendations..."
        generate_recommendations("birthday", "child", 30, age="8")
        messages = mock_chat.call_args[0][0]
        assert "8" in messages[0]["content"]


class TestGetGiftDetails:
    """Tests for gift detail retrieval."""

    @patch("app.chat")
    def test_returns_details(self, mock_chat):
        mock_chat.return_value = "A custom photo album is a wonderful..."
        result = get_gift_details("Custom Photo Album", 50)
        assert "photo album" in result.lower()

    @patch("app.chat")
    def test_includes_budget(self, mock_chat):
        mock_chat.return_value = "Details..."
        get_gift_details("Board Game", 30)
        messages = mock_chat.call_args[0][0]
        assert "$30" in messages[0]["content"]


class TestCLI:
    """Tests for the CLI interface."""

    @patch("app.check_ollama_running", return_value=False)
    def test_exits_when_ollama_down(self, mock_check):
        runner = CliRunner()
        result = runner.invoke(main, ["--occasion", "birthday"])
        assert result.exit_code != 0
