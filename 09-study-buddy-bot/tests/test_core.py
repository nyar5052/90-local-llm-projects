"""Tests for Study Buddy Bot core logic."""

import pytest
from unittest.mock import patch

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from study_buddy.core import (
    generate_quiz,
    explain_concept,
    create_study_plan,
    generate_flashcards,
    ask_question,
    record_study_session,
    get_study_stats,
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

    @patch("study_buddy.core.chat")
    def test_generates_quiz(self, mock_chat):
        mock_chat.return_value = "Q1: What is mitosis?\nA) Cell division..."
        result = generate_quiz("Biology", "Cell Division")
        assert "Q1" in result or "mitosis" in result.lower()

    @patch("study_buddy.core.chat")
    def test_quiz_mentions_topic(self, mock_chat):
        mock_chat.return_value = "Quiz..."
        generate_quiz("Math", "Algebra", num_questions=3)
        messages = mock_chat.call_args[0][0]
        assert "Algebra" in messages[0]["content"]
        assert "3" in messages[0]["content"]


class TestExplainConcept:
    """Tests for concept explanation."""

    @patch("study_buddy.core.chat")
    def test_explains_concept(self, mock_chat):
        mock_chat.return_value = "Photosynthesis is the process by which..."
        result = explain_concept("Biology", "Photosynthesis")
        assert "Photosynthesis" in result

    @patch("study_buddy.core.chat")
    def test_includes_depth(self, mock_chat):
        mock_chat.return_value = "Summary..."
        explain_concept("Physics", "Gravity", depth="summary")
        messages = mock_chat.call_args[0][0]
        assert "summary" in messages[0]["content"].lower()


class TestCreateStudyPlan:
    """Tests for study plan creation."""

    @patch("study_buddy.core.chat")
    def test_creates_plan(self, mock_chat):
        mock_chat.return_value = "Day 1: Review basics...\nDay 2: Practice problems..."
        result = create_study_plan("Chemistry", "Organic Chemistry", days=5)
        assert "Day 1" in result

    @patch("study_buddy.core.chat")
    def test_plan_uses_days(self, mock_chat):
        mock_chat.return_value = "Plan..."
        create_study_plan("Math", "Calculus", days=10)
        messages = mock_chat.call_args[0][0]
        assert "10" in messages[0]["content"]


class TestGenerateFlashcards:
    """Tests for flashcard generation."""

    @patch("study_buddy.core.chat")
    def test_generates_flashcards(self, mock_chat):
        mock_chat.return_value = "**Q:** What is DNA?\n**A:** Deoxyribonucleic acid..."
        result = generate_flashcards("Biology", "Genetics")
        assert "Q:" in result or "DNA" in result

    @patch("study_buddy.core.chat")
    def test_flashcard_count(self, mock_chat):
        mock_chat.return_value = "Flashcards..."
        generate_flashcards("History", "World War 2", count=15)
        messages = mock_chat.call_args[0][0]
        assert "15" in messages[0]["content"]


class TestProgress:
    """Tests for progress tracking."""

    @patch("study_buddy.core.save_json_file")
    @patch("study_buddy.core.load_json_file", return_value={"sessions": [], "subjects": {}})
    def test_record_session(self, mock_load, mock_save):
        session = record_study_session("Biology", "Cells", "quiz", 30)
        assert session["subject"] == "Biology"
        assert session["duration_minutes"] == 30
        mock_save.assert_called_once()

    @patch("study_buddy.core.load_json_file", return_value={
        "sessions": [{"duration_minutes": 30}, {"duration_minutes": 45}],
        "subjects": {"biology": {"total_minutes": 75, "session_count": 2, "topics": ["Cells"]}}
    })
    def test_get_stats(self, mock_load):
        stats = get_study_stats()
        assert stats["total_sessions"] == 2
        assert stats["total_minutes"] == 75


class TestCLI:
    """Tests for the CLI interface."""

    @patch("study_buddy.core.check_ollama_running", return_value=False)
    def test_exits_when_ollama_down(self, mock_check):
        from click.testing import CliRunner
        from study_buddy.cli import cli
        runner = CliRunner()
        result = runner.invoke(cli, ["study", "--subject", "Biology", "--topic", "Cells"])
        assert result.exit_code != 0
