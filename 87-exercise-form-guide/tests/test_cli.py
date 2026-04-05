"""Tests for Exercise Form Guide CLI commands."""

import pytest
from unittest.mock import patch
from click.testing import CliRunner

from exercise_guide.cli import cli


@pytest.fixture
def runner():
    """Create a Click CLI test runner."""
    return CliRunner()


@pytest.fixture
def mock_ollama_running():
    """Mock check_ollama_running to return True."""
    with patch("exercise_guide.cli.check_ollama_running", return_value=True) as mock:
        yield mock


@pytest.fixture
def mock_generate():
    """Mock the LLM generate function with a sample response."""
    sample = "## Sample Response\n\nThis is a test response from the LLM."
    with patch("exercise_guide.core.generate", return_value=sample) as mock:
        yield mock


# ---------------------------------------------------------------------------
# Guide Command
# ---------------------------------------------------------------------------


class TestGuideCommand:
    """Tests for the 'guide' CLI command."""

    def test_guide_success(self, runner, mock_ollama_running, mock_generate):
        result = runner.invoke(cli, ["guide", "--exercise", "deadlift", "--level", "beginner"])
        assert result.exit_code == 0
        mock_generate.assert_called_once()

    def test_guide_default_level(self, runner, mock_ollama_running, mock_generate):
        result = runner.invoke(cli, ["guide", "--exercise", "squat"])
        assert result.exit_code == 0
        call_kwargs = mock_generate.call_args
        assert "beginner" in call_kwargs.kwargs["prompt"].lower()

    def test_guide_requires_exercise(self, runner):
        result = runner.invoke(cli, ["guide"])
        assert result.exit_code != 0

    def test_guide_invalid_level(self, runner):
        result = runner.invoke(cli, ["guide", "--exercise", "squat", "--level", "expert"])
        assert result.exit_code != 0

    def test_guide_ollama_not_running(self, runner):
        with patch("exercise_guide.cli.check_ollama_running", return_value=False):
            result = runner.invoke(cli, ["guide", "--exercise", "deadlift"])
            assert result.exit_code != 0


# ---------------------------------------------------------------------------
# List Command
# ---------------------------------------------------------------------------


class TestListCommand:
    """Tests for the 'list' CLI command."""

    def test_list_success(self, runner, mock_ollama_running, mock_generate):
        result = runner.invoke(cli, ["list", "--muscle-group", "legs"])
        assert result.exit_code == 0
        mock_generate.assert_called_once()

    def test_list_invalid_muscle_group(self, runner):
        result = runner.invoke(cli, ["list", "--muscle-group", "fingers"])
        assert result.exit_code != 0


# ---------------------------------------------------------------------------
# Routine Command
# ---------------------------------------------------------------------------


class TestRoutineCommand:
    """Tests for the 'routine' CLI command."""

    def test_routine_success(self, runner, mock_ollama_running, mock_generate):
        result = runner.invoke(cli, ["routine", "--goal", "strength", "--level", "beginner"])
        assert result.exit_code == 0
        mock_generate.assert_called_once()

    def test_routine_invalid_goal(self, runner):
        result = runner.invoke(cli, ["routine", "--goal", "speed"])
        assert result.exit_code != 0


# ---------------------------------------------------------------------------
# Warmup Command
# ---------------------------------------------------------------------------


class TestWarmupCommand:
    """Tests for the 'warmup' CLI command."""

    def test_warmup_success(self, runner):
        result = runner.invoke(cli, ["warmup", "--muscle-group", "chest"])
        assert result.exit_code == 0
        assert "Warm-up" in result.output or "warm-up" in result.output.lower()

    def test_warmup_invalid_group(self, runner):
        result = runner.invoke(cli, ["warmup", "--muscle-group", "fingers"])
        assert result.exit_code != 0


# ---------------------------------------------------------------------------
# Cooldown Command
# ---------------------------------------------------------------------------


class TestCooldownCommand:
    """Tests for the 'cooldown' CLI command."""

    def test_cooldown_success(self, runner):
        result = runner.invoke(cli, ["cooldown", "--muscle-group", "legs"])
        assert result.exit_code == 0
        assert "Cool-down" in result.output or "cool-down" in result.output.lower()

    def test_cooldown_invalid_group(self, runner):
        result = runner.invoke(cli, ["cooldown", "--muscle-group", "fingers"])
        assert result.exit_code != 0


# ---------------------------------------------------------------------------
# Progression Command
# ---------------------------------------------------------------------------


class TestProgressionCommand:
    """Tests for the 'progression' CLI command."""

    def test_progression_success(self, runner):
        result = runner.invoke(cli, ["progression", "--exercise", "push-up"])
        assert result.exit_code == 0
        assert "Step" in result.output or "Progression" in result.output

    def test_progression_invalid_exercise(self, runner):
        result = runner.invoke(cli, ["progression", "--exercise", "backflip"])
        assert result.exit_code != 0


# ---------------------------------------------------------------------------
# Muscles Command
# ---------------------------------------------------------------------------


class TestMusclesCommand:
    """Tests for the 'muscles' CLI command."""

    def test_muscles_success(self, runner):
        result = runner.invoke(cli, ["muscles", "--group", "chest"])
        assert result.exit_code == 0
        assert "pectoralis" in result.output.lower() or "Chest" in result.output

    def test_muscles_invalid_group(self, runner):
        result = runner.invoke(cli, ["muscles", "--group", "fingers"])
        assert result.exit_code != 0
