"""Tests for KPI Dashboard Reporter CLI."""

import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner

from src.kpi_reporter.cli import main


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
def runner():
    """Click CLI test runner."""
    return CliRunner()


class TestReportCommand:
    @patch("src.kpi_reporter.cli.check_ollama_running", return_value=True)
    @patch("src.kpi_reporter.core.chat")
    def test_report_success(self, mock_chat, mock_check, runner, sample_kpi_csv):
        mock_chat.return_value = "# KPI Report\n\nStrong growth in revenue..."
        result = runner.invoke(main, ["report", "--file", sample_kpi_csv, "--period", "monthly"])
        assert result.exit_code == 0

    @patch("src.kpi_reporter.cli.check_ollama_running", return_value=False)
    def test_report_ollama_not_running(self, mock_check, runner, sample_kpi_csv):
        result = runner.invoke(main, ["report", "--file", sample_kpi_csv, "--period", "Q1"])
        assert result.exit_code != 0

    @patch("src.kpi_reporter.cli.check_ollama_running", return_value=True)
    @patch("src.kpi_reporter.core.chat")
    def test_report_no_alerts(self, mock_chat, mock_check, runner, sample_kpi_csv):
        mock_chat.return_value = "# Report\n\nAll good."
        result = runner.invoke(
            main, ["report", "--file", sample_kpi_csv, "--no-alerts"]
        )
        assert result.exit_code == 0

    def test_report_missing_file(self, runner):
        result = runner.invoke(main, ["report", "--file", "nonexistent.csv"])
        assert result.exit_code != 0


class TestDashboardCommand:
    def test_dashboard_success(self, runner, sample_kpi_csv):
        result = runner.invoke(main, ["dashboard", "--file", sample_kpi_csv])
        assert result.exit_code == 0

    def test_dashboard_missing_file(self, runner):
        result = runner.invoke(main, ["dashboard", "--file", "nonexistent.csv"])
        assert result.exit_code != 0


class TestGoalsCommand:
    def test_goals_success(self, runner, sample_kpi_csv):
        result = runner.invoke(main, ["goals", "--file", sample_kpi_csv])
        assert result.exit_code == 0

    def test_goals_missing_file(self, runner):
        result = runner.invoke(main, ["goals", "--file", "nonexistent.csv"])
        assert result.exit_code != 0


class TestAnomaliesCommand:
    def test_anomalies_success(self, runner, sample_kpi_csv):
        result = runner.invoke(main, ["anomalies", "--file", sample_kpi_csv])
        assert result.exit_code == 0

    def test_anomalies_custom_threshold(self, runner, sample_kpi_csv):
        result = runner.invoke(
            main, ["anomalies", "--file", sample_kpi_csv, "--threshold", "1.5"]
        )
        assert result.exit_code == 0

    def test_anomalies_missing_file(self, runner):
        result = runner.invoke(main, ["anomalies", "--file", "nonexistent.csv"])
        assert result.exit_code != 0


class TestMainGroup:
    def test_help(self, runner):
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "KPI Dashboard Reporter" in result.output

    def test_report_help(self, runner):
        result = runner.invoke(main, ["report", "--help"])
        assert result.exit_code == 0
        assert "--file" in result.output

    def test_custom_config(self, runner, sample_kpi_csv, tmp_path):
        config_path = tmp_path / "custom_config.yaml"
        config_path.write_text(
            "model:\n  name: gemma3\ntargets:\n  revenue: 100000\n"
        )
        result = runner.invoke(
            main, ["--config", str(config_path), "dashboard", "--file", sample_kpi_csv]
        )
        assert result.exit_code == 0
