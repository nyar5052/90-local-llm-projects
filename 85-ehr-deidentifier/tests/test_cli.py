"""Tests for EHR De-Identifier CLI module."""

import os
import pytest
from unittest.mock import patch
from click.testing import CliRunner

from src.ehr_deidentifier.cli import cli


class TestTextCommand:
    """Tests for the text CLI command."""

    @patch("src.ehr_deidentifier.core.check_ollama_running", return_value=True)
    @patch("src.ehr_deidentifier.core.generate", return_value="[NAME_1] visited the clinic.")
    def test_text_command(self, mock_generate, mock_ollama):
        """The text command should de-identify inline text."""
        runner = CliRunner()
        result = runner.invoke(cli, ["text", "--input", "John visited the clinic."])

        assert result.exit_code == 0
        assert mock_generate.called

    @patch("src.ehr_deidentifier.cli.check_ollama_running", return_value=False)
    def test_text_command_no_ollama(self, mock_ollama):
        """Should fail gracefully when Ollama is not running."""
        runner = CliRunner()
        result = runner.invoke(cli, ["text", "--input", "test"])

        assert result.exit_code != 0


class TestDeidentifyCommand:
    """Tests for the deidentify CLI command."""

    @patch("src.ehr_deidentifier.core.check_ollama_running", return_value=True)
    @patch("src.ehr_deidentifier.core.generate", return_value="[NAME_1] record")
    def test_deidentify_command(self, mock_generate, mock_ollama, tmp_path):
        """The deidentify command should process a file."""
        input_file = tmp_path / "input.txt"
        input_file.write_text("John Smith record", encoding="utf-8")

        runner = CliRunner()
        result = runner.invoke(cli, ["deidentify", "--file", str(input_file)])

        assert result.exit_code == 0
        assert mock_generate.called

    @patch("src.ehr_deidentifier.core.check_ollama_running", return_value=True)
    @patch("src.ehr_deidentifier.core.generate", return_value="[NAME_1] record")
    def test_deidentify_with_output(self, mock_generate, mock_ollama, tmp_path):
        """The deidentify command should write output file when specified."""
        input_file = tmp_path / "input.txt"
        input_file.write_text("John Smith record", encoding="utf-8")
        output_file = tmp_path / "output.txt"

        runner = CliRunner()
        result = runner.invoke(
            cli,
            ["deidentify", "--file", str(input_file), "--output", str(output_file)],
        )

        assert result.exit_code == 0
        assert output_file.exists()

    def test_deidentify_missing_file(self):
        """Should fail gracefully for missing input file."""
        runner = CliRunner()
        result = runner.invoke(
            cli, ["deidentify", "--file", "nonexistent_file.txt"]
        )
        # Should fail (either no ollama or file not found)
        assert result.exit_code != 0


class TestBatchCommand:
    """Tests for the batch CLI command."""

    @patch("src.ehr_deidentifier.core.check_ollama_running", return_value=True)
    @patch("src.ehr_deidentifier.core.generate", return_value="Clean text")
    def test_batch_command(self, mock_generate, mock_ollama, tmp_path):
        """Batch command should process all matching files."""
        for i in range(2):
            (tmp_path / f"record_{i}.txt").write_text(
                f"Patient {i}", encoding="utf-8"
            )

        runner = CliRunner()
        result = runner.invoke(
            cli, ["batch", "--directory", str(tmp_path)]
        )

        assert result.exit_code == 0

    @patch("src.ehr_deidentifier.core.check_ollama_running", return_value=True)
    def test_batch_empty_directory(self, mock_ollama, tmp_path):
        """Batch command should handle empty directory gracefully."""
        runner = CliRunner()
        result = runner.invoke(
            cli, ["batch", "--directory", str(tmp_path)]
        )

        assert result.exit_code == 0

    @patch("src.ehr_deidentifier.cli.check_ollama_running", return_value=False)
    def test_batch_no_ollama(self, mock_ollama, tmp_path):
        """Batch command should fail when Ollama is not running."""
        runner = CliRunner()
        result = runner.invoke(
            cli, ["batch", "--directory", str(tmp_path)]
        )

        assert result.exit_code != 0


class TestRulesCommand:
    """Tests for the rules CLI command."""

    def test_rules_command(self):
        """Rules command should list PII rules."""
        runner = CliRunner()
        result = runner.invoke(cli, ["rules"])

        assert result.exit_code == 0
        # Should contain rule names
        assert "SSN" in result.output or "Social Security" in result.output


class TestAuditCommand:
    """Tests for the audit CLI command."""

    def test_audit_command_empty(self):
        """Audit command with no entries should not crash."""
        runner = CliRunner()
        result = runner.invoke(cli, ["audit"])

        assert result.exit_code == 0


class TestValidateCommand:
    """Tests for the validate CLI command."""

    @patch("src.ehr_deidentifier.core.check_ollama_running", return_value=True)
    @patch("src.ehr_deidentifier.core.generate", return_value="De-identified text.")
    def test_validate_command(self, mock_generate, mock_ollama, tmp_path):
        """Validate command should produce a report."""
        test_file = tmp_path / "record.txt"
        test_file.write_text("Patient SSN 123-45-6789", encoding="utf-8")

        runner = CliRunner()
        result = runner.invoke(cli, ["validate", "--file", str(test_file)])

        assert result.exit_code == 0
        assert "VALIDATION REPORT" in result.output

    @patch("src.ehr_deidentifier.cli.check_ollama_running", return_value=False)
    def test_validate_no_ollama(self, mock_ollama, tmp_path):
        """Validate command should fail when Ollama is not running."""
        test_file = tmp_path / "record.txt"
        test_file.write_text("test", encoding="utf-8")

        runner = CliRunner()
        result = runner.invoke(cli, ["validate", "--file", str(test_file)])

        assert result.exit_code != 0
