"""Tests for KPI Dashboard Reporter."""

import json
import pytest
from unittest.mock import patch
from click.testing import CliRunner

from app import main, load_kpi_data, compute_kpi_trends, generate_alert_summary, safe_float


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
    """Return sample KPI data."""
    return [
        {"month": "Jan", "revenue": "100000", "customers": "500", "churn_rate": "5.2"},
        {"month": "Feb", "revenue": "110000", "customers": "520", "churn_rate": "4.8"},
        {"month": "Mar", "revenue": "105000", "customers": "510", "churn_rate": "5.5"},
        {"month": "Apr", "revenue": "120000", "customers": "550", "churn_rate": "4.2"},
    ]


class TestSafeFloat:
    def test_basic_number(self):
        assert safe_float("100") == 100.0

    def test_formatted_number(self):
        assert safe_float("$1,000.50") == 1000.50

    def test_percentage(self):
        assert safe_float("5.2%") == 5.2

    def test_invalid_value(self):
        assert safe_float("abc") == 0.0


class TestLoadKpiData:
    def test_load_valid_csv(self, sample_kpi_csv):
        data = load_kpi_data(sample_kpi_csv)
        assert len(data) == 4
        assert "revenue" in data[0]

    def test_load_nonexistent_file(self):
        with pytest.raises(SystemExit):
            load_kpi_data("nonexistent.csv")


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


class TestCLI:
    @patch("app.check_ollama_running", return_value=True)
    @patch("app.chat")
    def test_cli_generate_report(self, mock_chat, mock_check, sample_kpi_csv):
        mock_chat.return_value = "# KPI Report\n\nStrong growth in revenue..."
        runner = CliRunner()
        result = runner.invoke(main, ["--file", sample_kpi_csv, "--period", "monthly"])
        assert result.exit_code == 0

    @patch("app.check_ollama_running", return_value=False)
    def test_cli_ollama_not_running(self, mock_check, sample_kpi_csv):
        runner = CliRunner()
        result = runner.invoke(main, ["--file", sample_kpi_csv, "--period", "Q1"])
        assert result.exit_code != 0
