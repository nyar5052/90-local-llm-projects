#!/usr/bin/env python3
"""Tests for calendar_assistant.core module."""

import sys
import os
import json
import tempfile
from datetime import datetime
from unittest.mock import patch, MagicMock

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from calendar_assistant.core import (
    load_schedule,
    display_schedule,
    optimize_schedule,
    suggest_meeting_time,
    analyze_workload,
    detect_conflicts,
    score_priority,
    generate_daily_agenda,
    convert_timezone,
    load_config,
    _parse_dt,
    DEFAULT_CONFIG,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

SAMPLE_EVENTS = [
    {
        "title": "Team Standup",
        "start": "2025-01-15T09:00",
        "end": "2025-01-15T09:30",
        "priority": "high",
        "attendees": ["Alice", "Bob", "Carol"],
    },
    {
        "title": "Design Review",
        "start": "2025-01-15T10:00",
        "end": "2025-01-15T11:00",
        "priority": "medium",
        "attendees": ["Alice", "Dave"],
    },
    {
        "title": "Lunch",
        "start": "2025-01-15T12:00",
        "end": "2025-01-15T13:00",
        "priority": "low",
    },
    {
        "title": "Sprint Planning",
        "start": "2025-01-15T14:00",
        "end": "2025-01-15T15:30",
        "priority": "critical",
        "attendees": ["Alice", "Bob", "Carol", "Dave", "Eve"],
    },
]

CONFLICTING_EVENTS = [
    {"title": "Meeting A", "start": "2025-01-15T09:00", "end": "2025-01-15T10:00", "priority": "high"},
    {"title": "Meeting B", "start": "2025-01-15T09:30", "end": "2025-01-15T10:30", "priority": "medium"},
    {"title": "Meeting C", "start": "2025-01-15T11:00", "end": "2025-01-15T12:00", "priority": "low"},
]


@pytest.fixture
def sample_events():
    return [dict(e) for e in SAMPLE_EVENTS]


@pytest.fixture
def conflicting_events():
    return [dict(e) for e in CONFLICTING_EVENTS]


@pytest.fixture
def schedule_file(sample_events):
    """Write sample events to a temp JSON file and yield its path."""
    path = os.path.join(os.path.dirname(__file__), "_test_schedule.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(sample_events, fh)
    yield path
    if os.path.exists(path):
        os.remove(path)


# ---------------------------------------------------------------------------
# load_schedule
# ---------------------------------------------------------------------------

class TestLoadSchedule:
    def test_load_valid_file(self, schedule_file, sample_events):
        result = load_schedule(schedule_file)
        assert len(result) == len(sample_events)
        assert result[0]["title"] == "Team Standup"

    def test_load_missing_file(self):
        result = load_schedule("nonexistent.json")
        assert result == []

    def test_load_invalid_json(self):
        path = os.path.join(os.path.dirname(__file__), "_bad.json")
        with open(path, "w") as fh:
            fh.write("{bad json")
        try:
            result = load_schedule(path)
            assert result == []
        finally:
            os.remove(path)

    def test_load_non_array_json(self):
        path = os.path.join(os.path.dirname(__file__), "_obj.json")
        with open(path, "w") as fh:
            json.dump({"not": "a list"}, fh)
        try:
            result = load_schedule(path)
            assert result == []
        finally:
            os.remove(path)


# ---------------------------------------------------------------------------
# display_schedule
# ---------------------------------------------------------------------------

class TestDisplaySchedule:
    def test_empty(self):
        assert display_schedule([]) == "No events in schedule."

    def test_formatting(self, sample_events):
        text = display_schedule(sample_events)
        assert "Team Standup" in text
        assert "[HIGH]" in text
        assert "→" in text


# ---------------------------------------------------------------------------
# detect_conflicts
# ---------------------------------------------------------------------------

class TestDetectConflicts:
    def test_no_conflicts(self, sample_events):
        conflicts = detect_conflicts(sample_events)
        assert conflicts == []

    def test_detects_overlap(self, conflicting_events):
        conflicts = detect_conflicts(conflicting_events)
        assert len(conflicts) == 1
        titles = {conflicts[0][0]["title"], conflicts[0][1]["title"]}
        assert titles == {"Meeting A", "Meeting B"}

    def test_no_events(self):
        assert detect_conflicts([]) == []

    def test_custom_timezone(self, conflicting_events):
        conflicts = detect_conflicts(conflicting_events, timezone="US/Eastern")
        assert len(conflicts) == 1

    def test_skips_bad_events(self):
        events = [
            {"title": "OK", "start": "2025-01-15T09:00", "end": "2025-01-15T10:00"},
            {"title": "Bad"},  # missing start/end
        ]
        conflicts = detect_conflicts(events)
        assert conflicts == []


# ---------------------------------------------------------------------------
# score_priority
# ---------------------------------------------------------------------------

class TestScorePriority:
    def test_critical_high(self):
        ev = {"title": "X", "start": "2025-01-15T09:00", "end": "2025-01-15T10:00", "priority": "critical", "attendees": ["a", "b", "c"]}
        score = score_priority(ev)
        assert score >= 5  # base 5 + attendees + duration

    def test_optional_low(self):
        ev = {"title": "Y", "start": "2025-01-15T09:00", "end": "2025-01-15T09:15", "priority": "optional"}
        score = score_priority(ev)
        assert score <= 3

    def test_default_medium(self):
        ev = {"title": "Z", "start": "2025-01-15T09:00", "end": "2025-01-15T09:30"}
        score = score_priority(ev)
        assert score >= 3  # medium = 3 base

    def test_attendee_string(self):
        ev = {"title": "A", "start": "2025-01-15T09:00", "end": "2025-01-15T10:00", "priority": "medium", "attendees": "alice, bob"}
        score = score_priority(ev)
        assert score >= 3

    def test_missing_times(self):
        ev = {"title": "No times", "priority": "high"}
        score = score_priority(ev)
        assert score == 4  # base only, no duration bonus


# ---------------------------------------------------------------------------
# generate_daily_agenda
# ---------------------------------------------------------------------------

class TestGenerateDailyAgenda:
    def test_filters_by_date(self, sample_events):
        agenda = generate_daily_agenda(sample_events, date="2025-01-15")
        assert len(agenda) == len(sample_events)

    def test_wrong_date_empty(self, sample_events):
        agenda = generate_daily_agenda(sample_events, date="2025-12-25")
        assert agenda == []

    def test_sorted_by_start(self, sample_events):
        agenda = generate_daily_agenda(sample_events, date="2025-01-15")
        starts = [e["start"] for e in agenda]
        assert starts == sorted(starts)

    def test_has_priority_score(self, sample_events):
        agenda = generate_daily_agenda(sample_events, date="2025-01-15")
        for item in agenda:
            assert "priority_score" in item
            assert isinstance(item["priority_score"], int)

    def test_empty_events(self):
        assert generate_daily_agenda([], date="2025-01-15") == []


# ---------------------------------------------------------------------------
# convert_timezone
# ---------------------------------------------------------------------------

class TestConvertTimezone:
    def test_utc_to_eastern(self):
        events = [{"title": "E", "start": "2025-06-15T14:00", "end": "2025-06-15T15:00"}]
        converted = convert_timezone(events, "UTC", "US/Eastern")
        assert len(converted) == 1
        assert converted[0]["timezone"] == "US/Eastern"
        assert "10:00" in converted[0]["start"]  # UTC-4 in summer

    def test_skips_bad_event(self):
        events = [{"title": "Bad"}]
        assert convert_timezone(events, "UTC", "US/Eastern") == []


# ---------------------------------------------------------------------------
# _parse_dt
# ---------------------------------------------------------------------------

class TestParseDt:
    def test_iso_format(self):
        dt = _parse_dt("2025-01-15T09:30:00")
        assert dt.hour == 9
        assert dt.minute == 30

    def test_short_format(self):
        dt = _parse_dt("2025-01-15T09:30")
        assert dt.year == 2025

    def test_space_format(self):
        dt = _parse_dt("2025-01-15 09:30")
        assert dt.month == 1

    def test_invalid_raises(self):
        with pytest.raises(ValueError):
            _parse_dt("not-a-date")


# ---------------------------------------------------------------------------
# LLM-powered functions (mocked)
# ---------------------------------------------------------------------------

class TestLLMFunctions:
    @patch("calendar_assistant.core.generate", return_value="Optimized schedule here")
    def test_optimize_schedule(self, mock_gen, sample_events):
        result = optimize_schedule(sample_events)
        assert "Optimized schedule here" in result
        mock_gen.assert_called_once()

    @patch("calendar_assistant.core.generate", return_value="Suggested time: 3pm")
    def test_suggest_meeting_time(self, mock_gen, sample_events):
        result = suggest_meeting_time(sample_events, 45, "Alice, Bob")
        assert "3pm" in result
        mock_gen.assert_called_once()

    @patch("calendar_assistant.core.generate", return_value="Workload is balanced")
    def test_analyze_workload(self, mock_gen, sample_events):
        result = analyze_workload(sample_events)
        assert "balanced" in result
        mock_gen.assert_called_once()

    def test_optimize_empty(self):
        assert optimize_schedule([]) == "No events to optimize."

    def test_analyze_empty(self):
        assert analyze_workload([]) == "No events to analyze."


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

class TestConfig:
    def test_default_config_structure(self):
        assert "app" in DEFAULT_CONFIG
        assert "calendar" in DEFAULT_CONFIG
        assert "llm" in DEFAULT_CONFIG

    def test_load_missing_config(self):
        cfg = load_config("nonexistent_path_xyz.yaml")
        assert cfg == DEFAULT_CONFIG

    def test_load_valid_config(self):
        path = os.path.join(os.path.dirname(__file__), "_test_config.yaml")
        import yaml
        with open(path, "w") as fh:
            yaml.dump({"app": {"name": "TestApp"}, "calendar": {}, "llm": {}}, fh)
        try:
            cfg = load_config(path)
            assert cfg["app"]["name"] == "TestApp"
        finally:
            os.remove(path)
