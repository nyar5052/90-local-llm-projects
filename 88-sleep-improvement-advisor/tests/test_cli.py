"""Tests for Sleep Improvement Advisor CLI commands."""

import os
import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner

from sleep_advisor.cli import cli


SAMPLE_CSV_CONTENT = """date,bedtime,waketime,quality_rating,notes
2024-01-01,23:00,07:00,4,Felt rested
2024-01-02,23:30,06:30,3,Woke up once during night
2024-01-03,00:00,07:30,2,Trouble falling asleep
2024-01-04,22:30,06:00,5,Great sleep
2024-01-05,23:15,06:45,3,Restless
"""


def _write_csv(directory, filename, content):
    """Write CSV content to a file and return the path."""
    path = os.path.join(directory, filename)
    with open(path, "w", newline="", encoding="utf-8") as f:
        f.write(content)
    return path


@pytest.fixture
def runner():
    """Create a Click CLI test runner."""
    return CliRunner()


@pytest.fixture
def mock_ollama_running():
    """Mock check_ollama_running to return True."""
    with patch("sleep_advisor.cli.check_ollama_running", return_value=True) as mock:
        yield mock


@pytest.fixture
def mock_generate():
    """Mock the generate function with a sample response."""
    sample_response = (
        "## Sleep Analysis\n\n"
        "### Pattern Analysis\n"
        "Your average sleep duration is 7.5 hours.\n\n"
        "### Recommendations\n"
        "1. Maintain a consistent bedtime\n"
        "2. Reduce screen time before bed\n\n"
        "### When to Seek Help\n"
        "Consult a healthcare provider if problems persist.\n"
    )
    with patch("sleep_advisor.cli.generate", return_value=sample_response) as mock:
        yield mock


@pytest.fixture
def mock_chat():
    """Mock the chat function with a sample response."""
    sample_response = (
        "## Sleep Assessment Results\n\n"
        "Based on your responses, here are recommendations...\n"
    )
    with patch("sleep_advisor.cli.chat", return_value=sample_response) as mock:
        yield mock


class TestAnalyzeCommand:
    """Tests for the 'analyze' CLI command."""

    def test_analyze_with_valid_csv(self, runner, tmp_path, mock_ollama_running, mock_generate):
        """Test analyze command with a valid CSV file."""
        path = _write_csv(tmp_path, "log.csv", SAMPLE_CSV_CONTENT)
        result = runner.invoke(cli, ["analyze", "--log", path])
        assert result.exit_code == 0
        mock_generate.assert_called_once()

    def test_analyze_nonexistent_file(self, runner):
        """Test analyze command with a nonexistent file."""
        result = runner.invoke(cli, ["analyze", "--log", "no_such_file.csv"])
        assert result.exit_code != 0

    def test_analyze_requires_log(self, runner):
        """Test that analyze command requires --log option."""
        result = runner.invoke(cli, ["analyze"])
        assert result.exit_code != 0


class TestTipsCommand:
    """Tests for the 'tips' CLI command."""

    def test_tips_generates_advice(self, runner, mock_ollama_running, mock_generate):
        """Test that tips command generates sleep advice."""
        result = runner.invoke(cli, ["tips", "--issue", "difficulty falling asleep"])
        assert result.exit_code == 0
        mock_generate.assert_called_once()
        call_kwargs = mock_generate.call_args
        assert "difficulty falling asleep" in call_kwargs.kwargs["prompt"].lower()

    def test_tips_requires_issue_option(self, runner):
        """Test that tips command requires --issue option."""
        result = runner.invoke(cli, ["tips"])
        assert result.exit_code != 0

    def test_tips_ollama_not_running(self, runner):
        """Test error handling when Ollama is not running."""
        with patch("sleep_advisor.cli.check_ollama_running", return_value=False):
            result = runner.invoke(cli, ["tips", "--issue", "insomnia"])
            assert result.exit_code != 0


class TestAssessCommand:
    """Tests for the 'assess' CLI command."""

    def test_assess_interactive_flow(self, runner, mock_ollama_running, mock_chat):
        """Test interactive assessment with simulated user input."""
        input_lines = "\n".join([
            "11:00 PM",
            "7:00 AM",
            "15",
            "1",
            "3",
            "Yes, until 2 PM",
            "Yes, 30 min",
            "Yes, mornings",
            "Dark, cool room",
            "Sometimes restless",
        ])
        result = runner.invoke(cli, ["assess"], input=input_lines)
        assert result.exit_code == 0
        mock_chat.assert_called_once()


class TestScoreCommand:
    """Tests for the 'score' CLI command."""

    def test_score_with_valid_csv(self, runner, tmp_path):
        """Test score command with a valid CSV file."""
        path = _write_csv(tmp_path, "log.csv", SAMPLE_CSV_CONTENT)
        result = runner.invoke(cli, ["score", "--log", path])
        assert result.exit_code == 0
        assert "Sleep Score" in result.output

    def test_score_requires_log(self, runner):
        """Test that score command requires --log option."""
        result = runner.invoke(cli, ["score"])
        assert result.exit_code != 0

    def test_score_nonexistent_file(self, runner):
        """Test score command with a nonexistent file."""
        result = runner.invoke(cli, ["score", "--log", "no_such_file.csv"])
        assert result.exit_code != 0


class TestChecklistCommand:
    """Tests for the 'checklist' CLI command."""

    def test_checklist_displays(self, runner):
        """Test that checklist command displays items."""
        result = runner.invoke(cli, ["checklist"])
        assert result.exit_code == 0
        assert "Environment Checklist" in result.output


class TestRoutineCommand:
    """Tests for the 'routine' CLI command."""

    def test_routine_with_valid_time(self, runner):
        """Test routine command with a valid wake time."""
        result = runner.invoke(cli, ["routine", "--wake-time", "07:00"])
        assert result.exit_code == 0
        assert "Bedtime Routine" in result.output

    def test_routine_with_duration(self, runner):
        """Test routine command with custom duration."""
        result = runner.invoke(cli, ["routine", "--wake-time", "06:30", "--duration", "7.0"])
        assert result.exit_code == 0

    def test_routine_requires_wake_time(self, runner):
        """Test that routine command requires --wake-time."""
        result = runner.invoke(cli, ["routine"])
        assert result.exit_code != 0

    def test_routine_invalid_time_format(self, runner):
        """Test routine command with invalid time format."""
        result = runner.invoke(cli, ["routine", "--wake-time", "not-a-time"])
        assert result.exit_code != 0


class TestPatternsCommand:
    """Tests for the 'patterns' CLI command."""

    def test_patterns_with_valid_csv(self, runner, tmp_path):
        """Test patterns command with a valid CSV file."""
        path = _write_csv(tmp_path, "log.csv", SAMPLE_CSV_CONTENT)
        result = runner.invoke(cli, ["patterns", "--log", path])
        assert result.exit_code == 0
        assert "Pattern" in result.output

    def test_patterns_requires_log(self, runner):
        """Test that patterns command requires --log option."""
        result = runner.invoke(cli, ["patterns"])
        assert result.exit_code != 0

    def test_patterns_nonexistent_file(self, runner):
        """Test patterns command with a nonexistent file."""
        result = runner.invoke(cli, ["patterns", "--log", "no_such_file.csv"])
        assert result.exit_code != 0
