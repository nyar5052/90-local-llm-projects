"""Tests for Language Learning Bot."""

import pytest
from unittest.mock import patch
from click.testing import CliRunner

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app import (
    get_system_prompt,
    get_response,
    get_lesson,
    main,
    LANGUAGES,
    LEVELS,
    SYSTEM_PROMPT_TEMPLATE,
)


class TestConfiguration:
    """Tests for app configuration."""

    def test_languages_defined(self):
        assert len(LANGUAGES) >= 10
        assert "spanish" in LANGUAGES
        assert "french" in LANGUAGES
        assert "japanese" in LANGUAGES

    def test_levels_defined(self):
        assert "beginner" in LEVELS
        assert "intermediate" in LEVELS
        assert "advanced" in LEVELS

    def test_system_prompt_template_has_placeholders(self):
        assert "{language}" in SYSTEM_PROMPT_TEMPLATE
        assert "{level}" in SYSTEM_PROMPT_TEMPLATE


class TestGetSystemPrompt:
    """Tests for system prompt generation."""

    def test_includes_language(self):
        prompt = get_system_prompt("spanish", "beginner")
        assert "Spanish" in prompt

    def test_includes_level(self):
        prompt = get_system_prompt("french", "advanced")
        assert "advanced" in prompt

    def test_different_languages_different_prompts(self):
        spanish = get_system_prompt("spanish", "beginner")
        french = get_system_prompt("french", "beginner")
        assert spanish != french


class TestGetResponse:
    """Tests for response generation."""

    @patch("app.chat")
    def test_returns_response(self, mock_chat):
        mock_chat.return_value = "¡Hola! ¿Cómo estás?"
        result = get_response("Hello!", [], "spanish", "beginner")
        assert "Hola" in result

    @patch("app.chat")
    def test_includes_history(self, mock_chat):
        mock_chat.return_value = "Response..."
        history = [
            {"role": "user", "content": "Hi"},
            {"role": "assistant", "content": "Hola"},
        ]
        get_response("How are you?", history, "spanish", "beginner")
        messages = mock_chat.call_args[0][0]
        assert len(messages) == 3


class TestGetLesson:
    """Tests for lesson generation."""

    @patch("app.chat")
    def test_returns_lesson(self, mock_chat):
        mock_chat.return_value = "Lesson: Greetings in Spanish..."
        result = get_lesson("greetings", "spanish", "beginner")
        assert "Lesson" in result or "Greetings" in result

    @patch("app.chat")
    def test_lesson_mentions_topic(self, mock_chat):
        mock_chat.return_value = "Lesson content..."
        get_lesson("food vocabulary", "french", "intermediate")
        messages = mock_chat.call_args[0][0]
        assert "food vocabulary" in messages[0]["content"].lower()


class TestCLI:
    """Tests for the CLI interface."""

    @patch("app.check_ollama_running", return_value=False)
    def test_exits_when_ollama_down(self, mock_check):
        runner = CliRunner()
        result = runner.invoke(main, ["--language", "spanish"])
        assert result.exit_code != 0
