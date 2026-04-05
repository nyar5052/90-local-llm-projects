"""Tests for Time Management Coach."""

import csv
import json
import os
import pytest
from unittest.mock import patch
from click.testing import CliRunner

from app import (
    cli, load_timelog, compute_time_breakdown, compute_daily_totals,
    analyze_time_usage, get_tips
)


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def sample_timelog(tmp_path):
    """Create a sample time log CSV file."""
    csv_file = tmp_path / "timelog.csv"
    with open(csv_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["date", "category", "activity", "duration"])
        writer.writeheader()
        writer.writerow({"date": "2024-03-25", "category": "Deep Work", "activity": "Coding feature X", "duration": "3.0"})
        writer.writerow({"date": "2024-03-25", "category": "Meetings", "activity": "Sprint planning", "duration": "1.5"})
        writer.writerow({"date": "2024-03-25", "category": "Email", "activity": "Inbox processing", "duration": "1.0"})
        writer.writerow({"date": "2024-03-25", "category": "Deep Work", "activity": "Code review", "duration": "2.0"})
        writer.writerow({"date": "2024-03-26", "category": "Meetings", "activity": "Team sync", "duration": "0.5"})
        writer.writerow({"date": "2024-03-26", "category": "Deep Work", "activity": "Bug fixing", "duration": "4.0"})
    return str(csv_file)


def test_load_timelog(sample_timelog):
    """Test loading time log from CSV."""
    entries = load_timelog(sample_timelog)
    assert len(entries) == 6
    assert entries[0]["category"] == "Deep Work"


def test_compute_time_breakdown(sample_timelog):
    """Test time breakdown computation."""
    entries = load_timelog(sample_timelog)
    breakdown = compute_time_breakdown(entries)
    assert "Deep Work" in breakdown
    assert breakdown["Deep Work"] == pytest.approx(9.0)
    assert "Meetings" in breakdown
    assert breakdown["Meetings"] == pytest.approx(2.0)


def test_compute_daily_totals(sample_timelog):
    """Test daily totals computation."""
    entries = load_timelog(sample_timelog)
    daily = compute_daily_totals(entries)
    assert "2024-03-25" in daily
    assert daily["2024-03-25"] == pytest.approx(7.5)
    assert daily["2024-03-26"] == pytest.approx(4.5)


@patch('app.generate')
def test_analyze_time_usage(mock_generate):
    """Test AI time analysis with mocked LLM."""
    breakdown = {"Deep Work": 9.0, "Meetings": 2.0, "Email": 1.0}
    daily = {"2024-03-25": 7.5, "2024-03-26": 4.5}
    entries = [{"category": "Deep Work", "duration": "3.0"}]

    mock_generate.return_value = "## Analysis\n- Productivity Score: 8/10\n- 75% deep work is excellent"
    result = analyze_time_usage(entries, breakdown, daily)
    assert "Analysis" in result or "Productivity" in result
    mock_generate.assert_called_once()


@patch('app.generate')
def test_get_tips(mock_generate):
    """Test getting AI tips for a goal."""
    mock_generate.return_value = "## Deep Work Tips\n1. Block 3-hour morning sessions\n2. Eliminate distractions"
    result = get_tips("deep work")
    assert "Deep Work" in result or "Block" in result
    mock_generate.assert_called_once()


@patch('app.check_ollama_running', return_value=True)
@patch('app.generate', return_value="## Tips\n- Focus deeply")
def test_cli_tips(mock_generate, mock_check, runner):
    """Test CLI tips command."""
    result = runner.invoke(cli, ['tips', '--goal', 'deep work'])
    assert result.exit_code == 0


@patch('app.check_ollama_running', return_value=True)
@patch('app.generate', return_value="## Analysis\nGood time usage")
def test_cli_review(mock_generate, mock_check, runner, sample_timelog):
    """Test CLI review command."""
    result = runner.invoke(cli, ['review', '--log', sample_timelog, '--analyze'])
    assert result.exit_code == 0
    assert "Deep Work" in result.output
