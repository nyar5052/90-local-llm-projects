"""Tests for the PDF Report Generator."""

import csv
import os
import tempfile

import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner

from app import read_csv_data, summarize_data, generate_report, save_report, main


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_csv(tmp_path):
    """Create a temporary CSV file with sample sales data."""
    filepath = tmp_path / "sales.csv"
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Region", "Product", "Revenue", "Units"])
        writer.writerow(["North", "Widget A", "15000", "120"])
        writer.writerow(["South", "Widget B", "22000", "200"])
        writer.writerow(["East", "Widget A", "18000", "150"])
        writer.writerow(["West", "Widget C", "9500", "80"])
        writer.writerow(["North", "Widget B", "27000", "230"])
    return str(filepath)


@pytest.fixture
def empty_csv(tmp_path):
    """Create a CSV file with headers only and no data rows."""
    filepath = tmp_path / "empty.csv"
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Col1", "Col2"])
    return str(filepath)


@pytest.fixture
def blank_csv(tmp_path):
    """Create a completely empty CSV file."""
    filepath = tmp_path / "blank.csv"
    filepath.write_text("")
    return str(filepath)


# ---------------------------------------------------------------------------
# Tests – CSV Reading
# ---------------------------------------------------------------------------

class TestReadCsvData:
    """Tests for read_csv_data function."""

    def test_read_valid_csv(self, sample_csv):
        """Reading a well-formed CSV returns correct headers and row count."""
        headers, rows = read_csv_data(sample_csv)
        assert headers == ["Region", "Product", "Revenue", "Units"]
        assert len(rows) == 5
        assert rows[0]["Region"] == "North"
        assert rows[1]["Revenue"] == "22000"

    def test_file_not_found_raises(self):
        """A missing file path raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError, match="CSV file not found"):
            read_csv_data("nonexistent_file.csv")

    def test_empty_csv_raises(self, empty_csv):
        """A CSV with headers but no data rows raises ValueError."""
        with pytest.raises(ValueError, match="no data rows"):
            read_csv_data(empty_csv)

    def test_blank_csv_raises(self, blank_csv):
        """A completely empty CSV raises ValueError."""
        with pytest.raises(ValueError, match="empty or has no header"):
            read_csv_data(blank_csv)


# ---------------------------------------------------------------------------
# Tests – Data Summarization
# ---------------------------------------------------------------------------

class TestSummarizeData:
    """Tests for summarize_data function."""

    def test_summary_contains_row_count(self, sample_csv):
        """Summary string includes the total number of rows."""
        headers, rows = read_csv_data(sample_csv)
        summary = summarize_data(headers, rows)
        assert "Total rows: 5" in summary

    def test_summary_contains_all_columns(self, sample_csv):
        """Summary lists every column name."""
        headers, rows = read_csv_data(sample_csv)
        summary = summarize_data(headers, rows)
        for col in headers:
            assert col in summary

    def test_numeric_stats_computed(self, sample_csv):
        """Numeric columns show min, max, mean, and sum statistics."""
        headers, rows = read_csv_data(sample_csv)
        summary = summarize_data(headers, rows)
        # Revenue column: min=9500, max=27000
        assert "9,500.00" in summary or "9500" in summary
        assert "27,000.00" in summary or "27000" in summary
        assert "mean" in summary.lower()

    def test_categorical_values_listed(self, sample_csv):
        """Categorical columns list unique values or counts."""
        headers, rows = read_csv_data(sample_csv)
        summary = summarize_data(headers, rows)
        assert "unique" in summary.lower() or "North" in summary

    def test_summary_handles_single_row(self, tmp_path):
        """Summarization works with a single-row dataset (no stdev)."""
        filepath = tmp_path / "single.csv"
        with open(filepath, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Value"])
            writer.writerow(["42"])
        headers, rows = read_csv_data(str(filepath))
        summary = summarize_data(headers, rows)
        assert "42" in summary
        # stdev should not appear for a single value
        assert "stdev" not in summary


# ---------------------------------------------------------------------------
# Tests – Report Generation (mocked LLM)
# ---------------------------------------------------------------------------

class TestGenerateReport:
    """Tests for generate_report with mocked LLM calls."""

    @patch("app.chat")
    def test_returns_llm_output(self, mock_chat):
        """generate_report returns the string from the LLM."""
        mock_chat.return_value = "# Mocked Report\nSome analysis."
        result = generate_report("Test Topic", "summary data")
        assert "Mocked Report" in result

    @patch("app.chat")
    def test_passes_topic_in_prompt(self, mock_chat):
        """The topic appears in the message sent to the LLM."""
        mock_chat.return_value = "report"
        generate_report("Q4 Sales", "summary")
        call_args = mock_chat.call_args
        messages = call_args.kwargs.get("messages") or call_args[0][0]
        user_content = messages[0]["content"]
        assert "Q4 Sales" in user_content

    @patch("app.chat")
    def test_passes_data_summary_in_prompt(self, mock_chat):
        """The data summary appears in the message sent to the LLM."""
        mock_chat.return_value = "report"
        generate_report("Topic", "Total rows: 100")
        call_args = mock_chat.call_args
        messages = call_args.kwargs.get("messages") or call_args[0][0]
        user_content = messages[0]["content"]
        assert "Total rows: 100" in user_content


# ---------------------------------------------------------------------------
# Tests – Report Saving
# ---------------------------------------------------------------------------

class TestSaveReport:
    """Tests for save_report function."""

    def test_creates_output_file(self, tmp_path):
        """save_report writes a file to the specified path."""
        outpath = str(tmp_path / "output.md")
        saved = save_report("# Report", outpath, "My Topic")
        assert os.path.exists(saved)

    def test_file_contains_content(self, tmp_path):
        """The saved file includes both the YAML front-matter and body."""
        outpath = str(tmp_path / "output.md")
        save_report("# Body Content", outpath, "Sales Report")
        with open(outpath, encoding="utf-8") as f:
            content = f.read()
        assert "# Body Content" in content
        assert 'title: "Sales Report"' in content
        assert "generator:" in content

    def test_creates_parent_directories(self, tmp_path):
        """save_report creates intermediate directories if needed."""
        outpath = str(tmp_path / "sub" / "dir" / "report.md")
        saved = save_report("content", outpath, "Topic")
        assert os.path.exists(saved)


# ---------------------------------------------------------------------------
# Tests – CLI Integration
# ---------------------------------------------------------------------------

class TestCLI:
    """Tests for the Click CLI entrypoint."""

    def test_cli_missing_data_option(self):
        """CLI exits with error when --data is missing."""
        runner = CliRunner()
        result = runner.invoke(main, ["--topic", "Test"])
        assert result.exit_code != 0
        assert "Missing" in result.output or "Error" in result.output or "missing" in result.output.lower() or result.exit_code == 2

    def test_cli_missing_topic_option(self):
        """CLI exits with error when --topic is missing."""
        runner = CliRunner()
        result = runner.invoke(main, ["--data", "some.csv"])
        assert result.exit_code != 0

    @patch("app.check_ollama_running", return_value=True)
    @patch("app.chat")
    def test_cli_end_to_end(self, mock_chat, mock_ollama, sample_csv, tmp_path):
        """Full CLI invocation with mocked LLM produces a report file."""
        mock_chat.return_value = "# Generated Report\n\nAnalysis here."
        outpath = str(tmp_path / "result.md")
        runner = CliRunner()
        result = runner.invoke(
            main, ["--topic", "Q4 Sales", "--data", sample_csv, "--output", outpath]
        )
        assert result.exit_code == 0
        assert os.path.exists(outpath)
        with open(outpath, encoding="utf-8") as f:
            content = f.read()
        assert "Generated Report" in content

    def test_cli_nonexistent_data_file(self):
        """CLI rejects a --data path that doesn't exist."""
        runner = CliRunner()
        result = runner.invoke(main, ["--topic", "Test", "--data", "no_such_file.csv"])
        assert result.exit_code != 0
