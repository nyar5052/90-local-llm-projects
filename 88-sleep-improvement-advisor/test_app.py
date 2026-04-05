"""Tests for Sleep Improvement Advisor application."""

import os
import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner
from app import cli, parse_sleep_log, compute_sleep_stats


SAMPLE_CSV_CONTENT = """date,bedtime,waketime,quality_rating,notes
2024-01-01,23:00,07:00,4,Felt rested
2024-01-02,23:30,06:30,3,Woke up once during night
2024-01-03,00:00,07:30,2,Trouble falling asleep
2024-01-04,22:30,06:00,5,Great sleep
2024-01-05,23:15,06:45,3,Restless
"""


@pytest.fixture
def runner():
    """Create a Click CLI test runner."""
    return CliRunner()


@pytest.fixture
def sample_csv(runner):
    """Create a temporary sample CSV file using CliRunner's isolated filesystem."""
    with runner.isolated_filesystem() as td:
        csv_path = os.path.join(td, "test_sleep_log.csv")
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            f.write(SAMPLE_CSV_CONTENT)
        yield csv_path


@pytest.fixture
def mock_ollama_running():
    """Mock check_ollama_running to return True."""
    with patch("app.check_ollama_running", return_value=True) as mock:
        yield mock


@pytest.fixture
def mock_generate():
    """Mock the generate function with a sample sleep analysis response."""
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
    with patch("app.generate", return_value=sample_response) as mock:
        yield mock


@pytest.fixture
def mock_chat():
    """Mock the chat function with a sample assessment response."""
    sample_response = (
        "## Sleep Assessment Results\n\n"
        "Based on your responses, here are recommendations...\n"
    )
    with patch("app.chat", return_value=sample_response) as mock:
        yield mock


class TestCSVParsing:
    """Tests for sleep log CSV parsing."""

    def test_parse_valid_csv(self, sample_csv):
        """Test parsing a valid sleep log CSV file."""
        entries = parse_sleep_log(sample_csv)
        assert len(entries) == 5
        assert entries[0]["date"] == "2024-01-01"
        assert entries[0]["bedtime"] == "23:00"
        assert entries[0]["waketime"] == "07:00"
        assert entries[0]["quality_rating"] == "4"
        assert entries[0]["notes"] == "Felt rested"

    def test_parse_nonexistent_file_raises_error(self):
        """Test that parsing a nonexistent file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError, match="not found"):
            parse_sleep_log("nonexistent_file.csv")

    def test_parse_csv_missing_columns(self, runner):
        """Test that CSV with missing required columns raises ValueError."""
        with runner.isolated_filesystem() as td:
            bad_csv = os.path.join(td, "bad.csv")
            with open(bad_csv, "w") as f:
                f.write("date,notes\n2024-01-01,test\n")
            with pytest.raises(ValueError, match="missing required columns"):
                parse_sleep_log(bad_csv)

    def test_compute_sleep_stats(self, sample_csv):
        """Test computing statistics from parsed sleep entries."""
        entries = parse_sleep_log(sample_csv)
        stats = compute_sleep_stats(entries)

        assert stats["total_entries"] == 5
        assert stats["avg_duration"] is not None
        assert 7.0 <= stats["avg_duration"] <= 8.0
        assert stats["avg_quality"] is not None
        assert 3.0 <= stats["avg_quality"] <= 4.0
        assert stats["min_quality"] == 2.0
        assert stats["max_quality"] == 5.0


class TestTipsCommand:
    """Tests for the 'tips' command."""

    def test_tips_generates_advice(self, runner, mock_ollama_running, mock_generate):
        """Test that tips command generates sleep advice for an issue."""
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
        with patch("app.check_ollama_running", return_value=False):
            result = runner.invoke(cli, ["tips", "--issue", "insomnia"])
            assert result.exit_code != 0


class TestAnalyzeCommand:
    """Tests for the 'analyze' command."""

    def test_analyze_with_valid_csv(self, runner, sample_csv, mock_ollama_running, mock_generate):
        """Test analyze command with a valid CSV file."""
        result = runner.invoke(cli, ["analyze", "--log", sample_csv])
        assert result.exit_code == 0
        mock_generate.assert_called_once()

    def test_analyze_nonexistent_file(self, runner):
        """Test analyze command with a nonexistent file."""
        result = runner.invoke(cli, ["analyze", "--log", "no_such_file.csv"])
        assert result.exit_code != 0


class TestAssessCommand:
    """Tests for the 'assess' command."""

    def test_assess_interactive_flow(self, runner, mock_ollama_running, mock_chat):
        """Test interactive assessment with simulated user input."""
        input_lines = "\n".join([
            "11:00 PM",   # bedtime
            "7:00 AM",    # waketime
            "15",         # fall_asleep_time
            "1",          # wake_during_night
            "3",          # sleep_quality
            "Yes, until 2 PM",  # caffeine
            "Yes, 30 min",      # screen_time
            "Yes, mornings",    # exercise
            "Dark, cool room",  # environment
            "Sometimes restless",  # concerns
        ])
        result = runner.invoke(cli, ["assess"], input=input_lines)
        assert result.exit_code == 0
        mock_chat.assert_called_once()
