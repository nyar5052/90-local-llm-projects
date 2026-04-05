"""Tests for CSV Data Analyzer core module."""

import os
import json
import pytest
import pandas as pd
from unittest.mock import patch, MagicMock

from src.csv_analyzer.core import (
    load_csv,
    detect_column_types,
    generate_statistical_summary,
    compute_correlations,
    suggest_charts,
    generate_data_summary,
    analyze_data,
    export_insights,
)


class TestLoadCSV:
    def test_load_valid_csv(self, sample_csv):
        df = load_csv(sample_csv)
        assert len(df) == 4
        assert "revenue" in df.columns

    def test_load_nonexistent_file(self):
        with pytest.raises(FileNotFoundError):
            load_csv("nonexistent.csv")

    def test_load_empty_csv(self, tmp_path):
        empty_csv = tmp_path / "empty.csv"
        empty_csv.write_text("")
        with pytest.raises(ValueError):
            load_csv(str(empty_csv))


class TestDetectColumnTypes:
    def test_numeric_detection(self, sample_df):
        types = detect_column_types(sample_df)
        assert types["revenue"] == "numeric"
        assert types["expenses"] == "numeric"

    def test_categorical_detection(self):
        df = pd.DataFrame({"color": ["red", "blue", "red", "blue"] * 10})
        types = detect_column_types(df)
        assert types["color"] == "categorical"


class TestGenerateStatisticalSummary:
    def test_summary_shape(self, sample_df):
        summary = generate_statistical_summary(sample_df)
        assert summary["shape"]["rows"] == 3
        assert summary["shape"]["columns"] == 3

    def test_summary_has_numeric_stats(self, sample_df):
        summary = generate_statistical_summary(sample_df)
        assert "numeric_stats" in summary

    def test_summary_null_counts(self, sample_df):
        summary = generate_statistical_summary(sample_df)
        assert "null_counts" in summary


class TestComputeCorrelations:
    def test_correlations_with_numeric(self, large_numeric_df):
        result = compute_correlations(large_numeric_df)
        assert result is not None
        assert "matrix" in result
        assert "strong_correlations" in result

    def test_no_correlations_single_col(self):
        df = pd.DataFrame({"a": [1, 2, 3]})
        assert compute_correlations(df) is None


class TestSuggestCharts:
    def test_suggests_histogram(self, sample_df):
        types = detect_column_types(sample_df)
        suggestions = suggest_charts(sample_df, types)
        chart_types = [s["type"] for s in suggestions]
        assert "histogram" in chart_types

    def test_suggests_scatter_for_multiple_numeric(self, sample_df):
        types = detect_column_types(sample_df)
        suggestions = suggest_charts(sample_df, types)
        chart_types = [s["type"] for s in suggestions]
        assert "scatter" in chart_types


class TestGenerateDataSummary:
    def test_summary_contains_shape(self, sample_df):
        summary = generate_data_summary(sample_df)
        assert "3 rows x 3 columns" in summary

    def test_summary_contains_columns(self, sample_df):
        summary = generate_data_summary(sample_df)
        assert "month" in summary
        assert "revenue" in summary


class TestAnalyzeData:
    @patch("src.csv_analyzer.core.get_llm_client")
    def test_analyze_returns_response(self, mock_get_client, sample_df):
        mock_chat = MagicMock(return_value="April had the highest revenue at $18,000.")
        mock_get_client.return_value = (mock_chat, MagicMock())
        result = analyze_data(sample_df, "What month had highest revenue?")
        assert "highest revenue" in result.lower() or "18,000" in result
        mock_chat.assert_called_once()


class TestExportInsights:
    def test_export_creates_file(self, sample_df, tmp_path):
        output = str(tmp_path / "insights.json")
        export_insights(sample_df, output)
        assert os.path.exists(output)
        with open(output) as f:
            data = json.load(f)
        assert "column_types" in data
        assert "statistics" in data
        assert "chart_suggestions" in data
