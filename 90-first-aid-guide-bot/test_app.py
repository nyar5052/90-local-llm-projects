"""Tests for the First Aid Guide Bot."""

from unittest.mock import patch

import pytest
from click.testing import CliRunner

from app import cli, COMMON_SCENARIOS, EMERGENCY_DISCLAIMER


@pytest.fixture
def runner():
    """Create a CLI test runner."""
    return CliRunner()


class TestGuideCommand:
    """Tests for the guide command."""

    @patch("app.check_ollama_running", return_value=True)
    @patch("app.generate")
    def test_guide_generates_instructions(self, mock_generate, mock_ollama, runner):
        """Test that guide command generates first aid instructions."""
        mock_generate.return_value = {
            "response": (
                "⚠️ CALL 911 IF the burn is larger than 3 inches.\n\n"
                "## Step-by-Step Instructions\n"
                "1. Cool the burn under cool running water for 10-20 minutes.\n"
                "2. Do not apply ice directly.\n"
                "3. Cover with a sterile bandage."
            )
        }

        result = runner.invoke(cli, ["guide", "--situation", "minor burn"])
        assert result.exit_code == 0
        assert mock_generate.called
        # Verify disclaimer is shown
        assert "NOT" in result.output or "911" in result.output

    @patch("app.check_ollama_running", return_value=False)
    def test_guide_ollama_not_running(self, mock_ollama, runner):
        """Test guide command handles Ollama not running."""
        result = runner.invoke(cli, ["guide", "--situation", "burn"])
        assert result.exit_code != 0
        assert "not running" in result.output.lower() or "Ollama" in result.output

    def test_guide_requires_situation(self, runner):
        """Test that guide command requires --situation option."""
        result = runner.invoke(cli, ["guide"])
        assert result.exit_code != 0
        assert "Missing" in result.output or "required" in result.output.lower()


class TestListCommand:
    """Tests for the list command."""

    def test_list_shows_scenarios(self, runner):
        """Test that list command displays all common scenarios."""
        result = runner.invoke(cli, ["list"])
        assert result.exit_code == 0
        # Check that scenario names appear in output
        for name, _, _, _ in COMMON_SCENARIOS[:5]:
            assert name in result.output

    def test_list_shows_severity(self, runner):
        """Test that list command shows severity levels."""
        result = runner.invoke(cli, ["list"])
        assert result.exit_code == 0
        # Rich table may truncate columns; check for partial severity text
        assert "Moderate" in result.output or "Moder" in result.output
        assert "Low" in result.output or "Hig" in result.output

    def test_list_shows_emergency_reminder(self, runner):
        """Test that list command shows the 911 reminder."""
        result = runner.invoke(cli, ["list"])
        assert result.exit_code == 0
        assert "911" in result.output


class TestChatCommand:
    """Tests for the interactive chat command."""

    @patch("app.check_ollama_running", return_value=True)
    @patch("app.chat")
    def test_chat_interaction(self, mock_chat, mock_ollama, runner):
        """Test basic chat interaction with mocked LLM response."""
        mock_chat.return_value = {
            "message": {
                "content": (
                    "⚠️ CALL 911 IF the person is unconscious.\n\n"
                    "For a minor cut:\n"
                    "1. Wash your hands first.\n"
                    "2. Apply gentle pressure with a clean cloth."
                )
            }
        }

        result = runner.invoke(cli, ["chat"], input="How do I treat a cut?\nquit\n")
        assert result.exit_code == 0
        assert mock_chat.called

    @patch("app.check_ollama_running", return_value=False)
    def test_chat_ollama_not_running(self, mock_ollama, runner):
        """Test chat handles Ollama not running."""
        result = runner.invoke(cli, ["chat"])
        assert result.exit_code != 0
        assert "not running" in result.output.lower() or "Ollama" in result.output


class TestDisclaimer:
    """Tests for emergency disclaimer display."""

    def test_disclaimer_content(self):
        """Test that the disclaimer contains critical safety information."""
        assert "NOT" in EMERGENCY_DISCLAIMER
        assert "911" in EMERGENCY_DISCLAIMER
        assert "substitute" in EMERGENCY_DISCLAIMER.lower() or "medical" in EMERGENCY_DISCLAIMER.lower()

    def test_list_command_shows_disclaimer(self, runner):
        """Test that list command shows the disclaimer."""
        result = runner.invoke(cli, ["list"])
        assert result.exit_code == 0
        # The disclaimer should mention it's not a substitute or mention 911
        assert "911" in result.output
        assert "NOT" in result.output
