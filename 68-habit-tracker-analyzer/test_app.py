"""Tests for Habit Tracker Analyzer."""

import json
import os
import pytest
from datetime import datetime, timedelta
from unittest.mock import patch
from click.testing import CliRunner

from app import cli, log_habit, load_habits, compute_streaks, get_completion_rate, analyze_habits


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture(autouse=True)
def mock_habits_file(tmp_path, monkeypatch):
    """Use a temporary habits file for tests."""
    habits_path = str(tmp_path / "habits.json")
    monkeypatch.setattr('app.HABITS_FILE', habits_path)
    return habits_path


def test_log_habit():
    """Test logging a habit."""
    entry = log_habit("exercise", True, "30 min run")
    assert entry["habit"] == "exercise"
    assert entry["done"] is True
    assert entry["notes"] == "30 min run"

    data = load_habits()
    assert "exercise" in data["habits"]
    assert len(data["logs"]) == 1


def test_log_multiple_habits():
    """Test logging multiple different habits."""
    log_habit("exercise", True)
    log_habit("reading", True)
    log_habit("meditation", False)

    data = load_habits()
    assert len(data["habits"]) == 3
    assert len(data["logs"]) == 3


def test_compute_streaks():
    """Test streak computation."""
    data = load_habits()
    today = datetime.now().strftime("%Y-%m-%d")
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    data["habits"]["exercise"] = {"name": "exercise", "created": yesterday}
    data["logs"] = [
        {"habit": "exercise", "date": yesterday, "done": True},
        {"habit": "exercise", "date": today, "done": True},
    ]

    from app import save_habits
    save_habits(data)

    streaks = compute_streaks(data)
    assert streaks["exercise"]["current"] == 2
    assert streaks["exercise"]["total"] == 2


def test_completion_rate():
    """Test completion rate calculation."""
    log_habit("exercise", True)
    log_habit("exercise", True)

    data = load_habits()
    rates = get_completion_rate(data, 30)
    assert "exercise" in rates
    assert rates["exercise"]["done"] == 2


@patch('app.generate')
def test_analyze_habits(mock_generate):
    """Test AI habit analysis with mocked LLM."""
    log_habit("exercise", True)
    log_habit("reading", True)

    data = load_habits()
    mock_generate.return_value = "## Analysis\n- Exercise: Good consistency\n- Reading: Just started"
    result = analyze_habits(data, "month")
    assert "Analysis" in result
    mock_generate.assert_called_once()


def test_cli_log(runner):
    """Test CLI log command."""
    result = runner.invoke(cli, ['log', '--habit', 'exercise', '--done'])
    assert result.exit_code == 0
    assert "Done" in result.output


def test_cli_status_empty(runner):
    """Test CLI status with no habits."""
    result = runner.invoke(cli, ['status'])
    assert result.exit_code == 0
    assert "No habits" in result.output
