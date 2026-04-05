"""Tests for Financial Report Generator."""

import json
import pytest
from unittest.mock import patch
from click.testing import CliRunner

from app import main, load_financial_data, compute_financial_metrics, generate_financial_report


@pytest.fixture
def sample_financials_csv(tmp_path):
    """Create a sample financial data CSV."""
    csv_path = tmp_path / "financials.csv"
    csv_path.write_text(
        "month,revenue,expenses,net_income\n"
        "October,500000,350000,150000\n"
        "November,550000,380000,170000\n"
        "December,600000,400000,200000\n"
    )
    return str(csv_path)


@pytest.fixture
def sample_financial_data():
    """Return sample financial data."""
    return [
        {"month": "Oct", "revenue": "500000", "expenses": "350000", "net_income": "150000"},
        {"month": "Nov", "revenue": "550000", "expenses": "380000", "net_income": "170000"},
        {"month": "Dec", "revenue": "600000", "expenses": "400000", "net_income": "200000"},
    ]


class TestLoadFinancialData:
    def test_load_valid_csv(self, sample_financials_csv):
        data = load_financial_data(sample_financials_csv)
        assert len(data) == 3
        assert "revenue" in data[0]

    def test_load_nonexistent_file(self):
        with pytest.raises(SystemExit):
            load_financial_data("nonexistent.csv")


class TestComputeFinancialMetrics:
    def test_metrics_computation(self, sample_financial_data):
        metrics = compute_financial_metrics(sample_financial_data)
        assert "revenue" in metrics
        assert metrics["revenue"]["total"] == 1650000
        assert metrics["revenue"]["latest"] == 600000

    def test_metrics_average(self, sample_financial_data):
        metrics = compute_financial_metrics(sample_financial_data)
        assert metrics["net_income"]["average"] == pytest.approx(173333.33, rel=1e-2)

    def test_metrics_min_max(self, sample_financial_data):
        metrics = compute_financial_metrics(sample_financial_data)
        assert metrics["expenses"]["min"] == 350000
        assert metrics["expenses"]["max"] == 400000


class TestGenerateReport:
    @patch("app.chat")
    def test_generate_report(self, mock_chat, sample_financial_data):
        mock_chat.return_value = "# Q4-2024 Financial Report\n\nRevenue grew 20%..."
        metrics = compute_financial_metrics(sample_financial_data)
        report = generate_financial_report(sample_financial_data, metrics, "Q4-2024")
        assert "Q4-2024" in report or "Revenue" in report
        mock_chat.assert_called_once()


class TestCLI:
    @patch("app.check_ollama_running", return_value=True)
    @patch("app.chat")
    def test_cli_full_report(self, mock_chat, mock_check, sample_financials_csv):
        mock_chat.return_value = "# Financial Report\n\nStrong Q4 performance..."
        runner = CliRunner()
        result = runner.invoke(main, ["--file", sample_financials_csv, "--period", "Q4-2024"])
        assert result.exit_code == 0

    @patch("app.check_ollama_running", return_value=False)
    def test_cli_ollama_not_running(self, mock_check, sample_financials_csv):
        runner = CliRunner()
        result = runner.invoke(main, ["--file", sample_financials_csv, "--period", "Q4-2024"])
        assert result.exit_code != 0
