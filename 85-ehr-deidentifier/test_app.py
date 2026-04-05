"""Tests for EHR De-Identifier."""

import os
import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner

from app import cli, regex_preprocess, deidentify_text, read_file, write_file


# --- Regex Pre-Processing Tests ---

class TestRegexPreprocess:
    """Tests for regex-based PII detection."""

    def test_ssn_detection(self):
        """SSNs in XXX-XX-XXXX format should be replaced."""
        text = "Patient SSN: 123-45-6789"
        processed, replacements = regex_preprocess(text)

        assert "123-45-6789" not in processed
        assert "[SSN_1]" in processed
        assert len(replacements) == 1
        assert replacements[0]["type"] == "SSN"
        assert replacements[0]["original"] == "123-45-6789"

    def test_phone_detection(self):
        """Phone numbers in common formats should be replaced."""
        text = "Call (555) 123-4567 or 555-987-6543"
        processed, replacements = regex_preprocess(text)

        phone_replacements = [r for r in replacements if r["type"] == "PHONE"]
        assert len(phone_replacements) == 2
        assert "(555) 123-4567" not in processed
        assert "555-987-6543" not in processed

    def test_email_detection(self):
        """Email addresses should be replaced."""
        text = "Contact john.doe@hospital.com for details"
        processed, replacements = regex_preprocess(text)

        assert "john.doe@hospital.com" not in processed
        assert "[EMAIL_1]" in processed
        assert replacements[0]["type"] == "EMAIL"

    def test_date_detection(self):
        """Dates in MM/DD/YYYY and text formats should be replaced."""
        text = "DOB: 01/15/1980, visit on March 22, 2024"
        processed, replacements = regex_preprocess(text)

        date_replacements = [r for r in replacements if r["type"] == "DATE"]
        assert len(date_replacements) == 2
        assert "01/15/1980" not in processed
        assert "March 22, 2024" not in processed

    def test_no_pii_unchanged(self):
        """Text without PII should remain unchanged."""
        text = "Patient presented with chronic headache and nausea."
        processed, replacements = regex_preprocess(text)

        assert processed == text
        assert len(replacements) == 0


# --- De-identification with Mocked LLM ---

class TestDeidentifyText:
    """Tests for full de-identification pipeline with mocked LLM."""

    @patch("app.generate")
    def test_deidentify_with_llm(self, mock_generate):
        """De-identification should combine regex and LLM results."""
        mock_generate.return_value = (
            "Patient [NAME_1], SSN: [SSN_1], visited [ADDRESS_1] clinic."
        )

        result = deidentify_text(
            "Patient John Smith, SSN: 123-45-6789, visited Springfield clinic."
        )

        assert result["original"] == (
            "Patient John Smith, SSN: 123-45-6789, visited Springfield clinic."
        )
        assert "123-45-6789" not in result["regex_processed"]
        assert mock_generate.called
        assert "final" in result

    @patch("app.generate", side_effect=Exception("LLM down"))
    def test_deidentify_llm_failure_falls_back(self, mock_generate):
        """When LLM fails, regex-only result should be returned."""
        result = deidentify_text("SSN: 999-88-7777, email: test@test.com")

        assert "999-88-7777" not in result["final"]
        assert "test@test.com" not in result["final"]
        assert "[SSN_1]" in result["final"]
        assert "[EMAIL_1]" in result["final"]


# --- File I/O Tests ---

class TestFileIO:
    """Tests for file reading and writing."""

    def test_read_file(self, tmp_path):
        """Reading an existing file should return its content."""
        test_file = tmp_path / "record.txt"
        test_file.write_text("Patient data here", encoding="utf-8")

        content = read_file(str(test_file))
        assert content == "Patient data here"

    def test_read_file_not_found(self):
        """Reading a non-existent file should raise FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            read_file("nonexistent_file_xyz.txt")

    def test_write_file(self, tmp_path):
        """Writing a file should create it with correct content."""
        output_file = tmp_path / "output.txt"
        write_file(str(output_file), "De-identified content")

        assert output_file.read_text(encoding="utf-8") == "De-identified content"


# --- CLI Tests ---

class TestCLI:
    """Tests for the CLI interface."""

    @patch("app.check_ollama_running", return_value=True)
    @patch("app.generate", return_value="[NAME_1] visited the clinic.")
    def test_text_command(self, mock_generate, mock_ollama):
        """The text command should de-identify inline text."""
        runner = CliRunner()
        result = runner.invoke(cli, ["text", "--input", "John visited the clinic."])

        assert result.exit_code == 0
        assert mock_generate.called

    @patch("app.check_ollama_running", return_value=False)
    def test_text_command_no_ollama(self, mock_ollama):
        """Should fail gracefully when Ollama is not running."""
        runner = CliRunner()
        result = runner.invoke(cli, ["text", "--input", "test"])

        assert result.exit_code != 0

    @patch("app.check_ollama_running", return_value=True)
    @patch("app.generate", return_value="[NAME_1] record")
    def test_deidentify_command(self, mock_generate, mock_ollama, tmp_path):
        """The deidentify command should process a file."""
        input_file = tmp_path / "input.txt"
        input_file.write_text("John Smith record", encoding="utf-8")

        runner = CliRunner()
        result = runner.invoke(cli, ["deidentify", "--file", str(input_file)])

        assert result.exit_code == 0
        assert mock_generate.called
