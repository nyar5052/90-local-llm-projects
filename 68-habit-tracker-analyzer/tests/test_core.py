"""Tests for Habit Tracker Analyzer core module."""

import json
import os
import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from src.habit_tracker.core import (
    load_habits,
    save_habits,
    log_habit,
    add_habit,
    delete_habit,
    compute_streaks,
    get_completion_rate,
    compute_correlations,
    check_achievements,
    analyze_habits,
    get_calendar_data,
    ACHIEVEMENTS,
)


@pytest.fixture(autouse=True)
def habits_file(tmp_path):
    """Provide a temporary habits file for each test."""
    return str(tmp_path / "habits.json")


# ---------------------------------------------------------------------------
# log_habit
# ---------------------------------------------------------------------------


def test_log_habit(habits_file):
    """Test logging a single habit."""
    entry = log_habit("exercise", True, "30 min run", habits_file=habits_file)
    assert entry["habit"] == "exercise"
    assert entry["done"] is True
    assert entry["notes"] == "30 min run"

    data = load_habits(habits_file)
    assert "exercise" in data["habits"]
    assert len(data["logs"]) == 1


def test_log_multiple_habits(habits_file):
    """Test logging multiple different habits."""
    log_habit("exercise", True, habits_file=habits_file)
    log_habit("reading", True, habits_file=habits_file)
    log_habit("meditation", False, habits_file=habits_file)

    data = load_habits(habits_file)
    assert len(data["habits"]) == 3
    assert len(data["logs"]) == 3


# ---------------------------------------------------------------------------
# add_habit / delete_habit
# ---------------------------------------------------------------------------


def test_add_habit(habits_file):
    """Test adding a new habit definition."""
    habit = add_habit("Running", category="fitness", target="daily", habits_file=habits_file)
    assert habit["name"] == "Running"
    assert habit["category"] == "fitness"
    assert habit["target"] == "daily"

    data = load_habits(habits_file)
    assert "running" in data["habits"]


def test_delete_habit(habits_file):
    """Test deleting a habit."""
    log_habit("exercise", True, habits_file=habits_file)
    assert delete_habit("exercise", habits_file=habits_file) is True

    data = load_habits(habits_file)
    assert "exercise" not in data["habits"]
    assert all(l["habit"] != "exercise" for l in data["logs"])


def test_delete_nonexistent_habit(habits_file):
    """Deleting a missing habit returns False."""
    assert delete_habit("nonexistent", habits_file=habits_file) is False


# ---------------------------------------------------------------------------
# compute_streaks
# ---------------------------------------------------------------------------


def test_compute_streaks(habits_file):
    """Test streak computation with consecutive dates."""
    today = datetime.now().strftime("%Y-%m-%d")
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    data = {
        "habits": {"exercise": {"name": "exercise", "created": yesterday, "target": "daily", "category": "fitness"}},
        "logs": [
            {"habit": "exercise", "date": yesterday, "done": True},
            {"habit": "exercise", "date": today, "done": True},
        ],
    }
    save_habits(data, habits_file)

    streaks = compute_streaks(data)
    assert streaks["exercise"]["current"] == 2
    assert streaks["exercise"]["best"] == 2
    assert streaks["exercise"]["total"] == 2


def test_compute_streaks_with_gap(habits_file):
    """Test streak resets after a gap."""
    today = datetime.now()
    dates = [
        (today - timedelta(days=5)).strftime("%Y-%m-%d"),
        (today - timedelta(days=4)).strftime("%Y-%m-%d"),
        # gap on day 3
        (today - timedelta(days=1)).strftime("%Y-%m-%d"),
        today.strftime("%Y-%m-%d"),
    ]

    data = {
        "habits": {"run": {"name": "run", "created": dates[0], "target": "daily", "category": "fitness"}},
        "logs": [{"habit": "run", "date": d, "done": True} for d in dates],
    }

    streaks = compute_streaks(data)
    assert streaks["run"]["current"] == 2
    assert streaks["run"]["best"] == 2


# ---------------------------------------------------------------------------
# get_completion_rate
# ---------------------------------------------------------------------------


def test_completion_rate(habits_file):
    """Test completion rate calculation."""
    log_habit("exercise", True, habits_file=habits_file)
    log_habit("exercise", True, habits_file=habits_file)

    data = load_habits(habits_file)
    rates = get_completion_rate(data, 30)
    assert "exercise" in rates
    assert rates["exercise"]["done"] == 2
    assert rates["exercise"]["rate"] > 0


# ---------------------------------------------------------------------------
# compute_correlations
# ---------------------------------------------------------------------------


def test_compute_correlations(habits_file):
    """Test correlation between habits done on the same day."""
    today = datetime.now().strftime("%Y-%m-%d")
    data = {
        "habits": {
            "exercise": {"name": "exercise", "created": today, "target": "daily", "category": "fitness"},
            "reading": {"name": "reading", "created": today, "target": "daily", "category": "learning"},
        },
        "logs": [
            {"habit": "exercise", "date": today, "done": True},
            {"habit": "reading", "date": today, "done": True},
        ],
    }
    save_habits(data, habits_file)

    corr = compute_correlations(data)
    assert len(corr) == 1
    pair = list(corr.values())[0]
    assert pair["co_occurrence"] == 1
    assert pair["rate"] == 100.0


def test_compute_correlations_single_habit(habits_file):
    """Correlations need at least 2 habits."""
    data = {
        "habits": {"exercise": {"name": "exercise", "created": "2024-01-01", "target": "daily", "category": "fitness"}},
        "logs": [{"habit": "exercise", "date": "2024-01-01", "done": True}],
    }
    assert compute_correlations(data) == {}


# ---------------------------------------------------------------------------
# check_achievements
# ---------------------------------------------------------------------------


def test_check_achievements_first_log(habits_file):
    """Logging one habit earns the 'first_log' achievement."""
    log_habit("exercise", True, habits_file=habits_file)
    data = load_habits(habits_file)

    earned = check_achievements(data)
    ids = {a["id"] for a in earned}
    assert "first_log" in ids


def test_check_achievements_no_logs(habits_file):
    """No achievements with empty data."""
    data = {"habits": {}, "logs": []}
    earned = check_achievements(data)
    assert earned == []


# ---------------------------------------------------------------------------
# analyze_habits (mocked LLM)
# ---------------------------------------------------------------------------


@patch("src.habit_tracker.core.generate")
def test_analyze_habits(mock_generate, habits_file):
    """Test AI habit analysis with mocked LLM."""
    log_habit("exercise", True, habits_file=habits_file)
    log_habit("reading", True, habits_file=habits_file)

    data = load_habits(habits_file)
    mock_generate.return_value = "## Analysis\n- Exercise: Good consistency\n- Reading: Just started"

    result = analyze_habits(data, "month")
    assert "Analysis" in result
    mock_generate.assert_called_once()


# ---------------------------------------------------------------------------
# get_calendar_data
# ---------------------------------------------------------------------------


def test_get_calendar_data(habits_file):
    """Test calendar heatmap data generation."""
    today = datetime.now().strftime("%Y-%m-%d")
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    data = {
        "habits": {"exercise": {"name": "exercise", "created": yesterday, "target": "daily", "category": "fitness"}},
        "logs": [
            {"habit": "exercise", "date": yesterday, "done": True},
            {"habit": "exercise", "date": today, "done": True},
        ],
    }

    cal = get_calendar_data(data, "exercise", months=1)
    assert cal[today] is True
    assert cal[yesterday] is True
    # A date with no log should be False
    two_days_ago = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")
    assert cal.get(two_days_ago) is False


def test_get_calendar_data_missing_habit(habits_file):
    """Calendar data for non-existent habit returns all False."""
    data = {"habits": {"x": {"name": "x", "created": "2024-01-01", "target": "daily", "category": "general"}}, "logs": []}
    cal = get_calendar_data(data, "x", months=1)
    assert all(v is False for v in cal.values())
