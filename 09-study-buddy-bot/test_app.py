"""Tests for Study Buddy Bot."""

import pytest
from unittest.mock import patch
from click.testing import CliRunner

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app import (
    generate_quiz,
    explain_concept,
    create_study_plan,
    generate_flashcards,
    main,
    MODES,
    SYSTEM_PROMPT,
)


class TestConfiguration:
    """Tests for app configuration."""

    def test_modes_defined(self):
        assert "quiz" in MODES
        assert "explain" in MODES
        assert "plan" in MODES
        assert "flashcards" in MODES
        assert len(MODES) >= 4

    def test_system_prompt_is_tutor(self):
        assert "tutor" in SYSTEM_PROMPT.lower() or "study" in SYSTEM_PROMPT.lower()


class TestGenerateQuiz:
    """Tests for quiz generation."""

    @patch("app.chat")
    def test_generates_quiz(self, mock_chat):
        mock_chat.return_value = "Q1: What is mitosis?\nA) Cell division..."
        result = generate_quiz("Biology", "Cell Division")
        assert "Q1" in result or "mitosis" in result.lower()

    @patch("app.chat")
    def test_quiz_mentions_topic(self, mock_chat):
        mock_chat.return_value = "Quiz..."
        generate_quiz("Math", "Algebra", num_questions=3)
        messages = mock_chat.call_args[0][0]
        assert "Algebra" in messages[0]["content"]
        assert "3" in messages[0]["content"]


class TestExplainConcept:
    """Tests for concept explanation."""

    @patch("app.chat")
    def test_explains_concept(self, mock_chat):
        mock_chat.return_value = "Photosynthesis is the process by which..."
        result = explain_concept("Biology", "Photosynthesis")
        assert "Photosynthesis" in result

    @patch("app.chat")
    def test_includes_depth(self, mock_chat):
        mock_chat.return_value = "Summary..."
        explain_concept("Physics", "Gravity", depth="summary")
        messages = mock_chat.call_args[0][0]
        assert "summary" in messages[0]["content"].lower()


class TestCreateStudyPlan:
    """Tests for study plan creation."""

    @patch("app.chat")
    def test_creates_plan(self, mock_chat):
        mock_chat.return_value = "Day 1: Review basics...\nDay 2: Practice problems..."
        result = create_study_plan("Chemistry", "Organic Chemistry", days=5)
        assert "Day 1" in result

    @patch("app.chat")
    def test_plan_uses_days(self, mock_chat):
        mock_chat.return_value = "Plan..."
        create_study_plan("Math", "Calculus", days=10)
        messages = mock_chat.call_args[0][0]
        assert "10" in messages[0]["content"]


class TestGenerateFlashcards:
    """Tests for flashcard generation."""

    @patch("app.chat")
    def test_generates_flashcards(self, mock_chat):
        mock_chat.return_value = "**Q:** What is DNA?\n**A:** Deoxyribonucleic acid..."
        result = generate_flashcards("Biology", "Genetics")
        assert "Q:" in result or "DNA" in result

    @patch("app.chat")
    def test_flashcard_count(self, mock_chat):
        mock_chat.return_value = "Flashcards..."
        generate_flashcards("History", "World War 2", count=15)
        messages = mock_chat.call_args[0][0]
        assert "15" in messages[0]["content"]


class TestCLI:
    """Tests for the CLI interface."""

    @patch("app.check_ollama_running", return_value=False)
    def test_exits_when_ollama_down(self, mock_check):
        runner = CliRunner()
        result = runner.invoke(main, ["--subject", "Biology", "--topic", "Cells"])
        assert result.exit_code != 0
