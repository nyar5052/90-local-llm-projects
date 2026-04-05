"""Tests for Mood Journal Bot."""

import pytest
import json
import os
from unittest.mock import patch, mock_open
from click.testing import CliRunner
from datetime import datetime

import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app import (
    load_entries,
    save_entries,
    add_entry,
    get_recent_entries,
    analyze_entries,
    cli,
    MOODS,
    SYSTEM_PROMPT,
    JOURNAL_FILE,
)


class TestConfiguration:
    """Tests for app configuration."""

    def test_moods_defined(self):
        assert len(MOODS) == 10

    def test_mood_has_emoji_name_color(self):
        for key, value in MOODS.items():
            assert len(value) == 3
            emoji, name, color = value
            assert len(emoji) > 0
            assert len(name) > 0
            assert len(color) > 0

    def test_system_prompt_is_empathetic(self):
        assert "empathetic" in SYSTEM_PROMPT.lower() or "supportive" in SYSTEM_PROMPT.lower()


class TestLoadEntries:
    """Tests for loading journal entries."""

    @patch("app.JOURNAL_FILE", "nonexistent_file.json")
    def test_returns_empty_for_missing_file(self):
        result = load_entries()
        assert result == []

    @patch("builtins.open", mock_open(read_data='[{"mood": "Happy"}]'))
    @patch("os.path.exists", return_value=True)
    def test_loads_valid_entries(self, mock_exists):
        result = load_entries()
        assert len(result) == 1
        assert result[0]["mood"] == "Happy"


class TestAddEntry:
    """Tests for adding journal entries."""

    @patch("app.save_entries")
    @patch("app.load_entries", return_value=[])
    def test_creates_entry(self, mock_load, mock_save):
        entry = add_entry("1", "Feeling great today!")
        assert entry["mood"] == "Happy"
        assert entry["text"] == "Feeling great today!"
        assert entry["mood_emoji"] == "😊"
        assert entry["id"] == 1
        mock_save.assert_called_once()

    @patch("app.save_entries")
    @patch("app.load_entries", return_value=[{"id": 1}])
    def test_increments_id(self, mock_load, mock_save):
        entry = add_entry("4", "Bad day", energy_level=3)
        assert entry["id"] == 2
        assert entry["energy_level"] == 3

    @patch("app.save_entries")
    @patch("app.load_entries", return_value=[])
    def test_entry_has_timestamp(self, mock_load, mock_save):
        entry = add_entry("3", "Test")
        assert "timestamp" in entry
        assert "date" in entry
        assert "time" in entry


class TestGetRecentEntries:
    """Tests for filtering recent entries."""

    @patch("app.load_entries")
    def test_filters_by_date(self, mock_load):
        now = datetime.now()
        mock_load.return_value = [
            {"timestamp": now.isoformat(), "mood": "Happy"},
            {"timestamp": "2020-01-01T00:00:00", "mood": "Sad"},
        ]
        result = get_recent_entries(7)
        assert len(result) == 1
        assert result[0]["mood"] == "Happy"


class TestAnalyzeEntries:
    """Tests for mood analysis."""

    def test_empty_entries(self):
        result = analyze_entries([])
        assert "no entries" in result.lower()

    @patch("app.chat")
    def test_analyzes_entries(self, mock_chat):
        mock_chat.return_value = "Your mood has been mostly positive..."
        entries = [
            {
                "date": "2024-01-01",
                "time": "10:00",
                "mood": "Happy",
                "mood_emoji": "😊",
                "energy_level": 8,
                "text": "Great day!",
            }
        ]
        result = analyze_entries(entries)
        assert "positive" in result.lower()
        mock_chat.assert_called_once()


class TestCLI:
    """Tests for CLI commands."""

    def test_journal_command_exists(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["journal", "--help"])
        assert result.exit_code == 0

    def test_analyze_command_exists(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "--help"])
        assert result.exit_code == 0

    def test_history_command_exists(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["history", "--help"])
        assert result.exit_code == 0

    def test_stats_command_exists(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["stats", "--help"])
        assert result.exit_code == 0
