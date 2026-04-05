"""Tests for the Compliance Checker core module."""

import json
import os
import pytest
from unittest.mock import patch

import click

from src.compliance_checker.core import (
    read_file,
    check_compliance,
    parse_compliance_response,
    filter_violations,
    get_score_color,
    get_score_label,
)

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


class TestReadFile:
    def test_read_document_file(self, tmp_document):
        content = read_file(tmp_document)
        assert "sample document" in content

    def test_read_policy_file(self, tmp_policy):
        content = read_file(tmp_policy)
        assert "data retention" in content

    def test_read_missing_file_raises(self):
        with pytest.raises(click.ClickException, match="File not found"):
            read_file("nonexistent_file_xyz.txt")


class TestCheckCompliance:
    @patch("src.compliance_checker.core.chat")
    def test_compliance_check_returns_report(self, mock_chat):
        mock_chat.return_value = json.dumps(SAMPLE_REPORT)
        result = check_compliance("document text", "policy rules")
        assert isinstance(result, dict)
        assert result["compliance_score"] == 72
        assert len(result["violations"]) == 3

    @patch("src.compliance_checker.core.chat")
    def test_compliance_check_handles_code_fences(self, mock_chat):
        fenced = f"```json\n{json.dumps(SAMPLE_REPORT)}\n```"
        mock_chat.return_value = fenced
        result = check_compliance("doc", "policy")
        assert result["compliance_score"] == 72

    @patch("src.compliance_checker.core.chat")
    def test_compliance_check_handles_invalid_json(self, mock_chat):
        mock_chat.return_value = "This is not JSON at all."
        result = check_compliance("doc", "policy")
        assert result["compliance_score"] == 0
        assert "Unable to parse" in result["summary"]


class TestSeverityFilter:
    def test_filter_all_returns_everything(self, sample_report):
        result = filter_violations(sample_report["violations"], "all")
        assert len(result) == 3

    def test_filter_high_only(self, sample_report):
        result = filter_violations(sample_report["violations"], "high")
        assert len(result) == 1
        assert result[0]["severity"] == "high"

    def test_filter_medium_only(self, sample_report):
        result = filter_violations(sample_report["violations"], "medium")
        assert len(result) == 1

    def test_filter_low_only(self, sample_report):
        result = filter_violations(sample_report["violations"], "low")
        assert len(result) == 1

    def test_filter_returns_empty_when_none_match(self):
        violations = [{"severity": "high", "rule": "X"}]
        assert filter_violations(violations, "low") == []


class TestParseResponse:
    def test_score_clamped_above_100(self):
        raw = json.dumps({"compliance_score": 150})
        result = parse_compliance_response(raw)
        assert result["compliance_score"] == 100

    def test_score_clamped_below_0(self):
        raw = json.dumps({"compliance_score": -10})
        result = parse_compliance_response(raw)
        assert result["compliance_score"] == 0

    def test_missing_keys_get_defaults(self):
        raw = json.dumps({"compliance_score": 50})
        result = parse_compliance_response(raw)
        assert result["summary"] == "No summary provided."
        assert result["violations"] == []


class TestScoreHelpers:
    def test_score_color_green(self):
        assert get_score_color(85) == "green"

    def test_score_color_yellow(self):
        assert get_score_color(65) == "yellow"

    def test_score_color_red(self):
        assert get_score_color(30) == "red"

    def test_score_label_pass(self):
        assert get_score_label(90) == "PASS"

    def test_score_label_warning(self):
        assert get_score_label(60) == "WARNING"

    def test_score_label_fail(self):
        assert get_score_label(20) == "FAIL"
