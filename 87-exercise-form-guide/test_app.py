"""Tests for Exercise Form Guide application."""

import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner
from app import cli, VALID_LEVELS, VALID_MUSCLE_GROUPS, VALID_GOALS


@pytest.fixture
def runner():
    """Create a Click CLI test runner."""
    return CliRunner()


@pytest.fixture
def mock_ollama_running():
    """Mock check_ollama_running to return True."""
    with patch("app.check_ollama_running", return_value=True) as mock:
        yield mock


@pytest.fixture
def mock_generate():
    """Mock the generate function with a sample response."""
    sample_response = (
        "## Deadlift Form Guide\n\n"
        "### Exercise Description\n"
        "The deadlift is a compound exercise.\n\n"
        "### Target Muscles\n"
        "- Primary: Glutes, Hamstrings\n"
        "- Secondary: Erector Spinae, Core\n\n"
        "### Step-by-Step Instructions\n"
        "1. Stand with feet hip-width apart\n"
        "2. Hinge at the hips\n"
        "3. Grip the bar\n\n"
        "### Common Mistakes\n"
        "- Rounding the back\n\n"
        "### Breathing Cues\n"
        "- Inhale before lifting\n\n"
        "### Progressions\n"
        "- Romanian Deadlift\n\n"
        "### Safety Tips\n"
        "- Consult a trainer before attempting heavy loads.\n"
    )
    with patch("app.generate", return_value=sample_response) as mock:
        yield mock


class TestGuideCommand:
    """Tests for the 'guide' command."""

    def test_guide_generates_exercise_form(self, runner, mock_ollama_running, mock_generate):
        """Test that guide command generates form instructions for an exercise."""
        result = runner.invoke(cli, ["guide", "--exercise", "deadlift", "--level", "intermediate"])
        assert result.exit_code == 0
        mock_generate.assert_called_once()
        call_kwargs = mock_generate.call_args
        assert "deadlift" in call_kwargs.kwargs["prompt"].lower()
        assert "intermediate" in call_kwargs.kwargs["prompt"].lower()

    def test_guide_default_level_is_beginner(self, runner, mock_ollama_running, mock_generate):
        """Test that the default level is beginner when not specified."""
        result = runner.invoke(cli, ["guide", "--exercise", "squat"])
        assert result.exit_code == 0
        call_kwargs = mock_generate.call_args
        assert "beginner" in call_kwargs.kwargs["prompt"].lower()

    def test_guide_requires_exercise_option(self, runner):
        """Test that guide command requires --exercise option."""
        result = runner.invoke(cli, ["guide"])
        assert result.exit_code != 0
        assert "Missing option" in result.output or "required" in result.output.lower()

    def test_guide_invalid_level_rejected(self, runner):
        """Test that invalid levels are rejected."""
        result = runner.invoke(cli, ["guide", "--exercise", "pushup", "--level", "expert"])
        assert result.exit_code != 0

    def test_guide_ollama_not_running(self, runner):
        """Test error handling when Ollama is not running."""
        with patch("app.check_ollama_running", return_value=False):
            result = runner.invoke(cli, ["guide", "--exercise", "deadlift"])
            assert result.exit_code != 0


class TestListCommand:
    """Tests for the 'list' command."""

    def test_list_exercises_for_muscle_group(self, runner, mock_ollama_running, mock_generate):
        """Test listing exercises for a specific muscle group."""
        result = runner.invoke(cli, ["list", "--muscle-group", "legs"])
        assert result.exit_code == 0
        mock_generate.assert_called_once()
        call_kwargs = mock_generate.call_args
        assert "legs" in call_kwargs.kwargs["prompt"].lower()

    def test_list_invalid_muscle_group_rejected(self, runner):
        """Test that invalid muscle groups are rejected."""
        result = runner.invoke(cli, ["list", "--muscle-group", "fingers"])
        assert result.exit_code != 0


class TestRoutineCommand:
    """Tests for the 'routine' command."""

    def test_routine_generates_workout_plan(self, runner, mock_ollama_running, mock_generate):
        """Test that routine command generates a workout plan."""
        result = runner.invoke(cli, ["routine", "--goal", "strength", "--level", "beginner"])
        assert result.exit_code == 0
        mock_generate.assert_called_once()
        call_kwargs = mock_generate.call_args
        assert "strength" in call_kwargs.kwargs["prompt"].lower()
        assert "beginner" in call_kwargs.kwargs["prompt"].lower()

    def test_routine_invalid_goal_rejected(self, runner):
        """Test that invalid goals are rejected."""
        result = runner.invoke(cli, ["routine", "--goal", "speed"])
        assert result.exit_code != 0


class TestConstants:
    """Tests for application constants and configuration."""

    def test_valid_levels(self):
        """Test that all expected levels are defined."""
        assert "beginner" in VALID_LEVELS
        assert "intermediate" in VALID_LEVELS
        assert "advanced" in VALID_LEVELS

    def test_valid_muscle_groups(self):
        """Test that common muscle groups are defined."""
        for group in ["legs", "chest", "back", "shoulders", "arms", "core"]:
            assert group in VALID_MUSCLE_GROUPS

    def test_valid_goals(self):
        """Test that training goals are defined."""
        for goal in ["strength", "hypertrophy", "endurance", "flexibility"]:
            assert goal in VALID_GOALS
