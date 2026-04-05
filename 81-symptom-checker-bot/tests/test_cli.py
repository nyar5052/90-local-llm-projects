"""
Tests for symptom_checker.cli module.
"""

import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner
from symptom_checker.cli import cli


@pytest.fixture
def runner():
    return CliRunner()


# -----------------------------------------------------------------------
# CLI group tests
# -----------------------------------------------------------------------

class TestCLIGroup:
    def test_cli_help(self, runner):
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "Symptom Checker" in result.output


# -----------------------------------------------------------------------
# Check command tests
# -----------------------------------------------------------------------

class TestCheckCommand:
    @patch("symptom_checker.cli.check_symptoms")
    @patch("symptom_checker.cli.check_ollama_running", return_value=True)
    @patch("symptom_checker.cli.display_disclaimer")
    def test_check_success(self, mock_disclaimer, mock_ollama, mock_check, runner):
        mock_check.return_value = "Rest and stay hydrated."
        result = runner.invoke(cli, ["check", "--symptoms", "headache"])
        assert result.exit_code == 0
        assert "Analysis" in result.output or "Urgency" in result.output

    @patch("symptom_checker.cli.check_ollama_running", return_value=False)
    @patch("symptom_checker.cli.display_disclaimer")
    def test_check_ollama_not_running(self, mock_disclaimer, mock_ollama, runner):
        result = runner.invoke(cli, ["check", "--symptoms", "headache"])
        assert result.exit_code != 0

    def test_check_no_symptoms(self, runner):
        result = runner.invoke(cli, ["check"])
        assert result.exit_code != 0


# -----------------------------------------------------------------------
# Regions command tests
# -----------------------------------------------------------------------

class TestRegionsCommand:
    def test_regions_output(self, runner):
        result = runner.invoke(cli, ["regions"])
        assert result.exit_code == 0
        assert "Head" in result.output or "head" in result.output.lower()

    def test_regions_lists_all(self, runner):
        result = runner.invoke(cli, ["regions"])
        assert result.exit_code == 0
        # Check for several region names
        output_lower = result.output.lower()
        for region in ["head", "chest", "abdomen", "limbs"]:
            assert region in output_lower, f"Missing region: {region}"


# -----------------------------------------------------------------------
# History command tests
# -----------------------------------------------------------------------

class TestHistoryCommand:
    def test_history_empty(self, runner):
        result = runner.invoke(cli, ["history"])
        assert result.exit_code == 0
        assert "No symptom checks" in result.output or "history" in result.output.lower()
