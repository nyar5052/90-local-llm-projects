"""Tests for Language Learning Bot core logic."""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from language_learner.core import (
    get_system_prompt,
    get_response,
    get_lesson,
    get_pronunciation_tips,
    generate_lesson_plan,
    add_vocabulary_word,
    load_vocabulary,
    get_vocabulary_quiz,
    record_session,
    load_progress,
    get_progress_summary,
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

    @patch("language_learner.core.chat")
    def test_returns_response(self, mock_chat):
        mock_chat.return_value = "¡Hola! ¿Cómo estás?"
        result = get_response("Hello!", [], "spanish", "beginner")
        assert "Hola" in result

    @patch("language_learner.core.chat")
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

    @patch("language_learner.core.chat")
    def test_returns_lesson(self, mock_chat):
        mock_chat.return_value = "Lesson: Greetings in Spanish..."
        result = get_lesson("greetings", "spanish", "beginner")
        assert "Lesson" in result or "Greetings" in result

    @patch("language_learner.core.chat")
    def test_lesson_mentions_topic(self, mock_chat):
        mock_chat.return_value = "Lesson content..."
        get_lesson("food vocabulary", "french", "intermediate")
        messages = mock_chat.call_args[0][0]
        assert "food vocabulary" in messages[0]["content"].lower()


class TestPronunciationTips:
    """Tests for pronunciation tips."""

    @patch("language_learner.core.chat")
    def test_returns_tips(self, mock_chat):
        mock_chat.return_value = "The word 'hola' is pronounced..."
        result = get_pronunciation_tips("hola", "spanish")
        assert "hola" in result.lower()


class TestLessonPlan:
    """Tests for lesson plan generation."""

    @patch("language_learner.core.chat")
    def test_generates_plan(self, mock_chat):
        mock_chat.return_value = "Week 1: Greetings and introductions..."
        result = generate_lesson_plan("spanish", "beginner", 4)
        assert "Week" in result


class TestVocabulary:
    """Tests for vocabulary tracker."""

    @patch("language_learner.core.save_json_file")
    @patch("language_learner.core.load_json_file", return_value=[])
    def test_add_word(self, mock_load, mock_save):
        entry = add_vocabulary_word("spanish", "hola", "hello")
        assert entry["word"] == "hola"
        assert entry["translation"] == "hello"
        assert entry["id"] == 1
        mock_save.assert_called_once()

    @patch("language_learner.core.load_json_file", return_value=[
        {"word": "hola", "translation": "hello", "added_date": "2024-01-01T00:00:00"}
    ])
    def test_load_vocabulary(self, mock_load):
        vocab = load_vocabulary("spanish")
        assert len(vocab) == 1
        assert vocab[0]["word"] == "hola"


class TestProgress:
    """Tests for progress tracking."""

    @patch("language_learner.core.save_json_file")
    @patch("language_learner.core.load_json_file", return_value={
        "language": "spanish", "sessions": [], "total_time_minutes": 0
    })
    def test_record_session(self, mock_load, mock_save):
        session = record_session("spanish", "beginner", 15, "conversation")
        assert session["duration_minutes"] == 15
        assert session["level"] == "beginner"

    @patch("language_learner.core.load_json_file", return_value={
        "language": "spanish", "sessions": [{"date": "2024-01-01T00:00:00"}],
        "total_time_minutes": 30
    })
    @patch("language_learner.core.load_vocabulary", return_value=[{"word": "hola"}])
    def test_progress_summary(self, mock_vocab, mock_load):
        summary = get_progress_summary("spanish")
        assert "Spanish" in summary
        assert "Sessions" in summary
