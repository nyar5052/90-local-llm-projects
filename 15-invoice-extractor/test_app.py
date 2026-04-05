"""Tests for the Invoice Extractor application."""

import json
from io import StringIO
from unittest.mock import patch, mock_open

import click
import pytest
from click.testing import CliRunner

from app import (
    extract_invoice_data,
    format_csv,
    main,
    parse_llm_json,
    read_invoice_file,
)

# ---------------------------------------------------------------------------
# Sample fixtures
# ---------------------------------------------------------------------------

SAMPLE_INVOICE_TEXT = """\
ACME Corporation
123 Business Ave, Suite 100
New York, NY 10001

Invoice #: INV-2024-0042
Date: 2024-03-15
Due: 2024-04-15

Bill To: John Doe

Description              Qty   Unit Price   Total
Widget A                  2     25.00       50.00
Widget B                  5     10.00       50.00
Consulting (1 hr)         1    150.00      150.00

Subtotal:  250.00
Tax (8%):   20.00
Total:     270.00

Payment Terms: Net 30
"""

SAMPLE_LLM_RESPONSE = json.dumps(
    {
        "vendor": {
            "name": "ACME Corporation",
            "address": "123 Business Ave, Suite 100, New York, NY 10001",
            "phone": None,
            "email": None,
        },
        "invoice_number": "INV-2024-0042",
        "date": "2024-03-15",
        "due_date": "2024-04-15",
        "line_items": [
            {"description": "Widget A", "quantity": 2, "unit_price": 25.00, "total": 50.00},
            {"description": "Widget B", "quantity": 5, "unit_price": 10.00, "total": 50.00},
            {"description": "Consulting (1 hr)", "quantity": 1, "unit_price": 150.00, "total": 150.00},
        ],
        "subtotal": 250.00,
        "tax": 20.00,
        "grand_total": 270.00,
        "currency": "USD",
        "payment_terms": "Net 30",
    }
)


EXPECTED_DATA = json.loads(SAMPLE_LLM_RESPONSE)


# ---------------------------------------------------------------------------
# Tests — File reading
# ---------------------------------------------------------------------------


class TestReadInvoiceFile:
    """Tests for read_invoice_file."""

    def test_reads_existing_file(self, tmp_path):
        """Should return contents of a valid text file."""
        invoice = tmp_path / "invoice.txt"
        invoice.write_text(SAMPLE_INVOICE_TEXT, encoding="utf-8")

        result = read_invoice_file(str(invoice))
        assert "ACME Corporation" in result
        assert "INV-2024-0042" in result

    def test_raises_on_missing_file(self):
        """Should raise ClickException for a nonexistent file."""
        with pytest.raises(click.ClickException, match="File not found"):
            read_invoice_file("nonexistent_file_12345.txt")

    def test_reads_unicode_content(self, tmp_path):
        """Should handle unicode characters in invoice text."""
        invoice = tmp_path / "unicode.txt"
        invoice.write_text("Ünïcödé Vendor — €100.00", encoding="utf-8")

        result = read_invoice_file(str(invoice))
        assert "€100.00" in result


# ---------------------------------------------------------------------------
# Tests — LLM JSON parsing
# ---------------------------------------------------------------------------


class TestParseLlmJson:
    """Tests for parse_llm_json."""

    def test_parses_clean_json(self):
        """Should parse a plain JSON string."""
        data = parse_llm_json(SAMPLE_LLM_RESPONSE)
        assert data["vendor"]["name"] == "ACME Corporation"
        assert len(data["line_items"]) == 3

    def test_strips_markdown_fences(self):
        """Should handle JSON wrapped in ```json ... ``` fences."""
        wrapped = f"```json\n{SAMPLE_LLM_RESPONSE}\n```"
        data = parse_llm_json(wrapped)
        assert data["grand_total"] == 270.00

    def test_extracts_json_from_surrounding_text(self):
        """Should extract JSON when preceded/followed by commentary."""
        response = f"Here is the data:\n{SAMPLE_LLM_RESPONSE}\nDone."
        data = parse_llm_json(response)
        assert data["invoice_number"] == "INV-2024-0042"

    def test_raises_on_invalid_json(self):
        """Should raise ClickException when response has no valid JSON."""
        with pytest.raises(click.ClickException, match="Failed to parse JSON"):
            parse_llm_json("This is not JSON at all.")


# ---------------------------------------------------------------------------
# Tests — Invoice extraction (mocked LLM)
# ---------------------------------------------------------------------------


class TestExtractInvoiceData:
    """Tests for extract_invoice_data with a mocked LLM."""

    @patch("app.chat", return_value=SAMPLE_LLM_RESPONSE)
    def test_returns_structured_data(self, mock_chat):
        """Should return parsed dict from LLM response."""
        data = extract_invoice_data(SAMPLE_INVOICE_TEXT)

        assert data["vendor"]["name"] == "ACME Corporation"
        assert data["grand_total"] == 270.00
        assert len(data["line_items"]) == 3
        mock_chat.assert_called_once()

    @patch("app.chat", return_value=SAMPLE_LLM_RESPONSE)
    def test_passes_correct_params_to_llm(self, mock_chat):
        """Should call chat() with low temperature and appropriate system prompt."""
        extract_invoice_data("some text")

        _, kwargs = mock_chat.call_args
        assert kwargs["temperature"] == 0.1
        assert "JSON" in kwargs["system_prompt"]

    @patch("app.chat", return_value=f"```json\n{SAMPLE_LLM_RESPONSE}\n```")
    def test_handles_fenced_llm_response(self, mock_chat):
        """Should handle LLM responses wrapped in code fences."""
        data = extract_invoice_data(SAMPLE_INVOICE_TEXT)
        assert data["subtotal"] == 250.00


# ---------------------------------------------------------------------------
# Tests — Output formats
# ---------------------------------------------------------------------------


class TestJsonOutputFormat:
    """Tests for JSON output formatting."""

    @patch("app.chat", return_value=SAMPLE_LLM_RESPONSE)
    @patch("app.check_ollama_running", return_value=True)
    def test_json_output_contains_vendor(self, mock_ollama, mock_chat, tmp_path):
        """CLI --output json should produce output containing vendor name."""
        invoice = tmp_path / "inv.txt"
        invoice.write_text(SAMPLE_INVOICE_TEXT, encoding="utf-8")

        runner = CliRunner()
        result = runner.invoke(main, ["--file", str(invoice), "--output", "json"])

        assert result.exit_code == 0
        assert "ACME Corporation" in result.output


class TestTableOutputFormat:
    """Tests for table output formatting."""

    @patch("app.chat", return_value=SAMPLE_LLM_RESPONSE)
    @patch("app.check_ollama_running", return_value=True)
    def test_table_output_has_line_items(self, mock_ollama, mock_chat, tmp_path):
        """CLI --output table should render line-item descriptions."""
        invoice = tmp_path / "inv.txt"
        invoice.write_text(SAMPLE_INVOICE_TEXT, encoding="utf-8")

        runner = CliRunner()
        result = runner.invoke(main, ["--file", str(invoice), "--output", "table"])

        assert result.exit_code == 0
        assert "Widget A" in result.output
        assert "Widget B" in result.output


class TestCsvOutputFormat:
    """Tests for CSV output formatting."""

    def test_csv_header_and_rows(self, capsys):
        """format_csv should print a header row followed by item rows."""
        format_csv(EXPECTED_DATA)
        captured = capsys.readouterr().out
        lines = captured.strip().split("\n")

        assert lines[0] == "description,quantity,unit_price,total"
        assert len(lines) == 4  # header + 3 items
        assert "Widget A" in lines[1]


# ---------------------------------------------------------------------------
# Tests — CLI behaviour
# ---------------------------------------------------------------------------


class TestCli:
    """Tests for Click CLI entry-point."""

    def test_missing_file_option_exits(self):
        """CLI should exit with error when --file is not provided."""
        runner = CliRunner()
        result = runner.invoke(main, [])
        assert result.exit_code != 0
        assert "Missing" in result.output or "required" in result.output.lower() or "Error" in result.output

    def test_nonexistent_file_exits(self):
        """CLI should exit with error for a file that doesn't exist."""
        runner = CliRunner()
        result = runner.invoke(main, ["--file", "does_not_exist.txt"])
        assert result.exit_code != 0

    def test_invalid_output_format_exits(self):
        """CLI should reject an unsupported output format."""
        runner = CliRunner()
        result = runner.invoke(main, ["--file", "any.txt", "--output", "xml"])
        assert result.exit_code != 0
