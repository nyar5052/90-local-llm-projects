"""Tests for the Symptom Checker Bot."""

import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner

from app import cli, check_symptoms, display_disclaimer, DISCLAIMER


@pytest.fixture
def runner():
    """Provide a Click CLI test runner."""
    return CliRunner()


class TestDisclaimer:
    """Tests for disclaimer display."""

    def test_disclaimer_content(self):
        """Disclaimer must contain key warning phrases."""
        assert "NOT a substitute" in DISCLAIMER
        assert "EDUCATIONAL" in DISCLAIMER
        assert "healthcare provider" in DISCLAIMER
        assert "NOT medical advice" in DISCLAIMER

    @patch("app.console")
    def test_display_disclaimer_uses_panel(self, mock_console):
        """display_disclaimer should print a rich Panel to the console."""
        display_disclaimer()
        mock_console.print.assert_called_once()
        args = mock_console.print.call_args
        panel = args[0][0]
        assert "DISCLAIMER" in panel.title


class TestCheckSymptoms:
    """Tests for the check_symptoms helper."""

    @patch("app.chat")
    def test_returns_response_and_history(self, mock_chat):
        """check_symptoms should return the LLM response and updated history."""
        mock_chat.return_value = "Possible causes include a common cold."
        response, history = check_symptoms("headache and fever")

        assert response == "Possible causes include a common cold."
        assert len(history) == 2
        assert history[0]["role"] == "user"
        assert history[1]["role"] == "assistant"

    @patch("app.chat")
    def test_preserves_conversation_history(self, mock_chat):
        """check_symptoms should append to existing conversation history."""
        mock_chat.return_value = "Follow-up information."
        existing = [
            {"role": "user", "content": "I have a headache."},
            {"role": "assistant", "content": "Initial response."},
        ]
        response, history = check_symptoms("it also hurts behind my eyes", existing)

        assert len(history) == 4
        assert history[2]["role"] == "user"
        assert history[3]["content"] == "Follow-up information."


class TestCheckCommand:
    """Tests for the CLI 'check' command."""

    @patch("app.check_ollama_running", return_value=True)
    @patch("app.chat", return_value="You may have a common cold. Please see a doctor.")
    def test_check_command_success(self, mock_chat, mock_ollama, runner):
        """The check command should display symptom analysis."""
        result = runner.invoke(cli, ["check", "--symptoms", "headache, fever"])
        assert result.exit_code == 0
        assert "Analyzing symptoms" in result.output

    @patch("app.check_ollama_running", return_value=False)
    def test_check_command_ollama_not_running(self, mock_ollama, runner):
        """The check command should fail gracefully when Ollama is down."""
        result = runner.invoke(cli, ["check", "--symptoms", "headache"])
        assert result.exit_code != 0
        assert "Ollama is not running" in result.output

    @patch("app.check_ollama_running", return_value=True)
    @patch("app.chat", side_effect=Exception("Connection refused"))
    def test_check_command_llm_error(self, mock_chat, mock_ollama, runner):
        """The check command should handle LLM communication errors."""
        result = runner.invoke(cli, ["check", "--symptoms", "chest pain"])
        assert result.exit_code != 0
        assert "Error" in result.output
