"""Tests for Time Management Coach core module."""

import csv
import os
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

from src.time_coach.core import (
    load_timelog,
    save_time_entry,
    compute_time_breakdown,
    compute_daily_totals,
    compute_productivity_score,
    get_focus_time_stats,
    analyze_time_usage,
    get_tips,
    compute_trends,
    load_config,
    DEFAULT_CONFIG,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_csv(tmp_path):
    """Create a sample CSV time log."""
    csv_file = tmp_path / "timelog.csv"
    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["date", "category", "activity", "duration"])
        writer.writeheader()
        writer.writerow({"date": "2024-03-25", "category": "coding", "activity": "Feature X", "duration": "3.0"})
        writer.writerow({"date": "2024-03-25", "category": "meetings", "activity": "Sprint planning", "duration": "1.5"})
        writer.writerow({"date": "2024-03-25", "category": "email", "activity": "Inbox", "duration": "1.0"})
        writer.writerow({"date": "2024-03-25", "category": "coding", "activity": "Code review", "duration": "2.0"})
        writer.writerow({"date": "2024-03-26", "category": "meetings", "activity": "Team sync", "duration": "0.5"})
        writer.writerow({"date": "2024-03-26", "category": "coding", "activity": "Bug fixing", "duration": "4.0"})
        writer.writerow({"date": "2024-03-26", "category": "break", "activity": "Lunch", "duration": "1.0"})
    return str(csv_file)


@pytest.fixture
def sample_entries(sample_csv):
    return load_timelog(sample_csv)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestLoadTimelog:
    def test_loads_entries(self, sample_csv):
        entries = load_timelog(sample_csv)
        assert len(entries) == 7
        assert entries[0]["category"] == "coding"

    def test_missing_file_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            load_timelog(str(tmp_path / "nonexistent.csv"))


class TestComputeTimeBreakdown:
    def test_breakdown(self, sample_entries):
        breakdown = compute_time_breakdown(sample_entries)
        assert "coding" in breakdown
        assert breakdown["coding"] == pytest.approx(9.0)
        assert "meetings" in breakdown
        assert breakdown["meetings"] == pytest.approx(2.0)

    def test_sorted_descending(self, sample_entries):
        breakdown = compute_time_breakdown(sample_entries)
        values = list(breakdown.values())
        assert values == sorted(values, reverse=True)

    def test_empty_list(self):
        assert compute_time_breakdown([]) == {}


class TestComputeDailyTotals:
    def test_daily_totals(self, sample_entries):
        daily = compute_daily_totals(sample_entries)
        assert "2024-03-25" in daily
        assert daily["2024-03-25"] == pytest.approx(7.5)
        assert daily["2024-03-26"] == pytest.approx(5.5)

    def test_empty_list(self):
        assert compute_daily_totals([]) == {}


class TestComputeProductivityScore:
    def test_returns_required_keys(self, sample_entries):
        breakdown = compute_time_breakdown(sample_entries)
        result = compute_productivity_score(breakdown)
        assert "score" in result
        assert "factors" in result
        assert "suggestions" in result
        assert 1 <= result["score"] <= 10

    def test_high_deep_work(self):
        breakdown = {"coding": 5.0, "break": 1.5, "meetings": 1.5}
        result = compute_productivity_score(breakdown)
        assert result["score"] >= 5

    def test_no_deep_work(self):
        breakdown = {"meetings": 6.0, "email": 2.0}
        result = compute_productivity_score(breakdown)
        assert result["score"] < 5
        assert any("deep work" in s.lower() for s in result["suggestions"])


class TestGetFocusTimeStats:
    def test_focus_stats(self, sample_entries):
        stats = get_focus_time_stats(sample_entries)
        assert "deep_work_hours" in stats
        assert "total_hours" in stats
        assert "focus_ratio" in stats
        assert stats["deep_work_hours"] == pytest.approx(9.0)
        assert 0 <= stats["focus_ratio"] <= 1

    def test_empty_entries(self):
        stats = get_focus_time_stats([])
        assert stats["deep_work_hours"] == 0.0
        assert stats["focus_ratio"] == 0.0


class TestAnalyzeTimeUsage:
    @patch("src.time_coach.core.generate")
    def test_calls_llm(self, mock_generate, sample_entries):
        mock_generate.return_value = "## Analysis\n- Score: 8/10"
        breakdown = compute_time_breakdown(sample_entries)
        daily = compute_daily_totals(sample_entries)
        result = analyze_time_usage(sample_entries, breakdown, daily)
        assert "Analysis" in result
        mock_generate.assert_called_once()


class TestGetTips:
    @patch("src.time_coach.core.generate")
    def test_calls_llm(self, mock_generate):
        mock_generate.return_value = "## Tips\n1. Block deep-work sessions"
        result = get_tips("deep work")
        assert "Tips" in result
        mock_generate.assert_called_once()


class TestSaveTimeEntry:
    def test_creates_new_file(self, tmp_path):
        log_file = str(tmp_path / "new_log.csv")
        entry = {"date": "2024-04-01", "category": "coding", "activity": "Test", "duration": "2.0"}
        saved = save_time_entry(entry, log_file)
        assert saved["category"] == "coding"
        assert os.path.exists(log_file)
        loaded = load_timelog(log_file)
        assert len(loaded) == 1

    def test_appends_to_existing(self, sample_csv):
        entry = {"date": "2024-03-27", "category": "design", "activity": "Mockups", "duration": "1.5"}
        save_time_entry(entry, sample_csv)
        loaded = load_timelog(sample_csv)
        assert len(loaded) == 8
        assert loaded[-1]["category"] == "design"


class TestComputeTrends:
    def test_trends_structure(self, sample_entries):
        trends = compute_trends(sample_entries, weeks=4)
        assert isinstance(trends, dict)
        for week_label, bd in trends.items():
            assert isinstance(bd, dict)
            assert "-W" in week_label

    def test_empty_entries(self):
        assert compute_trends([]) == {}


class TestLoadConfig:
    def test_default_config(self):
        config = load_config(None)
        assert "llm" in config
        assert "pomodoro" in config

    def test_custom_config(self, tmp_path):
        cfg_file = tmp_path / "test_config.yaml"
        cfg_file.write_text("llm:\n  model: test-model\n")
        config = load_config(str(cfg_file))
        assert config["llm"]["model"] == "test-model"
        # Defaults preserved for other keys
        assert "pomodoro" in config
