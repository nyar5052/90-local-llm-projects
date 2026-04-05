"""Tests for stress_manager.cli module."""

from unittest.mock import patch, MagicMock

import pytest
from click.testing import CliRunner

from stress_manager.cli import cli


@pytest.fixture
def runner():
    """Create a CLI test runner."""
    return CliRunner()


# ---------------------------------------------------------------------------
# Chat command
# ---------------------------------------------------------------------------

class TestChatCommand:
    """Tests for the chat command."""

    @patch("stress_manager.cli.check_ollama_running", return_value=True)
    @patch("stress_manager.cli.chat")
    def test_chat_session(self, mock_chat, mock_ollama, runner):
        mock_chat.return_value = {
            "message": {"content": "I hear you. Let's try a grounding technique."}
        }
        result = runner.invoke(cli, ["chat"], input="I feel stressed\nquit\n")
        assert result.exit_code == 0
        assert mock_chat.called

    @patch("stress_manager.cli.check_ollama_running", return_value=False)
    def test_chat_ollama_not_running(self, mock_ollama, runner):
        result = runner.invoke(cli, ["chat"])
        assert result.exit_code != 0
        assert "not running" in result.output.lower() or "Ollama" in result.output


# ---------------------------------------------------------------------------
# Breathe command
# ---------------------------------------------------------------------------

class TestBreatheCommand:
    """Tests for the breathe command."""

    @patch("stress_manager.core.check_ollama_running", return_value=True)
    @patch("stress_manager.cli.check_ollama_running", return_value=True)
    @patch("stress_manager.cli.generate")
    @patch("stress_manager.core.time.sleep")
    def test_breathe_with_technique(self, mock_sleep, mock_generate, mock_ollama_cli, mock_ollama_core, runner):
        mock_generate.return_value = {"response": "Great job completing the exercise."}
        result = runner.invoke(cli, ["breathe", "--technique", "box"])
        assert result.exit_code == 0
        assert mock_sleep.called

    @patch("stress_manager.core.check_ollama_running", return_value=False)
    @patch("stress_manager.cli.check_ollama_running", return_value=False)
    @patch("stress_manager.core.time.sleep")
    def test_breathe_without_ollama(self, mock_sleep, mock_ollama_cli, mock_ollama_core, runner):
        result = runner.invoke(cli, ["breathe", "--technique", "478"])
        assert result.exit_code == 0
        assert mock_sleep.called


# ---------------------------------------------------------------------------
# Journal command
# ---------------------------------------------------------------------------

class TestJournalCommand:
    """Tests for the journal command."""

    @patch("stress_manager.cli.check_ollama_running", return_value=True)
    @patch("stress_manager.cli.generate")
    def test_journal_prompt(self, mock_generate, mock_ollama, runner):
        mock_generate.return_value = {
            "response": "What are three things you're grateful for today?"
        }
        result = runner.invoke(cli, ["journal"], input="\n\n")
        assert result.exit_code == 0
        assert mock_generate.called

    @patch("stress_manager.cli.check_ollama_running", return_value=False)
    def test_journal_ollama_not_running(self, mock_ollama, runner):
        result = runner.invoke(cli, ["journal"])
        assert result.exit_code != 0


# ---------------------------------------------------------------------------
# Assess command
# ---------------------------------------------------------------------------

class TestAssessCommand:
    """Tests for the assess command."""

    @patch("stress_manager.cli.check_ollama_running", return_value=True)
    @patch("stress_manager.cli.generate")
    def test_assess_completes(self, mock_generate, mock_ollama, runner):
        mock_generate.return_value = {
            "response": "Based on your assessment, try deep breathing."
        }
        result = runner.invoke(cli, ["assess"], input="7\n5\n4\n8\n3\n")
        assert result.exit_code == 0
        assert mock_generate.called

    @patch("stress_manager.cli.check_ollama_running", return_value=False)
    def test_assess_ollama_not_running(self, mock_ollama, runner):
        result = runner.invoke(cli, ["assess"])
        assert result.exit_code != 0


# ---------------------------------------------------------------------------
# Score command
# ---------------------------------------------------------------------------

class TestScoreCommand:
    """Tests for the score command."""

    def test_score_completes(self, runner):
        result = runner.invoke(cli, ["score"], input="5\n5\n5\n5\n5\n")
        assert result.exit_code == 0
        assert "Stress Score" in result.output or "MODERATE" in result.output

    def test_score_high(self, runner):
        result = runner.invoke(cli, ["score"], input="9\n9\n9\n9\n9\n")
        assert result.exit_code == 0
        assert "CRITICAL" in result.output


# ---------------------------------------------------------------------------
# Worksheet command
# ---------------------------------------------------------------------------

class TestWorksheetCommand:
    """Tests for the worksheet command."""

    def test_worksheet_thought_record(self, runner):
        result = runner.invoke(cli, ["worksheet", "--type", "thought_record"])
        assert result.exit_code == 0
        assert "Thought Record" in result.output

    def test_worksheet_behavioral_activation(self, runner):
        result = runner.invoke(cli, ["worksheet", "--type", "behavioral_activation"])
        assert result.exit_code == 0
        assert "Behavioral Activation" in result.output

    def test_worksheet_worry_time(self, runner):
        result = runner.invoke(cli, ["worksheet", "--type", "worry_time"])
        assert result.exit_code == 0
        assert "Worry Time" in result.output


# ---------------------------------------------------------------------------
# Coping command
# ---------------------------------------------------------------------------

class TestCopingCommand:
    """Tests for the coping command."""

    def test_coping_low(self, runner):
        result = runner.invoke(cli, ["coping", "--level", "low"])
        assert result.exit_code == 0

    def test_coping_moderate(self, runner):
        result = runner.invoke(cli, ["coping", "--level", "moderate"])
        assert result.exit_code == 0

    def test_coping_high(self, runner):
        result = runner.invoke(cli, ["coping", "--level", "high"])
        assert result.exit_code == 0


# ---------------------------------------------------------------------------
# Toolkit command
# ---------------------------------------------------------------------------

class TestToolkitCommand:
    """Tests for the toolkit command."""

    def test_toolkit_displays(self, runner):
        result = runner.invoke(cli, ["toolkit"])
        assert result.exit_code == 0
        assert "PHYSICAL" in result.output
        assert "COGNITIVE" in result.output
        assert "SOCIAL" in result.output
        assert "CREATIVE" in result.output


# ---------------------------------------------------------------------------
# Error cases
# ---------------------------------------------------------------------------

class TestErrorCases:
    """Tests for error handling."""

    def test_invalid_command(self, runner):
        result = runner.invoke(cli, ["nonexistent"])
        assert result.exit_code != 0

    def test_breathe_invalid_technique(self, runner):
        result = runner.invoke(cli, ["breathe", "--technique", "invalid"])
        assert result.exit_code != 0

    def test_worksheet_invalid_type(self, runner):
        result = runner.invoke(cli, ["worksheet", "--type", "invalid"])
        assert result.exit_code != 0

    def test_coping_invalid_level(self, runner):
        result = runner.invoke(cli, ["coping", "--level", "invalid"])
        assert result.exit_code != 0
