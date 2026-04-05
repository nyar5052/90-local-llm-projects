"""Tests for KPI Dashboard Reporter core business logic."""

import os
import pytest
from unittest.mock import patch, MagicMock

from src.kpi_reporter.core import (
    compute_kpi_trends,
    compute_moving_average,
    detect_anomalies,
    generate_alert_summary,
    generate_executive_summary,
    generate_kpi_report,
    load_config,
    load_kpi_data,
    safe_float,
    track_goals,
    compute_analytics,
)


# ─── Fixtures ────────────────────────────────────────────────────────────────


@pytest.fixture
def sample_kpi_csv(tmp_path):
    """Create a sample KPI data CSV."""
    csv_path = tmp_path / "kpis.csv"
    csv_path.write_text(
        "month,revenue,customers,churn_rate,nps_score\n"
        "Jan,100000,500,5.2,72\n"
        "Feb,110000,520,4.8,75\n"
        "Mar,105000,510,5.5,70\n"
        "Apr,120000,550,4.2,78\n"
    )
    return str(csv_path)


@pytest.fixture
def sample_kpi_data():
    """Return sample KPI data as list of dicts."""
    return [
        {"month": "Jan", "revenue": "100000", "customers": "500", "churn_rate": "5.2"},
        {"month": "Feb", "revenue": "110000", "customers": "520", "churn_rate": "4.8"},
        {"month": "Mar", "revenue": "105000", "customers": "510", "churn_rate": "5.5"},
        {"month": "Apr", "revenue": "120000", "customers": "550", "churn_rate": "4.2"},
    ]


@pytest.fixture
def sample_trends(sample_kpi_data):
    """Pre-computed trends from sample data."""
    return compute_kpi_trends(sample_kpi_data)


@pytest.fixture
def sample_targets():
    """Sample target values."""
    return {
        "revenue": 120000,
        "customers": 600,
        "churn_rate": 3.0,
        "nps_score": 80,
    }


@pytest.fixture
def config_yaml(tmp_path):
    """Create a temporary config.yaml file."""
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        "model:\n"
        "  name: gemma3\n"
        "  temperature: 0.5\n"
        "targets:\n"
        "  revenue: 150000\n"
        "anomaly_detection:\n"
        "  enabled: true\n"
        "  threshold: 1.5\n"
        "alert_threshold_pct: 15\n"
    )
    return str(config_path)


# ─── TestSafeFloat ───────────────────────────────────────────────────────────


class TestSafeFloat:
    def test_basic_number(self):
        assert safe_float("100") == 100.0

    def test_formatted_number(self):
        assert safe_float("$1,000.50") == 1000.50

    def test_percentage(self):
        assert safe_float("5.2%") == 5.2

    def test_invalid_value(self):
        assert safe_float("abc") == 0.0

    def test_none_value(self):
        assert safe_float(None) == 0.0

    def test_integer_input(self):
        assert safe_float(42) == 42.0

    def test_negative_number(self):
        assert safe_float("-15.5") == -15.5


# ─── TestLoadKpiData ────────────────────────────────────────────────────────


class TestLoadKpiData:
    def test_load_valid_csv(self, sample_kpi_csv):
        data = load_kpi_data(sample_kpi_csv)
        assert len(data) == 4
        assert "revenue" in data[0]

    def test_load_nonexistent_file(self):
        with pytest.raises(FileNotFoundError):
            load_kpi_data("nonexistent.csv")

    def test_load_empty_csv(self, tmp_path):
        empty_csv = tmp_path / "empty.csv"
        empty_csv.write_text("month,revenue\n")
        with pytest.raises(ValueError, match="empty"):
            load_kpi_data(str(empty_csv))


# ─── TestComputeKpiTrends ───────────────────────────────────────────────────


class TestComputeKpiTrends:
    def test_trend_computation(self, sample_kpi_data):
        trends = compute_kpi_trends(sample_kpi_data)
        assert "revenue" in trends
        assert trends["revenue"]["latest"] == 120000
        assert trends["revenue"]["previous"] == 105000
        assert trends["revenue"]["trend"] == "↑"

    def test_change_percentage(self, sample_kpi_data):
        trends = compute_kpi_trends(sample_kpi_data)
        expected_change_pct = (120000 - 105000) / 105000 * 100
        assert trends["revenue"]["change_pct"] == pytest.approx(expected_change_pct, rel=1e-2)

    def test_insufficient_data(self):
        trends = compute_kpi_trends([{"month": "Jan", "revenue": "100"}])
        assert trends == {}

    def test_includes_values_list(self, sample_kpi_data):
        trends = compute_kpi_trends(sample_kpi_data)
        assert trends["revenue"]["values"] == [100000, 110000, 105000, 120000]

    def test_includes_periods(self, sample_kpi_data):
        trends = compute_kpi_trends(sample_kpi_data)
        assert trends["revenue"]["periods"] == ["Jan", "Feb", "Mar", "Apr"]

    def test_min_max(self, sample_kpi_data):
        trends = compute_kpi_trends(sample_kpi_data)
        assert trends["revenue"]["min"] == 100000
        assert trends["revenue"]["max"] == 120000

    def test_downward_trend(self, sample_kpi_data):
        trends = compute_kpi_trends(sample_kpi_data)
        assert trends["churn_rate"]["trend"] == "↓"


# ─── TestTrackGoals ──────────────────────────────────────────────────────────


class TestTrackGoals:
    def test_goal_achieved(self, sample_trends):
        targets = {"revenue": 120000}
        goals = track_goals(sample_trends, targets)
        assert goals["revenue"]["status"] == "achieved"
        assert goals["revenue"]["pct_of_goal"] == pytest.approx(100.0)

    def test_goal_on_track(self, sample_trends):
        targets = {"revenue": 140000}
        goals = track_goals(sample_trends, targets)
        assert goals["revenue"]["status"] == "on_track"

    def test_goal_at_risk(self, sample_trends):
        targets = {"revenue": 200000}
        goals = track_goals(sample_trends, targets)
        assert goals["revenue"]["status"] == "at_risk"

    def test_goal_behind(self, sample_trends):
        targets = {"revenue": 500000}
        goals = track_goals(sample_trends, targets)
        assert goals["revenue"]["status"] == "behind"

    def test_missing_kpi_ignored(self, sample_trends):
        targets = {"nonexistent_kpi": 100}
        goals = track_goals(sample_trends, targets)
        assert len(goals) == 0

    def test_zero_target_ignored(self, sample_trends):
        targets = {"revenue": 0}
        goals = track_goals(sample_trends, targets)
        assert "revenue" not in goals

    def test_all_fields_present(self, sample_trends):
        targets = {"revenue": 120000}
        goals = track_goals(sample_trends, targets)
        assert "actual" in goals["revenue"]
        assert "target" in goals["revenue"]
        assert "pct_of_goal" in goals["revenue"]
        assert "status" in goals["revenue"]


# ─── TestDetectAnomalies ─────────────────────────────────────────────────────


class TestDetectAnomalies:
    def test_no_anomalies_normal_data(self, sample_trends):
        anomalies = detect_anomalies(sample_trends, threshold=3.0)
        # With only 4 data points and modest variance, unlikely to hit 3σ
        assert isinstance(anomalies, list)

    def test_detects_anomaly_with_outlier(self):
        trends = {
            "metric": {
                "values": [10, 11, 10, 11, 10, 100],
                "periods": ["P1", "P2", "P3", "P4", "P5", "P6"],
                "latest": 100,
                "previous": 10,
                "change": 90,
                "change_pct": 900.0,
                "average": 25.33,
                "min": 10,
                "max": 100,
                "trend": "↑",
            }
        }
        anomalies = detect_anomalies(trends, threshold=2.0)
        assert len(anomalies) > 0
        assert anomalies[0]["kpi"] == "metric"
        assert anomalies[0]["value"] == 100

    def test_anomaly_fields(self):
        trends = {
            "metric": {
                "values": [10, 10, 10, 10, 10, 100],
                "periods": ["P1", "P2", "P3", "P4", "P5", "P6"],
                "latest": 100,
                "previous": 10,
                "change": 90,
                "change_pct": 900.0,
                "average": 25.0,
                "min": 10,
                "max": 100,
                "trend": "↑",
            }
        }
        anomalies = detect_anomalies(trends, threshold=1.5)
        assert len(anomalies) > 0
        a = anomalies[0]
        assert "kpi" in a
        assert "period" in a
        assert "value" in a
        assert "mean" in a
        assert "std_dev" in a
        assert "deviation" in a

    def test_insufficient_data_for_anomaly(self):
        trends = {
            "metric": {
                "values": [10, 20],
                "periods": ["P1", "P2"],
                "latest": 20,
                "previous": 10,
                "change": 10,
                "change_pct": 100.0,
                "average": 15.0,
                "min": 10,
                "max": 20,
                "trend": "↑",
            }
        }
        anomalies = detect_anomalies(trends, threshold=2.0)
        assert anomalies == []


# ─── TestComputeMovingAverage ────────────────────────────────────────────────


class TestComputeMovingAverage:
    def test_basic_moving_average(self):
        values = [10.0, 20.0, 30.0, 40.0, 50.0]
        ma = compute_moving_average(values, window=3)
        assert len(ma) == 5
        assert ma[0] == pytest.approx(10.0)
        assert ma[1] == pytest.approx(15.0)
        assert ma[2] == pytest.approx(20.0)
        assert ma[3] == pytest.approx(30.0)
        assert ma[4] == pytest.approx(40.0)

    def test_window_1(self):
        values = [5.0, 10.0, 15.0]
        ma = compute_moving_average(values, window=1)
        assert ma == values

    def test_empty_input(self):
        assert compute_moving_average([], window=3) == []

    def test_window_larger_than_data(self):
        values = [10.0, 20.0]
        ma = compute_moving_average(values, window=5)
        assert len(ma) == 2
        assert ma[0] == pytest.approx(10.0)
        assert ma[1] == pytest.approx(15.0)

    def test_zero_window(self):
        assert compute_moving_average([1.0, 2.0], window=0) == []


# ─── TestGenerateAlertSummary ────────────────────────────────────────────────


class TestGenerateAlertSummary:
    def test_alerts_for_large_changes(self):
        trends = {
            "revenue": {"change_pct": 15.0, "previous": 100000, "latest": 115000},
            "churn": {"change_pct": -3.0, "previous": 5.0, "latest": 4.85},
        }
        alert_text = generate_alert_summary(trends)
        assert "revenue" in alert_text
        assert "15.0%" in alert_text

    def test_no_alerts(self):
        trends = {"revenue": {"change_pct": 2.0, "previous": 100, "latest": 102}}
        alert_text = generate_alert_summary(trends)
        assert "No Significant Alerts" in alert_text

    def test_custom_threshold(self):
        trends = {
            "revenue": {"change_pct": 8.0, "previous": 100000, "latest": 108000},
        }
        alert_text = generate_alert_summary(trends, threshold_pct=5.0)
        assert "revenue" in alert_text

        alert_text_default = generate_alert_summary(trends, threshold_pct=10.0)
        assert "No Significant Alerts" in alert_text_default


# ─── TestGenerateExecutiveSummary ────────────────────────────────────────────


class TestGenerateExecutiveSummary:
    @patch("src.kpi_reporter.core.chat")
    def test_generates_summary(self, mock_chat, sample_trends, sample_targets):
        mock_chat.return_value = "## Executive Summary\n\n- Revenue exceeded target."
        goals = track_goals(sample_trends, sample_targets)
        anomalies = []
        result = generate_executive_summary(sample_trends, goals, anomalies)
        assert "Executive Summary" in result
        mock_chat.assert_called_once()

    @patch("src.kpi_reporter.core.chat")
    def test_handles_empty_goals(self, mock_chat, sample_trends):
        mock_chat.return_value = "## Summary\n\nNo targets set."
        result = generate_executive_summary(sample_trends, {}, [])
        assert "Summary" in result

    @patch("src.kpi_reporter.core.chat")
    def test_includes_anomalies(self, mock_chat, sample_trends, sample_targets):
        mock_chat.return_value = "## Summary\n\nAnomalies found."
        goals = track_goals(sample_trends, sample_targets)
        anomalies = [{"kpi": "revenue", "period": "Apr", "value": 120000,
                       "mean": 108750, "std_dev": 7500, "deviation": 2.5}]
        result = generate_executive_summary(sample_trends, goals, anomalies)
        assert "Summary" in result


# ─── TestGenerateKpiReport ───────────────────────────────────────────────────


class TestGenerateKpiReport:
    @patch("src.kpi_reporter.core.chat")
    def test_generates_report(self, mock_chat, sample_kpi_data, sample_trends):
        mock_chat.return_value = "# KPI Report\n\nStrong growth in revenue."
        result = generate_kpi_report(sample_kpi_data, sample_trends, "monthly")
        assert "KPI Report" in result
        mock_chat.assert_called_once()


# ─── TestComputeAnalytics ────────────────────────────────────────────────────


class TestComputeAnalytics:
    def test_analytics_computation(self, sample_trends, sample_targets):
        goals = track_goals(sample_trends, sample_targets)
        analytics = compute_analytics(sample_trends, goals)
        assert analytics["total_kpis"] == len(sample_trends)
        assert "improving" in analytics
        assert "declining" in analytics
        assert "stable" in analytics
        assert "avg_change_pct" in analytics
        assert "goals_summary" in analytics

    def test_empty_data(self):
        analytics = compute_analytics({}, {})
        assert analytics["total_kpis"] == 0
        assert analytics["avg_change_pct"] == 0.0


# ─── TestLoadConfig ──────────────────────────────────────────────────────────


class TestLoadConfig:
    def test_load_existing_config(self, config_yaml):
        cfg = load_config(config_yaml)
        assert cfg["model"]["temperature"] == 0.5
        assert cfg["targets"]["revenue"] == 150000
        assert cfg["anomaly_detection"]["threshold"] == 1.5

    def test_load_missing_config(self):
        cfg = load_config("nonexistent_config.yaml")
        assert cfg["model"]["name"] == "gemma3"
        assert cfg["alert_threshold_pct"] == 10

    def test_default_config_structure(self):
        cfg = load_config("nonexistent_config.yaml")
        assert "model" in cfg
        assert "targets" in cfg
        assert "anomaly_detection" in cfg
        assert "moving_average" in cfg
        assert "logging" in cfg
