"""Tests for the Drug Interaction Checker."""

import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner

from app import cli, parse_medications, check_interactions, display_disclaimer, DISCLAIMER


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
        assert "pharmacist" in DISCLAIMER
        assert "NOT medical advice" in DISCLAIMER

    @patch("app.console")
    def test_display_disclaimer_uses_panel(self, mock_console):
        """display_disclaimer should print a rich Panel to the console."""
        display_disclaimer()
        mock_console.print.assert_called_once()
        args = mock_console.print.call_args
        panel = args[0][0]
        assert "DISCLAIMER" in panel.title


class TestParseMedications:
    """Tests for medication string parsing."""

    def test_basic_parsing(self):
        """Should split comma-separated medications and strip whitespace."""
        result = parse_medications("aspirin, ibuprofen, lisinopril")
        assert result == ["aspirin", "ibuprofen", "lisinopril"]

    def test_empty_entries_filtered(self):
        """Should filter out empty entries from extra commas."""
        result = parse_medications("aspirin,,ibuprofen, ,")
        assert result == ["aspirin", "ibuprofen"]

    def test_single_medication(self):
        """Should return a single-item list for one medication."""
        result = parse_medications("aspirin")
        assert result == ["aspirin"]

    def test_empty_string(self):
        """Should return an empty list for empty input."""
        result = parse_medications("")
        assert result == []


class TestCheckInteractions:
    """Tests for the interaction checking function."""

    @patch("app.generate")
    def test_returns_llm_response(self, mock_generate):
        """check_interactions should return the LLM response text."""
        mock_generate.return_value = (
            "Major interaction: Aspirin + Ibuprofen may increase bleeding risk."
        )
        result = check_interactions(["aspirin", "ibuprofen"])
        assert "Major interaction" in result
        mock_generate.assert_called_once()

    @patch("app.generate")
    def test_prompt_contains_all_medications(self, mock_generate):
        """The prompt sent to the LLM should include all medications."""
        mock_generate.return_value = "No significant interactions found."
        check_interactions(["metformin", "lisinopril", "atorvastatin"])
        call_kwargs = mock_generate.call_args
        prompt = call_kwargs.kwargs.get("prompt") or call_kwargs[1].get("prompt") or call_kwargs[0][0]
        assert "metformin" in prompt
        assert "lisinopril" in prompt
        assert "atorvastatin" in prompt


class TestCheckCommand:
    """Tests for the CLI 'check' command."""

    @patch("app.check_ollama_running", return_value=True)
    @patch("app.generate", return_value="No significant interactions found.")
    def test_check_command_success(self, mock_generate, mock_ollama, runner):
        """The check command should display interaction results."""
        result = runner.invoke(cli, ["check", "--medications", "aspirin,ibuprofen"])
        assert result.exit_code == 0
        assert "Checking interactions" in result.output

    @patch("app.check_ollama_running", return_value=False)
    def test_check_command_ollama_not_running(self, mock_ollama, runner):
        """The check command should fail gracefully when Ollama is down."""
        result = runner.invoke(cli, ["check", "--medications", "aspirin,ibuprofen"])
        assert result.exit_code != 0
        assert "Ollama is not running" in result.output

    @patch("app.check_ollama_running", return_value=True)
    def test_check_command_single_medication(self, mock_ollama, runner):
        """The check command should reject a single medication."""
        result = runner.invoke(cli, ["check", "--medications", "aspirin"])
        assert result.exit_code != 0
        assert "at least two" in result.output

    @patch("app.check_ollama_running", return_value=True)
    @patch("app.generate", side_effect=Exception("Connection refused"))
    def test_check_command_llm_error(self, mock_generate, mock_ollama, runner):
        """The check command should handle LLM communication errors."""
        result = runner.invoke(cli, ["check", "--medications", "aspirin,ibuprofen"])
        assert result.exit_code != 0
        assert "Error" in result.output
