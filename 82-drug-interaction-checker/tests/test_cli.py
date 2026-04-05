"""Tests for drug_checker CLI module."""

import sys
import os
import pytest
from unittest.mock import patch
from click.testing import CliRunner

# Ensure the src directory is on the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from drug_checker.cli import cli


@pytest.fixture
def runner():
    """Provide a Click CLI test runner."""
    return CliRunner()


# ============================================================================
# Check Command Tests
# ============================================================================

class TestCheckCommand:
    """Tests for the CLI 'check' command."""

    @patch("drug_checker.cli.check_ollama_running", return_value=True)
    @patch("drug_checker.cli.check_interactions", return_value="No significant interactions found.")
    def test_check_command_success(self, mock_check, mock_ollama, runner):
        result = runner.invoke(cli, ["check", "--medications", "aspirin,ibuprofen"])
        assert result.exit_code == 0
        assert "Checking interactions" in result.output

    @patch("drug_checker.cli.check_ollama_running", return_value=False)
    def test_check_command_ollama_not_running(self, mock_ollama, runner):
        result = runner.invoke(cli, ["check", "--medications", "aspirin,ibuprofen"])
        assert result.exit_code != 0
        assert "Ollama is not running" in result.output

    @patch("drug_checker.cli.check_ollama_running", return_value=True)
    def test_check_command_single_medication(self, mock_ollama, runner):
        result = runner.invoke(cli, ["check", "--medications", "aspirin"])
        assert result.exit_code != 0
        assert "at least two" in result.output

    @patch("drug_checker.cli.check_ollama_running", return_value=True)
    @patch("drug_checker.cli.check_interactions", side_effect=Exception("Connection refused"))
    def test_check_command_llm_error(self, mock_check, mock_ollama, runner):
        result = runner.invoke(cli, ["check", "--medications", "aspirin,ibuprofen"])
        assert result.exit_code != 0
        assert "Error" in result.output


# ============================================================================
# Food Command Tests
# ============================================================================

class TestFoodCommand:
    """Tests for the CLI 'food' command."""

    def test_food_command_known_drug(self, runner):
        result = runner.invoke(cli, ["food", "--medication", "warfarin"])
        assert result.exit_code == 0
        assert "grapefruit" in result.output.lower()

    def test_food_command_unknown_drug(self, runner):
        result = runner.invoke(cli, ["food", "--medication", "unknownmed"])
        assert result.exit_code == 0
        assert "No food interactions found" in result.output


# ============================================================================
# Alternatives Command Tests
# ============================================================================

class TestAlternativesCommand:
    """Tests for the CLI 'alternatives' command."""

    def test_alternatives_known_drug(self, runner):
        result = runner.invoke(cli, ["alternatives", "--medication", "ibuprofen"])
        assert result.exit_code == 0
        assert "acetaminophen" in result.output.lower()

    def test_alternatives_unknown_drug(self, runner):
        result = runner.invoke(cli, ["alternatives", "--medication", "unknownmed"])
        assert result.exit_code == 0
        assert "No alternatives found" in result.output


# ============================================================================
# CLI Group Tests
# ============================================================================

class TestCLIGroup:
    """Tests for the CLI group and help text."""

    def test_help_displays(self, runner):
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "Drug Interaction Checker" in result.output

    def test_check_help(self, runner):
        result = runner.invoke(cli, ["check", "--help"])
        assert result.exit_code == 0
        assert "medications" in result.output.lower()

    def test_food_help(self, runner):
        result = runner.invoke(cli, ["food", "--help"])
        assert result.exit_code == 0
        assert "medication" in result.output.lower()

    def test_alternatives_help(self, runner):
        result = runner.invoke(cli, ["alternatives", "--help"])
        assert result.exit_code == 0
        assert "medication" in result.output.lower()
