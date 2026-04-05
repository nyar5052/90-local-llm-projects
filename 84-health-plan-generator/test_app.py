"""Tests for the Health Plan Generator application."""

import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner

from app import cli, generate_plan, _build_prompt


MOCK_PLAN = """## Overview
A 1-month plan focused on improving sleep quality.

## Diet Suggestions
- Avoid caffeine after 2 PM.
- Eat lighter meals in the evening.

## Exercise Plan
- 30 minutes of moderate activity daily.
- Avoid vigorous exercise close to bedtime.

## Sleep Recommendations
- Maintain a consistent sleep schedule.
- Create a dark, cool sleeping environment.

## Stress Management
- Practice deep breathing before bed.
- Limit screen time 1 hour before sleep.

## Sample Weekly Schedule
| Day | Morning | Afternoon | Evening |
|-----|---------|-----------|---------|
| Mon | Walk 30min | Work | Wind-down routine |
| Tue | Yoga 20min | Work | Reading |
| Wed | Walk 30min | Work | Meditation |
| Thu | Yoga 20min | Work | Wind-down routine |
| Fri | Walk 30min | Work | Light stretching |
| Sat | Outdoor activity | Free time | Early dinner |
| Sun | Rest | Meal prep | Wind-down routine |

⚠️ Consult a healthcare professional before starting any new program.
"""


@pytest.fixture
def runner():
    """Create a Click CLI test runner."""
    return CliRunner()


class TestBuildPrompt:
    """Tests for prompt construction."""

    def test_prompt_contains_goal(self):
        prompt = _build_prompt("better sleep", None, None, None)
        assert "better sleep" in prompt

    def test_prompt_contains_age(self):
        prompt = _build_prompt("lose weight", 30, None, None)
        assert "30" in prompt

    def test_prompt_contains_lifestyle(self):
        prompt = _build_prompt("gain muscle", None, "active", None)
        assert "active" in prompt

    def test_prompt_contains_duration(self):
        prompt = _build_prompt("better sleep", None, None, "1month")
        assert "1 month" in prompt


class TestGeneratePlan:
    """Tests for the generate_plan function."""

    @patch("app.generate")
    def test_generate_plan_returns_response(self, mock_generate):
        """Test that generate_plan returns the LLM response."""
        mock_generate.return_value = MOCK_PLAN
        result = generate_plan("better sleep")
        assert result == MOCK_PLAN
        mock_generate.assert_called_once()

    @patch("app.generate")
    def test_generate_plan_with_all_params(self, mock_generate):
        """Test generate_plan passes all parameters correctly."""
        mock_generate.return_value = MOCK_PLAN
        result = generate_plan("lose weight", age=30, lifestyle="sedentary", duration="3months")
        assert result == MOCK_PLAN
        call_kwargs = mock_generate.call_args
        prompt = call_kwargs.kwargs.get("prompt", str(call_kwargs))
        assert "lose weight" in prompt


class TestGenerateCommand:
    """Tests for the 'generate' CLI command."""

    @patch("app.check_ollama_running", return_value=True)
    @patch("app.generate", return_value=MOCK_PLAN)
    def test_generate_basic(self, mock_generate, mock_check, runner):
        """Test basic plan generation via CLI."""
        result = runner.invoke(cli, ["generate", "--goal", "better sleep"])
        assert result.exit_code == 0
        assert "better sleep" in result.output.lower() or "Wellness Plan" in result.output

    @patch("app.check_ollama_running", return_value=True)
    @patch("app.generate", return_value=MOCK_PLAN)
    def test_generate_with_all_options(self, mock_generate, mock_check, runner):
        """Test plan generation with all CLI options."""
        result = runner.invoke(cli, [
            "generate",
            "--goal", "lose weight",
            "--age", "30",
            "--lifestyle", "sedentary",
            "--duration", "1month",
        ])
        assert result.exit_code == 0

    @patch("app.check_ollama_running", return_value=False)
    def test_generate_ollama_not_running(self, mock_check, runner):
        """Test error when Ollama is not running."""
        result = runner.invoke(cli, ["generate", "--goal", "better sleep"])
        assert result.exit_code != 0
        assert "Ollama" in result.output

    @patch("app.check_ollama_running", return_value=True)
    @patch("app.generate", return_value=MOCK_PLAN)
    def test_generate_with_different_lifestyles(self, mock_generate, mock_check, runner):
        """Test generation with different lifestyle options."""
        for lifestyle in ["sedentary", "moderate", "active"]:
            result = runner.invoke(cli, [
                "generate", "--goal", "get fit", "--lifestyle", lifestyle,
            ])
            assert result.exit_code == 0


class TestInteractiveCommand:
    """Tests for the 'interactive' CLI command."""

    @patch("app.check_ollama_running", return_value=False)
    def test_interactive_ollama_not_running(self, mock_check, runner):
        """Test interactive mode error when Ollama is not running."""
        result = runner.invoke(cli, ["interactive"])
        assert result.exit_code != 0
        assert "Ollama" in result.output

    @patch("app.check_ollama_running", return_value=True)
    @patch("app.generate", return_value=MOCK_PLAN)
    def test_interactive_with_inputs(self, mock_generate, mock_check, runner):
        """Test interactive mode with user inputs."""
        result = runner.invoke(
            cli,
            ["interactive"],
            input="better sleep\n25\nmoderate\n1month\n",
        )
        assert result.exit_code == 0
        mock_generate.assert_called_once()
