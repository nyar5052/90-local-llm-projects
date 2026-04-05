"""Tests for CSV Data Analyzer."""

import os
import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from click.testing import CliRunner

from app import main, load_csv, generate_data_summary, analyze_data


@pytest.fixture
def sample_csv(tmp_path):
    """Create a sample CSV file for testing."""
    csv_path = tmp_path / "test_data.csv"
    df = pd.DataFrame({
        "month": ["Jan", "Feb", "Mar", "Apr"],
        "revenue": [10000, 15000, 12000, 18000],
        "expenses": [8000, 9000, 7500, 10000],
    })
    df.to_csv(csv_path, index=False)
    return str(csv_path)


@pytest.fixture
def sample_df():
    """Return a sample DataFrame."""
    return pd.DataFrame({
        "month": ["Jan", "Feb", "Mar"],
        "revenue": [10000, 15000, 12000],
        "expenses": [8000, 9000, 7500],
    })


class TestLoadCSV:
    def test_load_valid_csv(self, sample_csv):
        df = load_csv(sample_csv)
        assert len(df) == 4
        assert "revenue" in df.columns

    def test_load_nonexistent_file(self):
        with pytest.raises(SystemExit):
            load_csv("nonexistent.csv")


class TestGenerateDataSummary:
    def test_summary_contains_shape(self, sample_df):
        summary = generate_data_summary(sample_df)
        assert "3 rows x 3 columns" in summary

    def test_summary_contains_columns(self, sample_df):
        summary = generate_data_summary(sample_df)
        assert "month" in summary
        assert "revenue" in summary
        assert "expenses" in summary


class TestAnalyzeData:
    @patch("app.chat")
    def test_analyze_returns_response(self, mock_chat, sample_df):
        mock_chat.return_value = "April had the highest revenue at $18,000."
        result = analyze_data(sample_df, "What month had highest revenue?")
        assert "highest revenue" in result.lower() or "18,000" in result
        mock_chat.assert_called_once()

    @patch("app.chat")
    def test_analyze_sends_correct_prompt(self, mock_chat, sample_df):
        mock_chat.return_value = "Answer"
        analyze_data(sample_df, "Test question?")
        call_args = mock_chat.call_args
        messages = call_args[0][0]
        assert "Test question?" in messages[0]["content"]


class TestCLI:
    @patch("app.check_ollama_running", return_value=True)
    @patch("app.chat")
    def test_cli_with_valid_file(self, mock_chat, mock_check, sample_csv):
        mock_chat.return_value = "The data shows interesting trends."
        runner = CliRunner()
        result = runner.invoke(main, ["--file", sample_csv, "--query", "Summarize"])
        assert result.exit_code == 0

    @patch("app.check_ollama_running", return_value=False)
    def test_cli_ollama_not_running(self, mock_check, sample_csv):
        runner = CliRunner()
        result = runner.invoke(main, ["--file", sample_csv, "--query", "test"])
        assert result.exit_code != 0
