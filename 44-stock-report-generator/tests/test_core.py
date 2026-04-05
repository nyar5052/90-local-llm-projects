"""Tests for Stock Report Generator core module."""

import os
import json
import pytest
from unittest.mock import patch, MagicMock

from src.stock_reporter.core import (
    load_stock_data,
    compute_metrics,
    compute_technical_indicators,
    assess_risk,
    compare_tickers,
    generate_report,
)


class TestLoadStockData:
    def test_load_valid_csv(self, sample_stock_csv):
        data = load_stock_data(sample_stock_csv)
        assert len(data) == 6
        assert "Close" in data[0]

    def test_load_nonexistent_file(self):
        with pytest.raises(FileNotFoundError):
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


class TestComputeTechnicalIndicators:
    def test_indicators_with_sufficient_data(self, large_stock_data):
        indicators = compute_technical_indicators(large_stock_data)
        assert indicators["rsi"] is not None
        assert indicators["bollinger"] is not None
        assert "upper" in indicators["bollinger"]

    def test_indicators_insufficient_data(self, sample_stock_data):
        indicators = compute_technical_indicators(sample_stock_data)
        assert indicators["rsi"] is None


class TestAssessRisk:
    def test_risk_assessment(self, sample_stock_data, large_stock_data):
        metrics = compute_metrics(sample_stock_data)
        indicators = compute_technical_indicators(large_stock_data)
        risk = assess_risk(metrics, indicators)
        assert "risk_score" in risk
        assert "risk_level" in risk
        assert risk["risk_level"] in ["low", "medium", "high"]

    def test_risk_without_indicators(self, sample_stock_data):
        metrics = compute_metrics(sample_stock_data)
        risk = assess_risk(metrics, {})
        assert "risk_score" in risk


class TestCompareTickers:
    def test_comparison(self, sample_stock_data):
        datasets = {"AAPL": sample_stock_data, "GOOG": sample_stock_data}
        comparison = compare_tickers(datasets)
        assert "AAPL" in comparison
        assert "GOOG" in comparison


class TestGenerateReport:
    @patch("src.stock_reporter.core.get_llm_client")
    def test_generate_report(self, mock_get_client, sample_stock_data):
        mock_chat = MagicMock(return_value="# AAPL Analysis\n\nThe stock shows an upward trend...")
        mock_get_client.return_value = (mock_chat, MagicMock())
        metrics = compute_metrics(sample_stock_data)
        report = generate_report(sample_stock_data, metrics, "AAPL")
        assert "AAPL" in report or "upward" in report
        mock_chat.assert_called_once()
