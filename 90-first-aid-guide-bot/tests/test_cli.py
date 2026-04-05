"""Tests for the First Aid Guide Bot CLI."""

from unittest.mock import patch

import pytest
from click.testing import CliRunner

from first_aid.cli import cli, _contact_manager
from first_aid.core import COMMON_SCENARIOS


@pytest.fixture
def runner():
    """Create a CLI test runner."""
    return CliRunner()


@pytest.fixture(autouse=True)
def _clear_contacts():
    """Clear contact manager before each test."""
    _contact_manager._contacts.clear()


# -------------------------------------------------------------------
# Guide command
# -------------------------------------------------------------------
class TestGuideCommand:
    """Tests for the guide command."""

    @patch("first_aid.cli.check_ollama_running", return_value=True)
    @patch("first_aid.cli.generate")
    def test_guide_generates_instructions(self, mock_generate, mock_ollama, runner):
        mock_generate.return_value = {
            "response": (
                "⚠️ CALL 911 IF the burn is larger than 3 inches.\n\n"
                "## Step-by-Step Instructions\n"
                "1. Cool the burn under cool running water.\n"
            )
        }
        result = runner.invoke(cli, ["guide", "--situation", "minor burn"])
        assert result.exit_code == 0
        assert mock_generate.called

    @patch("first_aid.cli.check_ollama_running", return_value=False)
    def test_guide_ollama_not_running(self, mock_ollama, runner):
        result = runner.invoke(cli, ["guide", "--situation", "burn"])
        assert result.exit_code != 0

    def test_guide_requires_situation(self, runner):
        result = runner.invoke(cli, ["guide"])
        assert result.exit_code != 0


# -------------------------------------------------------------------
# Chat command
# -------------------------------------------------------------------
class TestChatCommand:
    """Tests for the chat command."""

    @patch("first_aid.cli.check_ollama_running", return_value=True)
    @patch("first_aid.cli.chat")
    def test_chat_interaction(self, mock_chat, mock_ollama, runner):
        mock_chat.return_value = {
            "message": {"content": "For a minor cut:\n1. Wash your hands.\n2. Apply pressure."}
        }
        result = runner.invoke(cli, ["chat"], input="How do I treat a cut?\nquit\n")
        assert result.exit_code == 0
        assert mock_chat.called

    @patch("first_aid.cli.check_ollama_running", return_value=False)
    def test_chat_ollama_not_running(self, mock_ollama, runner):
        result = runner.invoke(cli, ["chat"])
        assert result.exit_code != 0


# -------------------------------------------------------------------
# List command
# -------------------------------------------------------------------
class TestListCommand:
    """Tests for the list command."""

    def test_list_shows_scenarios(self, runner):
        result = runner.invoke(cli, ["list"])
        assert result.exit_code == 0
        for name, _, _, _ in COMMON_SCENARIOS[:5]:
            assert name in result.output

    def test_list_shows_911(self, runner):
        result = runner.invoke(cli, ["list"])
        assert "911" in result.output


# -------------------------------------------------------------------
# Triage command
# -------------------------------------------------------------------
class TestTriageCommand:
    """Tests for the triage command."""

    def test_triage_defaults(self, runner):
        result = runner.invoke(cli, ["triage"])
        assert result.exit_code == 0
        assert "911" in result.output

    def test_triage_unconscious_not_breathing(self, runner):
        result = runner.invoke(cli, ["triage", "--unconscious", "--not-breathing"])
        assert result.exit_code == 0
        assert "CRITICAL" in result.output
        assert "911" in result.output

    def test_triage_conscious_breathing_bleeding(self, runner):
        result = runner.invoke(cli, ["triage", "--conscious", "--breathing", "--bleeding"])
        assert result.exit_code == 0
        assert "911" in result.output

    def test_triage_conscious_breathing_no_bleeding(self, runner):
        result = runner.invoke(cli, ["triage", "--conscious", "--breathing"])
        assert result.exit_code == 0

    def test_triage_conscious_not_breathing(self, runner):
        result = runner.invoke(cli, ["triage", "--conscious", "--not-breathing"])
        assert result.exit_code == 0
        assert "CRITICAL" in result.output


# -------------------------------------------------------------------
# Supplies command
# -------------------------------------------------------------------
class TestSuppliesCommand:
    """Tests for the supplies command."""

    def test_supplies_all(self, runner):
        result = runner.invoke(cli, ["supplies"])
        assert result.exit_code == 0
        assert "Adhesive bandages" in result.output

    def test_supplies_essential(self, runner):
        result = runner.invoke(cli, ["supplies", "--priority", "essential"])
        assert result.exit_code == 0
        assert "Essential" in result.output

    def test_supplies_recommended(self, runner):
        result = runner.invoke(cli, ["supplies", "--priority", "recommended"])
        assert result.exit_code == 0

    def test_supplies_optional(self, runner):
        result = runner.invoke(cli, ["supplies", "--priority", "optional"])
        assert result.exit_code == 0

    def test_supplies_invalid_priority(self, runner):
        result = runner.invoke(cli, ["supplies", "--priority", "invalid"])
        assert result.exit_code != 0


# -------------------------------------------------------------------
# CPR command
# -------------------------------------------------------------------
class TestCPRCommand:
    """Tests for the cpr command."""

    def test_cpr_display(self, runner):
        result = runner.invoke(cli, ["cpr"])
        assert result.exit_code == 0
        assert "911" in result.output
        assert "compression" in result.output.lower()

    def test_cpr_shows_steps(self, runner):
        result = runner.invoke(cli, ["cpr"])
        assert "Step 1" in result.output
        assert "Step 2" in result.output


# -------------------------------------------------------------------
# Contacts command
# -------------------------------------------------------------------
class TestContactsCommand:
    """Tests for the contacts command."""

    def test_contacts_list_empty(self, runner):
        result = runner.invoke(cli, ["contacts", "--list"])
        assert result.exit_code == 0
        assert "911" in result.output

    def test_contacts_add(self, runner):
        result = runner.invoke(
            cli,
            ["contacts", "--add"],
            input="John Doe\n555-0100\nFather\nn\n",
        )
        assert result.exit_code == 0
        assert "Added" in result.output

    def test_contacts_remove_not_found(self, runner):
        result = runner.invoke(
            cli,
            ["contacts", "--remove"],
            input="Nobody\n",
        )
        assert result.exit_code == 0
        assert "not found" in result.output

    def test_contacts_shows_emergency_numbers(self, runner):
        result = runner.invoke(cli, ["contacts"])
        assert "911" in result.output
        assert "1-800-222-1222" in result.output


# -------------------------------------------------------------------
# Error cases
# -------------------------------------------------------------------
class TestErrorCases:
    """Tests for error handling."""

    def test_unknown_command(self, runner):
        result = runner.invoke(cli, ["nonexistent"])
        assert result.exit_code != 0

    @patch("first_aid.cli.check_ollama_running", return_value=True)
    @patch("first_aid.cli.generate", side_effect=Exception("Connection failed"))
    def test_guide_handles_llm_error(self, mock_generate, mock_ollama, runner):
        result = runner.invoke(cli, ["guide", "--situation", "burn"])
        assert result.exit_code == 0
        assert "Error" in result.output or "error" in result.output.lower()
