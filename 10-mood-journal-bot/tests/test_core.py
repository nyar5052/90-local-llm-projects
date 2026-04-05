"""Tests for Mood Journal Bot core logic."""

import pytest
import json
import os
from unittest.mock import patch, mock_open
from datetime import datetime

import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from mood_journal.core import (
    load_entries,
    save_entries,
    add_entry,
    get_recent_entries,
    analyze_entries,
    generate_weekly_report,
    get_mood_stats,
    MOODS,
    SYSTEM_PROMPT,
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


class TestAddEntry:
    """Tests for adding journal entries."""

    @patch("mood_journal.core.save_entries")
    @patch("mood_journal.core.load_entries", return_value=[])
    def test_creates_entry(self, mock_load, mock_save):
        entry = add_entry("1", "Feeling great today!")
        assert entry["mood"] == "Happy"
        assert entry["text"] == "Feeling great today!"
        assert entry["mood_emoji"] == "😊"
        assert entry["id"] == 1
        mock_save.assert_called_once()

    @patch("mood_journal.core.save_entries")
    @patch("mood_journal.core.load_entries", return_value=[{"id": 1}])
    def test_increments_id(self, mock_load, mock_save):
        entry = add_entry("4", "Bad day", energy_level=3)
        assert entry["id"] == 2
        assert entry["energy_level"] == 3

    @patch("mood_journal.core.save_entries")
    @patch("mood_journal.core.load_entries", return_value=[])
    def test_entry_has_timestamp(self, mock_load, mock_save):
        entry = add_entry("3", "Test")
        assert "timestamp" in entry
        assert "date" in entry
        assert "time" in entry

    @patch("mood_journal.core.save_entries")
    @patch("mood_journal.core.load_entries", return_value=[])
    def test_entry_with_gratitude(self, mock_load, mock_save):
        entry = add_entry("8", "Good day", gratitude="My family")
        assert entry["gratitude"] == "My family"
        assert entry["mood"] == "Grateful"


class TestGetRecentEntries:
    """Tests for filtering recent entries."""

    @patch("mood_journal.core.load_entries")
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

    @patch("mood_journal.core.chat")
    def test_analyzes_entries(self, mock_chat):
        mock_chat.return_value = "Your mood has been mostly positive..."
        entries = [
            {
                "date": "2024-01-01", "time": "10:00",
                "mood": "Happy", "mood_emoji": "😊",
                "energy_level": 8, "text": "Great day!",
            }
        ]
        result = analyze_entries(entries)
        assert "positive" in result.lower()
        mock_chat.assert_called_once()


class TestWeeklyReport:
    """Tests for weekly report."""

    def test_empty_entries(self):
        result = generate_weekly_report([])
        assert "no entries" in result.lower()

    def test_generates_report(self):
        entries = [
            {"date": "2024-01-01", "mood": "Happy", "energy_level": 8},
            {"date": "2024-01-02", "mood": "Calm", "energy_level": 7},
        ]
        result = generate_weekly_report(entries)
        assert "Weekly Report" in result
        assert "Happy" in result


class TestMoodStats:
    """Tests for mood statistics."""

    @patch("mood_journal.core.load_entries", return_value=[])
    def test_empty_stats(self, mock_load):
        stats = get_mood_stats()
        assert stats["total"] == 0

    @patch("mood_journal.core.load_entries", return_value=[
        {"mood": "Happy", "energy_level": 8, "date": "2024-01-01"},
        {"mood": "Happy", "energy_level": 7, "date": "2024-01-02"},
        {"mood": "Sad", "energy_level": 3, "date": "2024-01-03"},
    ])
    def test_calculates_stats(self, mock_load):
        stats = get_mood_stats()
        assert stats["total"] == 3
        assert stats["mood_counts"]["Happy"] == 2
        assert stats["mood_counts"]["Sad"] == 1
        assert stats["avg_energy"] == 6.0


class TestCLI:
    """Tests for CLI commands."""

    def test_journal_command_exists(self):
        from click.testing import CliRunner
        from mood_journal.cli import cli
        runner = CliRunner()
        result = runner.invoke(cli, ["journal", "--help"])
        assert result.exit_code == 0

    def test_analyze_command_exists(self):
        from click.testing import CliRunner
        from mood_journal.cli import cli
        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "--help"])
        assert result.exit_code == 0

    def test_history_command_exists(self):
        from click.testing import CliRunner
        from mood_journal.cli import cli
        runner = CliRunner()
        result = runner.invoke(cli, ["history", "--help"])
        assert result.exit_code == 0

    def test_stats_command_exists(self):
        from click.testing import CliRunner
        from mood_journal.cli import cli
        runner = CliRunner()
        result = runner.invoke(cli, ["stats", "--help"])
        assert result.exit_code == 0

    def test_export_command_exists(self):
        from click.testing import CliRunner
        from mood_journal.cli import cli
        runner = CliRunner()
        result = runner.invoke(cli, ["export", "--help"])
        assert result.exit_code == 0

    def test_gratitude_command_exists(self):
        from click.testing import CliRunner
        from mood_journal.cli import cli
        runner = CliRunner()
        result = runner.invoke(cli, ["gratitude", "--help"])
        assert result.exit_code == 0
