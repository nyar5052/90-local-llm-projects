"""Tests for the Report Generator core module."""

import csv
import os
import pytest
from unittest.mock import patch

from src.report_generator.core import (
    read_csv_data,
    summarize_data,
    generate_report,
    save_report,
    REPORT_TEMPLATES,
)


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
    """Create a CSV file with headers only."""
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


class TestReadCsvData:
    """Tests for read_csv_data function."""

    def test_read_valid_csv(self, sample_csv):
        headers, rows = read_csv_data(sample_csv)
        assert headers == ["Region", "Product", "Revenue", "Units"]
        assert len(rows) == 5
        assert rows[0]["Region"] == "North"

    def test_file_not_found_raises(self):
        with pytest.raises(FileNotFoundError, match="CSV file not found"):
            read_csv_data("nonexistent_file.csv")

    def test_empty_csv_raises(self, empty_csv):
        with pytest.raises(ValueError, match="no data rows"):
            read_csv_data(empty_csv)

    def test_blank_csv_raises(self, blank_csv):
        with pytest.raises(ValueError, match="empty or has no header"):
            read_csv_data(blank_csv)


class TestSummarizeData:
    """Tests for summarize_data function."""

    def test_summary_contains_row_count(self, sample_csv):
        headers, rows = read_csv_data(sample_csv)
        summary = summarize_data(headers, rows)
        assert "Total rows: 5" in summary

    def test_summary_contains_all_columns(self, sample_csv):
        headers, rows = read_csv_data(sample_csv)
        summary = summarize_data(headers, rows)
        for col in headers:
            assert col in summary

    def test_numeric_stats_computed(self, sample_csv):
        headers, rows = read_csv_data(sample_csv)
        summary = summarize_data(headers, rows)
        assert "9,500.00" in summary or "9500" in summary
        assert "mean" in summary.lower()

    def test_categorical_values_listed(self, sample_csv):
        headers, rows = read_csv_data(sample_csv)
        summary = summarize_data(headers, rows)
        assert "unique" in summary.lower() or "North" in summary

    def test_summary_handles_single_row(self, tmp_path):
        filepath = tmp_path / "single.csv"
        with open(filepath, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Value"])
            writer.writerow(["42"])
        headers, rows = read_csv_data(str(filepath))
        summary = summarize_data(headers, rows)
        assert "42" in summary
        assert "stdev" not in summary


class TestGenerateReport:
    """Tests for generate_report with mocked LLM calls."""

    @patch("src.report_generator.core.chat")
    def test_returns_llm_output(self, mock_chat):
        mock_chat.return_value = "# Mocked Report\nSome analysis."
        result = generate_report("Test Topic", "summary data")
        assert "Mocked Report" in result

    @patch("src.report_generator.core.chat")
    def test_passes_topic_in_prompt(self, mock_chat):
        mock_chat.return_value = "report"
        generate_report("Q4 Sales", "summary")
        call_args = mock_chat.call_args
        messages = call_args.kwargs.get("messages") or call_args[0][0]
        user_content = messages[0]["content"]
        assert "Q4 Sales" in user_content

    @patch("src.report_generator.core.chat")
    def test_template_selection(self, mock_chat):
        mock_chat.return_value = "report"
        generate_report("Topic", "data", template="technical")
        call_args = mock_chat.call_args
        messages = call_args.kwargs.get("messages") or call_args[0][0]
        user_content = messages[0]["content"]
        assert "technical" in user_content.lower() or "Methodology" in user_content


class TestSaveReport:
    """Tests for save_report function."""

    def test_creates_output_file(self, tmp_path):
        outpath = str(tmp_path / "output.md")
        saved = save_report("# Report", outpath, "My Topic")
        assert os.path.exists(saved)

    def test_file_contains_content(self, tmp_path):
        outpath = str(tmp_path / "output.md")
        save_report("# Body Content", outpath, "Sales Report")
        with open(outpath, encoding="utf-8") as f:
            content = f.read()
        assert "# Body Content" in content
        assert 'title: "Sales Report"' in content

    def test_creates_parent_directories(self, tmp_path):
        outpath = str(tmp_path / "sub" / "dir" / "report.md")
        saved = save_report("content", outpath, "Topic")
        assert os.path.exists(saved)

    def test_html_format(self, tmp_path):
        outpath = str(tmp_path / "output.html")
        saved = save_report("# Report Content", outpath, "Topic", fmt="html")
        assert saved.endswith(".html")
        assert os.path.exists(saved)

    def test_text_format(self, tmp_path):
        outpath = str(tmp_path / "output.txt")
        saved = save_report("Report Content", outpath, "Topic", fmt="text")
        assert saved.endswith(".txt")


class TestReportTemplates:
    """Tests for report template definitions."""

    def test_all_templates_exist(self):
        assert "executive" in REPORT_TEMPLATES
        assert "technical" in REPORT_TEMPLATES
        assert "summary" in REPORT_TEMPLATES

    def test_templates_have_placeholders(self):
        for name, tmpl in REPORT_TEMPLATES.items():
            assert "{topic}" in tmpl, f"Template '{name}' missing {{topic}}"
            assert "{data_summary}" in tmpl, f"Template '{name}' missing {{data_summary}}"
