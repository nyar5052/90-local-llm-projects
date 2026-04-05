"""Tests for the Policy Compliance Checker."""

import json
import os
import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner

from app import (
    read_file,
    check_compliance,
    parse_compliance_response,
    filter_violations,
    display_report,
    main,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

SAMPLE_REPORT = {
    "compliance_score": 72,
    "summary": "Document partially complies with the policy.",
    "violations": [
        {
            "rule": "Data Retention",
            "severity": "high",
            "description": "No retention period specified.",
            "location": "Section 3",
            "remediation": "Add a data retention clause.",
        },
        {
            "rule": "Access Control",
            "severity": "medium",
            "description": "Missing role-based access details.",
            "location": "Section 5",
            "remediation": "Define RBAC roles.",
        },
        {
            "rule": "Naming Convention",
            "severity": "low",
            "description": "Inconsistent naming.",
            "location": "Throughout",
            "remediation": "Standardize naming.",
        },
    ],
    "compliant_areas": [
        {"rule": "Encryption", "description": "AES-256 encryption is used."}
    ],
    "recommendations": ["Add data retention policy.", "Define RBAC roles."],
}


@pytest.fixture
def sample_report():
    return SAMPLE_REPORT.copy()


@pytest.fixture
def tmp_document(tmp_path):
    doc = tmp_path / "doc.txt"
    doc.write_text("This is a sample document for compliance checking.", encoding="utf-8")
    return str(doc)


@pytest.fixture
def tmp_policy(tmp_path):
    pol = tmp_path / "policy.txt"
    pol.write_text("All documents must include a data retention clause.", encoding="utf-8")
    return str(pol)


# ---------------------------------------------------------------------------
# Test: File reading
# ---------------------------------------------------------------------------

class TestReadFile:
    """Tests for the read_file function."""

    def test_read_document_file(self, tmp_document):
        """read_file returns contents of a valid document file."""
        content = read_file(tmp_document)
        assert "sample document" in content

    def test_read_policy_file(self, tmp_policy):
        """read_file returns contents of a valid policy file."""
        content = read_file(tmp_policy)
        assert "data retention" in content

    def test_read_missing_file_raises(self):
        """read_file raises ClickException for a missing file."""
        import click
        with pytest.raises(click.ClickException, match="File not found"):
            read_file("nonexistent_file_xyz.txt")


# ---------------------------------------------------------------------------
# Test: Compliance check with mocked LLM
# ---------------------------------------------------------------------------

class TestCheckCompliance:
    """Tests for check_compliance with a mocked LLM."""

    @patch("app.chat")
    def test_compliance_check_returns_report(self, mock_chat):
        """check_compliance returns a parsed report dict from the LLM."""
        mock_chat.return_value = json.dumps(SAMPLE_REPORT)

        result = check_compliance("document text", "policy rules")

        assert isinstance(result, dict)
        assert result["compliance_score"] == 72
        assert len(result["violations"]) == 3
        assert len(result["compliant_areas"]) == 1
        assert len(result["recommendations"]) == 2
        mock_chat.assert_called_once()

    @patch("app.chat")
    def test_compliance_check_handles_code_fences(self, mock_chat):
        """check_compliance strips markdown code fences from LLM response."""
        fenced = f"```json\n{json.dumps(SAMPLE_REPORT)}\n```"
        mock_chat.return_value = fenced

        result = check_compliance("doc", "policy")

        assert result["compliance_score"] == 72
        assert len(result["violations"]) == 3

    @patch("app.chat")
    def test_compliance_check_handles_invalid_json(self, mock_chat):
        """check_compliance returns fallback report on unparseable response."""
        mock_chat.return_value = "This is not JSON at all."

        result = check_compliance("doc", "policy")

        assert result["compliance_score"] == 0
        assert "Unable to parse" in result["summary"]


# ---------------------------------------------------------------------------
# Test: Severity filtering
# ---------------------------------------------------------------------------

class TestSeverityFilter:
    """Tests for filter_violations."""

    def test_filter_all_returns_everything(self, sample_report):
        """severity='all' returns all violations."""
        result = filter_violations(sample_report["violations"], "all")
        assert len(result) == 3

    def test_filter_high_only(self, sample_report):
        """severity='high' returns only high-severity violations."""
        result = filter_violations(sample_report["violations"], "high")
        assert len(result) == 1
        assert result[0]["severity"] == "high"

    def test_filter_medium_only(self, sample_report):
        """severity='medium' returns only medium-severity violations."""
        result = filter_violations(sample_report["violations"], "medium")
        assert len(result) == 1
        assert result[0]["severity"] == "medium"

    def test_filter_low_only(self, sample_report):
        """severity='low' returns only low-severity violations."""
        result = filter_violations(sample_report["violations"], "low")
        assert len(result) == 1
        assert result[0]["severity"] == "low"

    def test_filter_returns_empty_when_none_match(self):
        """Filtering with no matching severity returns empty list."""
        violations = [{"severity": "high", "rule": "X"}]
        assert filter_violations(violations, "low") == []


# ---------------------------------------------------------------------------
# Test: CLI with missing files
# ---------------------------------------------------------------------------

class TestCLI:
    """Tests for the Click CLI interface."""

    def test_cli_missing_document(self, tmp_policy):
        """CLI exits with error when document file does not exist."""
        runner = CliRunner()
        result = runner.invoke(main, ["--document", "no_such_doc.txt", "--policy", tmp_policy])
        assert result.exit_code != 0

    def test_cli_missing_policy(self, tmp_document):
        """CLI exits with error when policy file does not exist."""
        runner = CliRunner()
        result = runner.invoke(main, ["--document", tmp_document, "--policy", "no_such_policy.txt"])
        assert result.exit_code != 0

    def test_cli_missing_both_args(self):
        """CLI exits with error when required options are omitted."""
        runner = CliRunner()
        result = runner.invoke(main, [])
        assert result.exit_code != 0
        assert "Missing option" in result.output or "Error" in result.output

    @patch("app.check_ollama_running", return_value=False)
    def test_cli_ollama_not_running(self, mock_check, tmp_document, tmp_policy):
        """CLI exits with error when Ollama is not available."""
        runner = CliRunner()
        result = runner.invoke(
            main, ["--document", tmp_document, "--policy", tmp_policy]
        )
        assert result.exit_code != 0


# ---------------------------------------------------------------------------
# Test: Output formatting / display
# ---------------------------------------------------------------------------

class TestDisplayReport:
    """Tests for display_report rendering."""

    def test_display_report_runs_without_error(self, sample_report, capsys):
        """display_report completes without raising exceptions."""
        display_report(sample_report, "all")

    def test_display_report_with_no_violations(self):
        """display_report shows success message when there are no violations."""
        report = {
            "compliance_score": 100,
            "summary": "Fully compliant.",
            "violations": [],
            "compliant_areas": [{"rule": "All rules", "description": "OK"}],
            "recommendations": [],
        }
        # Should not raise
        display_report(report, "all")

    def test_display_report_filters_in_output(self, sample_report):
        """display_report respects severity filter parameter."""
        # Filtering to 'high' should not raise and should process only 1 violation
        display_report(sample_report, "high")


# ---------------------------------------------------------------------------
# Test: parse_compliance_response edge cases
# ---------------------------------------------------------------------------

class TestParseResponse:
    """Tests for parse_compliance_response edge cases."""

    def test_score_clamped_above_100(self):
        """Scores above 100 are clamped to 100."""
        raw = json.dumps({"compliance_score": 150})
        result = parse_compliance_response(raw)
        assert result["compliance_score"] == 100

    def test_score_clamped_below_0(self):
        """Negative scores are clamped to 0."""
        raw = json.dumps({"compliance_score": -10})
        result = parse_compliance_response(raw)
        assert result["compliance_score"] == 0

    def test_missing_keys_get_defaults(self):
        """Missing keys are filled with sensible defaults."""
        raw = json.dumps({"compliance_score": 50})
        result = parse_compliance_response(raw)
        assert result["summary"] == "No summary provided."
        assert result["violations"] == []
        assert result["compliant_areas"] == []
        assert result["recommendations"] == []
