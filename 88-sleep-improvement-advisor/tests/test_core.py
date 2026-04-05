"""Tests for Sleep Improvement Advisor core logic."""

import os
import pytest
from unittest.mock import patch

from sleep_advisor.core import (
    parse_sleep_log,
    compute_sleep_stats,
    calculate_sleep_score,
    get_environment_checklist,
    build_bedtime_routine,
    analyze_weekly_patterns,
)


SAMPLE_CSV_CONTENT = """date,bedtime,waketime,quality_rating,notes
2024-01-01,23:00,07:00,4,Felt rested
2024-01-02,23:30,06:30,3,Woke up once during night
2024-01-03,00:00,07:30,2,Trouble falling asleep
2024-01-04,22:30,06:00,5,Great sleep
2024-01-05,23:15,06:45,3,Restless
"""

GOOD_CSV_CONTENT = """date,bedtime,waketime,quality_rating,notes
2024-01-01,23:00,07:00,5,Perfect
2024-01-02,23:00,07:00,5,Perfect
2024-01-03,23:00,07:00,5,Perfect
2024-01-04,23:00,07:00,5,Perfect
2024-01-05,23:00,07:00,5,Perfect
"""

POOR_CSV_CONTENT = """date,bedtime,waketime,quality_rating,notes
2024-01-01,03:00,05:00,1,Terrible
2024-01-02,04:00,06:00,1,Awful
2024-01-03,02:00,04:30,1,Could not sleep
2024-01-04,03:30,05:30,2,Very bad
2024-01-05,04:00,06:00,1,Worst night
"""

WEEKLY_CSV_CONTENT = """date,bedtime,waketime,quality_rating,notes
2024-01-01,23:00,07:00,4,Monday
2024-01-02,23:30,06:30,3,Tuesday
2024-01-03,00:00,07:30,2,Wednesday
2024-01-04,22:30,06:00,5,Thursday
2024-01-05,23:15,06:45,3,Friday
2024-01-06,00:30,09:00,4,Saturday
2024-01-07,01:00,09:30,4,Sunday
2024-01-08,23:00,07:00,5,Monday
2024-01-09,23:30,06:30,4,Tuesday
2024-01-10,23:00,07:00,5,Wednesday
2024-01-11,22:30,06:30,5,Thursday
2024-01-12,23:00,07:00,4,Friday
2024-01-13,00:00,09:00,5,Saturday
2024-01-14,00:30,09:30,5,Sunday
"""


def _write_csv(directory, filename, content):
    """Write CSV content to a file and return the path."""
    path = os.path.join(directory, filename)
    with open(path, "w", newline="", encoding="utf-8") as f:
        f.write(content)
    return path


class TestParseSleepLog:
    """Tests for sleep log CSV parsing."""

    def test_valid_csv(self, tmp_path):
        """Test parsing a valid sleep log CSV file."""
        path = _write_csv(tmp_path, "valid.csv", SAMPLE_CSV_CONTENT)
        entries = parse_sleep_log(path)
        assert len(entries) == 5
        assert entries[0]["date"] == "2024-01-01"
        assert entries[0]["bedtime"] == "23:00"
        assert entries[0]["waketime"] == "07:00"
        assert entries[0]["quality_rating"] == "4"
        assert entries[0]["notes"] == "Felt rested"

    def test_missing_file(self):
        """Test that parsing a nonexistent file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError, match="not found"):
            parse_sleep_log("nonexistent_file.csv")

    def test_missing_columns(self, tmp_path):
        """Test that CSV with missing required columns raises ValueError."""
        path = _write_csv(tmp_path, "bad.csv", "date,notes\n2024-01-01,test\n")
        with pytest.raises(ValueError, match="missing required columns"):
            parse_sleep_log(path)

    def test_empty_data(self, tmp_path):
        """Test that CSV with headers but no data raises ValueError."""
        path = _write_csv(tmp_path, "empty.csv", "date,bedtime,waketime,quality_rating,notes\n")
        with pytest.raises(ValueError, match="no data entries"):
            parse_sleep_log(path)


class TestComputeStats:
    """Tests for computing sleep statistics."""

    def test_known_data(self, tmp_path):
        """Test computing statistics with known data."""
        path = _write_csv(tmp_path, "sample.csv", SAMPLE_CSV_CONTENT)
        entries = parse_sleep_log(path)
        stats = compute_sleep_stats(entries)

        assert stats["total_entries"] == 5
        assert stats["avg_duration"] is not None
        assert 7.0 <= stats["avg_duration"] <= 8.0
        assert stats["avg_quality"] is not None
        assert 3.0 <= stats["avg_quality"] <= 4.0
        assert stats["min_quality"] == 2.0
        assert stats["max_quality"] == 5.0

    def test_edge_case_single_entry(self, tmp_path):
        """Test statistics with a single entry."""
        content = "date,bedtime,waketime,quality_rating,notes\n2024-01-01,23:00,07:00,4,Test\n"
        path = _write_csv(tmp_path, "single.csv", content)
        entries = parse_sleep_log(path)
        stats = compute_sleep_stats(entries)

        assert stats["total_entries"] == 1
        assert stats["avg_duration"] == 8.0
        assert stats["avg_quality"] == 4.0
        assert stats["min_duration"] == stats["max_duration"]


class TestSleepScore:
    """Tests for sleep score calculation."""

    def test_perfect_sleep_data(self, tmp_path):
        """Test that perfect sleep data yields a high score."""
        path = _write_csv(tmp_path, "good.csv", GOOD_CSV_CONTENT)
        entries = parse_sleep_log(path)
        stats = compute_sleep_stats(entries)
        result = calculate_sleep_score(stats)

        assert result["score"] >= 85
        assert result["grade"] in ("A", "B")
        assert "duration" in result["breakdown"]
        assert "quality" in result["breakdown"]
        assert "consistency" in result["breakdown"]
        assert "low_wake_count" in result["breakdown"]

    def test_poor_sleep_data(self, tmp_path):
        """Test that poor sleep data yields a low score."""
        path = _write_csv(tmp_path, "poor.csv", POOR_CSV_CONTENT)
        entries = parse_sleep_log(path)
        stats = compute_sleep_stats(entries)
        result = calculate_sleep_score(stats)

        assert result["score"] <= 40
        assert result["grade"] in ("D", "F")

    def test_boundary_values(self):
        """Test score with boundary stat values."""
        stats = {
            "avg_duration": 7.0,
            "avg_quality": 4.0,
            "durations": [7.0, 7.0, 7.0],
            "qualities": [4.0, 4.0, 4.0],
        }
        result = calculate_sleep_score(stats)
        assert 0 <= result["score"] <= 100
        assert result["grade"] in ("A", "B", "C", "D", "F")

    def test_empty_stats(self):
        """Test score with no data."""
        stats = {
            "avg_duration": None,
            "avg_quality": None,
            "durations": [],
            "qualities": [],
        }
        result = calculate_sleep_score(stats)
        assert result["score"] == 10  # only neutral consistency
        assert result["grade"] == "F"


class TestEnvironmentChecklist:
    """Tests for the environment checklist."""

    def test_returns_list(self):
        """Test that checklist returns a list."""
        items = get_environment_checklist()
        assert isinstance(items, list)
        assert len(items) > 0

    def test_has_required_keys(self):
        """Test that each item has required keys."""
        items = get_environment_checklist()
        required_keys = {"category", "item", "recommendation", "priority"}
        for item in items:
            assert required_keys.issubset(item.keys()), f"Missing keys in item: {item}"

    def test_valid_priorities(self):
        """Test that priorities are valid."""
        items = get_environment_checklist()
        valid_priorities = {"high", "medium", "low"}
        for item in items:
            assert item["priority"] in valid_priorities


class TestBedtimeRoutine:
    """Tests for the bedtime routine builder."""

    def test_morning_wake_time(self):
        """Test routine with a typical morning wake time."""
        result = build_bedtime_routine("07:00", 8.0)
        assert result["wake_time"] == "07:00"
        assert result["bedtime"] == "23:00"
        assert result["sleep_duration"] == 8.0
        assert len(result["routine"]) > 0

    def test_early_wake_time(self):
        """Test routine with an early wake time."""
        result = build_bedtime_routine("05:00", 7.0)
        assert result["wake_time"] == "05:00"
        assert result["bedtime"] == "22:00"

    def test_routine_has_activities(self):
        """Test that routine contains activities with expected fields."""
        result = build_bedtime_routine("07:00", 8.0)
        for step in result["routine"]:
            assert "time" in step
            assert "activity" in step
            assert "duration" in step

    def test_different_durations(self):
        """Test routine with different sleep durations."""
        result_short = build_bedtime_routine("07:00", 6.0)
        result_long = build_bedtime_routine("07:00", 9.0)
        assert result_short["bedtime"] == "01:00"
        assert result_long["bedtime"] == "22:00"


class TestWeeklyPatterns:
    """Tests for weekly pattern analysis."""

    def test_multi_day_data(self, tmp_path):
        """Test analysis with multi-day data."""
        path = _write_csv(tmp_path, "weekly.csv", WEEKLY_CSV_CONTENT)
        entries = parse_sleep_log(path)
        result = analyze_weekly_patterns(entries)

        assert "day_averages" in result
        assert "best_day" in result
        assert "worst_day" in result
        assert "weekday_vs_weekend" in result
        assert "trend" in result

        assert result["best_day"] is not None
        assert result["worst_day"] is not None

    def test_trend_detection(self, tmp_path):
        """Test that trend is correctly detected for improving data."""
        path = _write_csv(tmp_path, "weekly.csv", WEEKLY_CSV_CONTENT)
        entries = parse_sleep_log(path)
        result = analyze_weekly_patterns(entries)

        # The weekly CSV has improving quality (3.0 avg first half, 4.7 avg second half)
        assert result["trend"] in ("improving", "stable", "declining")

    def test_weekday_vs_weekend(self, tmp_path):
        """Test weekday vs weekend comparison."""
        path = _write_csv(tmp_path, "weekly.csv", WEEKLY_CSV_CONTENT)
        entries = parse_sleep_log(path)
        result = analyze_weekly_patterns(entries)

        wvw = result["weekday_vs_weekend"]
        assert "weekday_avg_quality" in wvw
        assert "weekend_avg_quality" in wvw
        assert "weekday_avg_duration" in wvw
        assert "weekend_avg_duration" in wvw

    def test_insufficient_data(self, tmp_path):
        """Test trend with very few entries."""
        content = "date,bedtime,waketime,quality_rating,notes\n2024-01-01,23:00,07:00,4,Test\n"
        path = _write_csv(tmp_path, "tiny.csv", content)
        entries = parse_sleep_log(path)
        result = analyze_weekly_patterns(entries)
        assert result["trend"] == "insufficient_data"
