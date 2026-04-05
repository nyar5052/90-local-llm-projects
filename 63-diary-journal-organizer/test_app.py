"""Tests for Diary Journal Organizer."""

import json
import os
import pytest
from datetime import datetime
from unittest.mock import patch
from click.testing import CliRunner

from app import cli, write_entry, load_diary, get_entries_for_period, analyze_mood, generate_insights


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture(autouse=True)
def mock_diary_file(tmp_path, monkeypatch):
    """Use a temporary diary file for tests."""
    diary_path = str(tmp_path / "diary.json")
    monkeypatch.setattr('app.DIARY_FILE', diary_path)
    return diary_path


def test_write_entry():
    """Test writing a diary entry."""
    entry = write_entry("Had a great day at the park", "happy", ["outdoors", "family"])
    assert entry["content"] == "Had a great day at the park"
    assert entry["mood"] == "happy"
    assert "outdoors" in entry["tags"]
    assert entry["id"] == 1

    diary = load_diary()
    assert len(diary["entries"]) == 1


def test_write_multiple_entries():
    """Test writing multiple entries."""
    write_entry("Morning jog", "energetic")
    write_entry("Work was stressful", "anxious")
    write_entry("Nice dinner with friends", "happy")

    diary = load_diary()
    assert len(diary["entries"]) == 3
    assert diary["entries"][0]["mood"] == "energetic"


def test_get_entries_for_period():
    """Test filtering entries by time period."""
    write_entry("Recent entry", "happy")
    entries = get_entries_for_period("week")
    assert len(entries) == 1

    entries = get_entries_for_period("month")
    assert len(entries) == 1


@patch('app.generate')
def test_analyze_mood(mock_generate):
    """Test mood analysis with mocked LLM."""
    entries = [
        {"date": "2024-03-25T10:00:00", "mood": "happy", "content": "Great day!"},
        {"date": "2024-03-26T10:00:00", "mood": "sad", "content": "Feeling down."},
    ]
    mock_generate.return_value = "## Mood Trend\n- Fluctuating between happy and sad"
    result = analyze_mood(entries)
    assert "Mood" in result or "happy" in result.lower() or "Fluctuating" in result
    mock_generate.assert_called_once()


@patch('app.generate')
def test_generate_insights(mock_generate):
    """Test comprehensive insights with mocked LLM."""
    entries = [
        {"date": "2024-03-25T10:00:00", "mood": "happy", "content": "Productive day", "tags": ["work"]},
    ]
    mock_generate.return_value = "## Summary\nA productive week with positive mood."
    result = generate_insights(entries)
    assert "Summary" in result
    mock_generate.assert_called_once()


def test_cli_write(runner):
    """Test CLI write command."""
    result = runner.invoke(cli, ['write', '--content', 'Test diary entry', '--mood', 'happy', '--tags', 'test'])
    assert result.exit_code == 0
    assert "saved" in result.output.lower()
