"""Tests for the Stress Management Bot."""

import time
from unittest.mock import patch, MagicMock

import pytest
from click.testing import CliRunner

from app import cli, run_breathing_exercise, BREATHING_EXERCISES, STRESS_QUESTIONS


@pytest.fixture
def runner():
    """Create a CLI test runner."""
    return CliRunner()


class TestBreathingExercise:
    """Tests for the guided breathing exercise."""

    @patch("app.time.sleep")
    def test_box_breathing_completes(self, mock_sleep):
        """Test that box breathing runs through all cycles without error."""
        run_breathing_exercise("box")

        exercise = BREATHING_EXERCISES["box"]
        total_seconds = sum(d for _, d in exercise["steps"]) * exercise["cycles"]
        # time.sleep is called once per second of breathing + initial 2-second pause
        assert mock_sleep.call_count == total_seconds + 1  # +1 for the 2s setup sleep (called once)
        # Actually the initial sleep(2) is one call, then each second is one call
        # Let's just verify it was called many times
        assert mock_sleep.call_count > 0

    @patch("app.time.sleep")
    def test_478_breathing_completes(self, mock_sleep):
        """Test that 4-7-8 breathing runs through all cycles."""
        run_breathing_exercise("478")

        exercise = BREATHING_EXERCISES["478"]
        total_seconds = sum(d for _, d in exercise["steps"]) * exercise["cycles"]
        assert mock_sleep.call_count > total_seconds


class TestChatCommand:
    """Tests for the interactive chat command."""

    @patch("app.check_ollama_running", return_value=True)
    @patch("app.chat")
    def test_chat_session(self, mock_chat, mock_ollama, runner):
        """Test basic chat interaction with mocked LLM response."""
        mock_chat.return_value = {
            "message": {
                "content": "I hear you. Let's try a simple grounding technique."
            }
        }

        result = runner.invoke(cli, ["chat"], input="I feel stressed\nquit\n")
        assert result.exit_code == 0
        assert mock_chat.called
        assert "Take care" in result.output or "Disclaimer" in result.output.upper() or "DISCLAIMER" in result.output

    @patch("app.check_ollama_running", return_value=False)
    def test_chat_ollama_not_running(self, mock_ollama, runner):
        """Test chat gracefully handles Ollama not running."""
        result = runner.invoke(cli, ["chat"])
        assert result.exit_code != 0
        assert "not running" in result.output.lower() or "Ollama" in result.output


class TestJournalCommand:
    """Tests for the journal prompt command."""

    @patch("app.check_ollama_running", return_value=True)
    @patch("app.generate")
    def test_journal_prompt_generation(self, mock_generate, mock_ollama, runner):
        """Test journal prompt generation with mocked LLM."""
        mock_generate.return_value = {
            "response": "What are three things you're grateful for today?"
        }

        result = runner.invoke(cli, ["journal"], input="\n\n")
        assert result.exit_code == 0
        assert mock_generate.called
        assert "grateful" in result.output.lower() or "Journal" in result.output


class TestAssessCommand:
    """Tests for the stress assessment command."""

    @patch("app.check_ollama_running", return_value=True)
    @patch("app.generate")
    def test_stress_assessment(self, mock_generate, mock_ollama, runner):
        """Test stress assessment with mocked responses."""
        mock_generate.return_value = {
            "response": "Based on your assessment, I recommend deep breathing and regular exercise."
        }

        # Provide answers for all 5 questions
        answers = "7\n5\n4\n8\n3\n"
        result = runner.invoke(cli, ["assess"], input=answers)
        assert result.exit_code == 0
        assert mock_generate.called
        assert "Recommendation" in result.output or "Results" in result.output


class TestBreatheCommand:
    """Tests for the breathe CLI command."""

    @patch("app.check_ollama_running", return_value=True)
    @patch("app.generate")
    @patch("app.time.sleep")
    def test_breathe_with_technique(self, mock_sleep, mock_generate, mock_ollama, runner):
        """Test breathe command with a specific technique."""
        mock_generate.return_value = {
            "response": "Great job completing the exercise. You should feel calmer now."
        }

        result = runner.invoke(cli, ["breathe", "--technique", "box"])
        assert result.exit_code == 0
        assert mock_sleep.called
        assert "DISCLAIMER" in result.output or "Disclaimer" in result.output or "NOT" in result.output
