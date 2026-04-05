"""Tests for Smart Calendar Assistant."""

import json
import os
import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner

from app import main, load_schedule, display_schedule, optimize_schedule, suggest_meeting_time, analyze_workload


SAMPLE_EVENTS = [
    {"date": "2024-03-25", "time": "09:00", "title": "Team Standup", "duration": "30 min", "priority": "high"},
    {"date": "2024-03-25", "time": "10:00", "title": "Code Review", "duration": "60 min", "priority": "medium"},
    {"date": "2024-03-25", "time": "14:00", "title": "Sprint Planning", "duration": "90 min", "priority": "high"},
]


@pytest.fixture
def sample_schedule_file(tmp_path):
    """Create a temporary schedule JSON file."""
    schedule_file = tmp_path / "calendar.json"
    schedule_file.write_text(json.dumps({"events": SAMPLE_EVENTS}))
    return str(schedule_file)


@pytest.fixture
def runner():
    """Create a CLI test runner."""
    return CliRunner()


def test_load_schedule_valid(sample_schedule_file):
    """Test loading a valid schedule file."""
    events = load_schedule(sample_schedule_file)
    assert len(events) == 3
    assert events[0]["title"] == "Team Standup"


def test_load_schedule_list_format(tmp_path):
    """Test loading a schedule file with list format."""
    schedule_file = tmp_path / "calendar.json"
    schedule_file.write_text(json.dumps(SAMPLE_EVENTS))
    events = load_schedule(str(schedule_file))
    assert len(events) == 3


def test_load_schedule_file_not_found():
    """Test loading a non-existent file."""
    with pytest.raises(SystemExit):
        load_schedule("nonexistent.json")


@patch('app.generate')
def test_optimize_schedule(mock_generate):
    """Test schedule optimization with mocked LLM."""
    mock_generate.return_value = "## Optimization\n- Move Code Review to 11 AM\n- Add 15-min breaks"
    result = optimize_schedule(SAMPLE_EVENTS)
    assert "Optimization" in result
    mock_generate.assert_called_once()
    call_kwargs = mock_generate.call_args
    assert "optimize" in call_kwargs.kwargs.get("prompt", call_kwargs[1].get("prompt", "")).lower() or \
           "schedule" in call_kwargs.kwargs.get("prompt", call_kwargs[1].get("prompt", "")).lower()


@patch('app.generate')
def test_suggest_meeting_time(mock_generate):
    """Test meeting time suggestion with mocked LLM."""
    mock_generate.return_value = "Best slot: March 25, 11:30 AM - 12:30 PM"
    result = suggest_meeting_time(SAMPLE_EVENTS, "60 minutes", "engineering team")
    assert "March 25" in result or "slot" in result.lower()
    mock_generate.assert_called_once()


@patch('app.check_ollama_running', return_value=True)
@patch('app.generate', return_value="## Workload\n- Daily hours: 3.5\n- Balance: 7/10")
def test_cli_view_schedule(mock_generate, mock_check, runner, sample_schedule_file):
    """Test CLI view command."""
    result = runner.invoke(main, ['--schedule', sample_schedule_file, '--view'])
    assert result.exit_code == 0
    assert "Team Standup" in result.output


@patch('app.check_ollama_running', return_value=False)
def test_cli_ollama_not_running(mock_check, runner, sample_schedule_file):
    """Test CLI when Ollama is not running."""
    result = runner.invoke(main, ['--schedule', sample_schedule_file, '--optimize'])
    assert result.exit_code != 0
