"""Tests for Stock Report Generator."""

import os
import pytest
from unittest.mock import patch
from click.testing import CliRunner

from app import main, load_stock_data, compute_metrics, generate_report


@pytest.fixture
def sample_stock_csv(tmp_path):
    """Create a sample stock data CSV."""
    csv_path = tmp_path / "stock.csv"
    csv_path.write_text(
        "Date,Open,High,Low,Close,Volume\n"
        "2024-01-02,150.00,152.00,149.00,151.00,1000000\n"
        "2024-01-03,151.00,155.00,150.00,154.00,1200000\n"
        "2024-01-04,154.00,156.00,152.00,153.00,900000\n"
        "2024-01-05,153.00,158.00,153.00,157.00,1100000\n"
        "2024-01-08,157.00,160.00,155.00,159.00,1300000\n"
        "2024-01-09,159.00,161.00,157.00,160.00,1050000\n"
    )
    return str(csv_path)


@pytest.fixture
def sample_stock_data():
    """Return sample stock data as list of dicts."""
    return [
        {"Date": "2024-01-02", "Close": "150.00"},
        {"Date": "2024-01-03", "Close": "155.00"},
        {"Date": "2024-01-04", "Close": "153.00"},
        {"Date": "2024-01-05", "Close": "158.00"},
        {"Date": "2024-01-08", "Close": "160.00"},
    ]


class TestLoadStockData:
    def test_load_valid_csv(self, sample_stock_csv):
        data = load_stock_data(sample_stock_csv)
        assert len(data) == 6
        assert "Close" in data[0]

    def test_load_nonexistent_file(self):
        with pytest.raises(SystemExit):
            load_stock_data("nonexistent.csv")


class TestComputeMetrics:
    def test_metrics_calculation(self, sample_stock_data):
        metrics = compute_metrics(sample_stock_data)
        assert metrics["current_price"] == 160.00
        assert metrics["period_start_price"] == 150.00
        assert metrics["period_high"] == 160.00
        assert metrics["period_low"] == 150.00
        assert metrics["change_percent"] > 0

    def test_insufficient_data(self):
        data = [{"Close": "100.00"}]
        metrics = compute_metrics(data)
        assert "error" in metrics

    def test_positive_days_counting(self, sample_stock_data):
        metrics = compute_metrics(sample_stock_data)
        assert metrics["positive_days"] >= 0
        assert metrics["negative_days"] >= 0
        total = metrics["positive_days"] + metrics["negative_days"]
        assert total == len(sample_stock_data) - 1


class TestGenerateReport:
    @patch("app.chat")
    def test_generate_report(self, mock_chat, sample_stock_data):
        mock_chat.return_value = "# AAPL Analysis\n\nThe stock shows an upward trend..."
        metrics = compute_metrics(sample_stock_data)
        report = generate_report(sample_stock_data, metrics, "AAPL")
        assert "AAPL" in report or "upward" in report
        mock_chat.assert_called_once()


class TestCLI:
    @patch("app.check_ollama_running", return_value=True)
    @patch("app.chat")
    def test_cli_valid_input(self, mock_chat, mock_check, sample_stock_csv):
        mock_chat.return_value = "# Report\n\nBullish trend observed."
        runner = CliRunner()
        result = runner.invoke(main, ["--file", sample_stock_csv, "--ticker", "AAPL"])
        assert result.exit_code == 0

    @patch("app.check_ollama_running", return_value=False)
    def test_cli_ollama_not_running(self, mock_check, sample_stock_csv):
        runner = CliRunner()
        result = runner.invoke(main, ["--file", sample_stock_csv, "--ticker", "AAPL"])
        assert result.exit_code != 0
