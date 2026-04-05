"""Tests for EHR De-Identifier core module."""

import os
import json
import pytest
from unittest.mock import patch, MagicMock

from src.ehr_deidentifier.core import (
    regex_preprocess,
    configurable_regex_preprocess,
    deidentify_text,
    read_file,
    write_file,
    batch_deidentify,
    AuditLog,
    ValidationReport,
    DEFAULT_PII_RULES,
    HIPAA_IDENTIFIERS,
    DISCLAIMER,
    SYSTEM_PROMPT,
)


# =========================================================================
# Regex Pre-Processing Tests (original function)
# =========================================================================
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

    def test_ssn_with_spaces(self):
        """SSNs with spaces should also be detected."""
        text = "SSN is 123 45 6789"
        processed, replacements = regex_preprocess(text)

        assert "123 45 6789" not in processed
        ssn_replacements = [r for r in replacements if r["type"] == "SSN"]
        assert len(ssn_replacements) == 1

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

    def test_date_numeric_detection(self):
        """Numeric dates should be replaced."""
        text = "DOB: 01/15/1980"
        processed, replacements = regex_preprocess(text)

        assert "01/15/1980" not in processed
        date_replacements = [r for r in replacements if r["type"] == "DATE"]
        assert len(date_replacements) == 1

    def test_date_text_detection(self):
        """Text dates should be replaced."""
        text = "Visit on March 22, 2024"
        processed, replacements = regex_preprocess(text)

        assert "March 22, 2024" not in processed
        date_replacements = [r for r in replacements if r["type"] == "DATE"]
        assert len(date_replacements) == 1

    def test_multiple_dates(self):
        """Multiple dates should all be detected."""
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

    def test_mixed_pii(self):
        """Multiple PII types in one text should all be detected."""
        text = "John Smith, SSN 123-45-6789, phone (555) 123-4567, email john@test.com"
        processed, replacements = regex_preprocess(text)

        assert "123-45-6789" not in processed
        assert "(555) 123-4567" not in processed
        assert "john@test.com" not in processed
        assert len(replacements) >= 3


# =========================================================================
# Configurable Regex Pre-Processing Tests
# =========================================================================
class TestConfigurableRegexPreprocess:
    """Tests for configurable regex-based PII detection."""

    def test_default_rules(self):
        """Default rules should detect standard PII patterns."""
        text = "SSN: 123-45-6789, email: test@test.com"
        processed, replacements = configurable_regex_preprocess(text)

        assert "123-45-6789" not in processed
        assert "test@test.com" not in processed
        assert len(replacements) >= 2

    def test_disabled_rule(self):
        """Disabled rules should not detect PII."""
        import copy
        rules = copy.deepcopy(DEFAULT_PII_RULES)
        rules["ssn"]["enabled"] = False

        text = "SSN: 123-45-6789, email: test@test.com"
        processed, replacements = configurable_regex_preprocess(text, rules)

        # SSN should still be present since rule is disabled
        assert "123-45-6789" in processed
        # Email should be caught
        assert "test@test.com" not in processed

    def test_mrn_detection(self):
        """Medical Record Numbers should be detected."""
        text = "MRN: 12345678"
        processed, replacements = configurable_regex_preprocess(text)

        mrn_replacements = [r for r in replacements if r["type"] == "MRN"]
        assert len(mrn_replacements) == 1
        assert "12345678" not in processed

    def test_ip_address_detection(self):
        """IP addresses should be detected."""
        text = "Login from 192.168.1.100"
        processed, replacements = configurable_regex_preprocess(text)

        ip_replacements = [r for r in replacements if r["type"] == "IP"]
        assert len(ip_replacements) == 1
        assert "192.168.1.100" not in processed

    def test_url_detection(self):
        """URLs should be detected."""
        text = "Visit https://patient-portal.example.com/records"
        processed, replacements = configurable_regex_preprocess(text)

        url_replacements = [r for r in replacements if r["type"] == "URL"]
        assert len(url_replacements) == 1
        assert "https://patient-portal.example.com/records" not in processed

    def test_replacement_includes_rule_name(self):
        """Replacements from configurable version should include rule name."""
        text = "SSN: 123-45-6789"
        _, replacements = configurable_regex_preprocess(text)

        assert len(replacements) >= 1
        assert "rule" in replacements[0]

    def test_custom_rules_only(self):
        """Custom rules dict should be used exclusively."""
        custom_rules = {
            "custom_id": {
                "enabled": True,
                "pattern": r"ID-\d{4}",
                "placeholder": "CUSTOM",
                "description": "Custom ID format",
            }
        }
        text = "Record ID-1234 for SSN 123-45-6789"
        processed, replacements = configurable_regex_preprocess(text, custom_rules)

        # Only custom rule should match
        assert "ID-1234" not in processed
        # SSN should still be present (no SSN rule in custom rules)
        assert "123-45-6789" in processed
        assert len(replacements) == 1
        assert replacements[0]["type"] == "CUSTOM"

    def test_empty_text(self):
        """Empty text should return empty results."""
        processed, replacements = configurable_regex_preprocess("")
        assert processed == ""
        assert len(replacements) == 0


# =========================================================================
# De-identification with Mocked LLM
# =========================================================================
class TestDeidentifyText:
    """Tests for full de-identification pipeline with mocked LLM."""

    @patch("src.ehr_deidentifier.core.generate")
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

    @patch("src.ehr_deidentifier.core.generate", side_effect=Exception("LLM down"))
    def test_deidentify_llm_failure_falls_back(self, mock_generate):
        """When LLM fails, regex-only result should be returned."""
        result = deidentify_text("SSN: 999-88-7777, email: test@test.com")

        assert "999-88-7777" not in result["final"]
        assert "test@test.com" not in result["final"]
        assert "[SSN_1]" in result["final"]
        assert "[EMAIL_1]" in result["final"]

    @patch("src.ehr_deidentifier.core.generate")
    def test_deidentify_returns_all_keys(self, mock_generate):
        """Result dict should have all expected keys."""
        mock_generate.return_value = "De-identified text."

        result = deidentify_text("Some text with SSN 123-45-6789")

        assert "original" in result
        assert "regex_processed" in result
        assert "final" in result
        assert "regex_replacements" in result

    @patch("src.ehr_deidentifier.core.generate")
    def test_deidentify_no_pii(self, mock_generate):
        """Text without PII should still go through pipeline."""
        mock_generate.return_value = "Patient has chronic headache."

        result = deidentify_text("Patient has chronic headache.")

        assert result["original"] == "Patient has chronic headache."
        assert len(result["regex_replacements"]) == 0


# =========================================================================
# Audit Log Tests
# =========================================================================
class TestAuditLog:
    """Tests for the AuditLog class."""

    def test_log_operation(self):
        """Logging an operation should create an entry."""
        audit = AuditLog()
        pii = [{"type": "SSN", "original": "123-45-6789", "placeholder": "[SSN_1]"}]

        entry = audit.log_operation("test", "test_source", pii, "success")

        assert entry["operation"] == "test"
        assert entry["input_source"] == "test_source"
        assert entry["pii_count"] == 1
        assert "SSN" in entry["pii_types_found"]
        assert entry["status"] == "success"
        assert "timestamp" in entry

    def test_get_log(self):
        """Get log should return all entries."""
        audit = AuditLog()
        audit.log_operation("op1", "src1", [], "success")
        audit.log_operation("op2", "src2", [], "error")

        log = audit.get_log()
        assert len(log) == 2

    def test_empty_summary(self):
        """Empty audit log should return minimal summary."""
        audit = AuditLog()
        summary = audit.get_summary()

        assert summary["total_operations"] == 0

    def test_summary_with_entries(self):
        """Summary should aggregate statistics correctly."""
        audit = AuditLog()
        pii1 = [
            {"type": "SSN", "original": "x", "placeholder": "y"},
            {"type": "EMAIL", "original": "x", "placeholder": "y"},
        ]
        pii2 = [{"type": "SSN", "original": "x", "placeholder": "y"}]

        audit.log_operation("op1", "src1", pii1, "success")
        audit.log_operation("op2", "src2", pii2, "success")
        audit.log_operation("op3", "src3", [], "error")

        summary = audit.get_summary()

        assert summary["total_operations"] == 3
        assert summary["total_pii_found"] == 3
        assert summary["success_count"] == 2
        assert summary["error_count"] == 1
        assert "SSN" in summary["pii_type_frequency"]
        assert summary["pii_type_frequency"]["SSN"] == 2

    def test_export_log(self, tmp_path):
        """Export should write valid JSON."""
        audit = AuditLog()
        audit.log_operation("test", "src", [], "success")

        filepath = str(tmp_path / "audit.json")
        audit.export_log(filepath)

        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert len(data) == 1
        assert data[0]["operation"] == "test"


# =========================================================================
# Validation Report Tests
# =========================================================================
class TestValidationReport:
    """Tests for the ValidationReport class."""

    def test_clean_report(self):
        """Fully de-identified text should produce clean report."""
        report = ValidationReport(
            original="Patient SSN 123-45-6789, email test@test.com",
            deidentified="Patient SSN [SSN_1], email [EMAIL_1]",
            replacements=[
                {"type": "SSN", "original": "123-45-6789", "placeholder": "[SSN_1]"},
                {"type": "EMAIL", "original": "test@test.com", "placeholder": "[EMAIL_1]"},
            ],
        )

        check = report.check_completeness()
        assert check["is_clean"] is True
        assert check["total_replacements"] == 2

    def test_dirty_report(self):
        """Text with remaining PII should flag issues."""
        report = ValidationReport(
            original="SSN 123-45-6789",
            deidentified="SSN 123-45-6789",  # not replaced
            replacements=[],
        )

        check = report.check_completeness()
        assert check["is_clean"] is False
        assert len(check["remaining_issues"]) > 0

    def test_generate_report_string(self):
        """Report should produce a non-empty string."""
        report = ValidationReport(
            original="Test",
            deidentified="Test",
            replacements=[],
        )

        text = report.generate_report()
        assert "VALIDATION REPORT" in text
        assert "NOT certified for HIPAA" in text

    def test_report_contains_disclaimer(self):
        """Report must contain manual review warning."""
        report = ValidationReport("a", "b", [])
        text = report.generate_report()

        assert "Manual review is ALWAYS required" in text


# =========================================================================
# Batch De-identification Tests
# =========================================================================
class TestBatchDeidentify:
    """Tests for batch file processing."""

    @patch("src.ehr_deidentifier.core.generate")
    def test_batch_single_file(self, mock_generate, tmp_path):
        """Batch with one file should produce one result."""
        mock_generate.return_value = "De-identified."

        test_file = tmp_path / "record.txt"
        test_file.write_text("Patient SSN 123-45-6789", encoding="utf-8")

        results = batch_deidentify([str(test_file)])

        assert len(results) == 1
        assert results[0]["status"] == "success"
        assert results[0]["source_file"] == str(test_file)

    @patch("src.ehr_deidentifier.core.generate")
    def test_batch_with_output_dir(self, mock_generate, tmp_path):
        """Batch with output dir should create output files."""
        mock_generate.return_value = "Clean text."

        test_file = tmp_path / "record.txt"
        test_file.write_text("Patient data", encoding="utf-8")
        output_dir = str(tmp_path / "output")

        results = batch_deidentify([str(test_file)], output_dir=output_dir)

        assert results[0]["status"] == "success"
        assert "output_file" in results[0]
        assert os.path.isfile(results[0]["output_file"])

    @patch("src.ehr_deidentifier.core.generate")
    def test_batch_with_audit(self, mock_generate, tmp_path):
        """Batch with audit log should record entries."""
        mock_generate.return_value = "Clean."

        test_file = tmp_path / "record.txt"
        test_file.write_text("SSN 123-45-6789", encoding="utf-8")
        audit = AuditLog()

        batch_deidentify([str(test_file)], audit=audit)

        assert len(audit.get_log()) == 1

    def test_batch_missing_file(self):
        """Batch with missing file should record error."""
        results = batch_deidentify(["nonexistent_file.txt"])

        assert len(results) == 1
        assert results[0]["status"] == "error"

    @patch("src.ehr_deidentifier.core.generate")
    def test_batch_multiple_files(self, mock_generate, tmp_path):
        """Batch with multiple files should process all."""
        mock_generate.return_value = "Clean."

        files = []
        for i in range(3):
            f = tmp_path / f"record_{i}.txt"
            f.write_text(f"Patient {i} SSN 123-45-678{i}", encoding="utf-8")
            files.append(str(f))

        results = batch_deidentify(files)
        assert len(results) == 3
        assert all(r["status"] == "success" for r in results)


# =========================================================================
# File I/O Tests
# =========================================================================
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

    def test_write_file_creates_directories(self, tmp_path):
        """Writing a file in nested dirs should create them."""
        output_file = tmp_path / "sub" / "dir" / "output.txt"
        write_file(str(output_file), "content")

        assert output_file.read_text(encoding="utf-8") == "content"


# =========================================================================
# Constants and configuration tests
# =========================================================================
class TestConstants:
    """Tests for module constants."""

    def test_hipaa_identifiers_count(self):
        """HIPAA Safe Harbor should list 18 identifiers."""
        assert len(HIPAA_IDENTIFIERS) == 18

    def test_default_rules_present(self):
        """Default rules should include essential PII types."""
        assert "ssn" in DEFAULT_PII_RULES
        assert "phone" in DEFAULT_PII_RULES
        assert "email" in DEFAULT_PII_RULES
        assert "date_numeric" in DEFAULT_PII_RULES
        assert "date_text" in DEFAULT_PII_RULES

    def test_disclaimer_not_empty(self):
        """Disclaimer constant should be non-empty."""
        assert len(DISCLAIMER) > 50

    def test_system_prompt_not_empty(self):
        """System prompt should be non-empty."""
        assert len(SYSTEM_PROMPT) > 50
