"""Tests for health_planner.cli module."""

from unittest.mock import patch

import pytest
from click.testing import CliRunner

from health_planner.cli import cli

MOCK_PLAN = """## Overview
A plan for better sleep.

## Diet Suggestions
- Avoid caffeine after 2 PM.

## Exercise Plan
- Walk 30 minutes daily.

## Sleep Recommendations
- Consistent schedule.

## Stress Management
- Deep breathing.

## Sample Weekly Schedule
| Day | Activity |
|-----|----------|
| Mon | Walk     |

⚠️ Consult a healthcare professional.
"""


@pytest.fixture
def runner():
    """Create a Click CLI test runner."""
    return CliRunner()


# ===========================================================================
# Generate command
# ===========================================================================
class TestGenerateCommand:
    """Tests for the 'generate' CLI command."""

    @patch("health_planner.cli.check_ollama_running", return_value=True)
    @patch("health_planner.cli.generate_plan", return_value=MOCK_PLAN)
    def test_generate_basic(self, mock_gen, mock_check, runner):
        result = runner.invoke(cli, ["generate", "--goal", "better sleep"])
        assert result.exit_code == 0
        assert "better sleep" in result.output.lower() or "Wellness Plan" in result.output

    @patch("health_planner.cli.check_ollama_running", return_value=True)
    @patch("health_planner.cli.generate_plan", return_value=MOCK_PLAN)
    def test_generate_with_all_options(self, mock_gen, mock_check, runner):
        result = runner.invoke(
            cli,
            [
                "generate",
                "--goal", "lose weight",
                "--age", "30",
                "--lifestyle", "sedentary",
                "--duration", "1month",
            ],
        )
        assert result.exit_code == 0

    @patch("health_planner.cli.check_ollama_running", return_value=False)
    def test_generate_ollama_not_running(self, mock_check, runner):
        result = runner.invoke(cli, ["generate", "--goal", "better sleep"])
        assert result.exit_code != 0
        assert "Ollama" in result.output

    @patch("health_planner.cli.check_ollama_running", return_value=True)
    @patch("health_planner.cli.generate_plan", return_value=MOCK_PLAN)
    def test_generate_with_different_lifestyles(self, mock_gen, mock_check, runner):
        for lifestyle in ["sedentary", "moderate", "active"]:
            result = runner.invoke(
                cli, ["generate", "--goal", "get fit", "--lifestyle", lifestyle]
            )
            assert result.exit_code == 0


# ===========================================================================
# Interactive command
# ===========================================================================
class TestInteractiveCommand:
    """Tests for the 'interactive' CLI command."""

    @patch("health_planner.cli.check_ollama_running", return_value=False)
    def test_interactive_ollama_not_running(self, mock_check, runner):
        result = runner.invoke(cli, ["interactive"])
        assert result.exit_code != 0
        assert "Ollama" in result.output

    @patch("health_planner.cli.check_ollama_running", return_value=True)
    @patch("health_planner.cli.generate_plan", return_value=MOCK_PLAN)
    def test_interactive_with_inputs(self, mock_gen, mock_check, runner):
        result = runner.invoke(
            cli,
            ["interactive"],
            input="better sleep\n25\nmoderate\n1month\n",
        )
        assert result.exit_code == 0
        mock_gen.assert_called_once()


# ===========================================================================
# Milestones command
# ===========================================================================
class TestMilestonesCommand:
    """Tests for the 'milestones' CLI command."""

    def test_milestones_displays(self, runner):
        result = runner.invoke(cli, ["milestones", "--goal", "lose weight"])
        assert result.exit_code == 0
        assert "Milestone" in result.output or "milestone" in result.output.lower()

    def test_milestones_unknown_goal(self, runner):
        result = runner.invoke(cli, ["milestones", "--goal", "random goal"])
        assert result.exit_code == 0


# ===========================================================================
# Progress command
# ===========================================================================
class TestProgressCommand:
    """Tests for the 'progress' CLI command."""

    def test_progress_no_plan(self, runner):
        result = runner.invoke(cli, ["progress"])
        # Should succeed (exit 0) even without a plan — just shows a message
        assert result.exit_code == 0
