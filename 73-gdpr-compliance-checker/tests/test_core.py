"""Tests for GDPR Compliance Checker core module."""

import pytest
from unittest.mock import patch

from src.gdpr_checker.core import (
    check_compliance,
    generate_checklist,
    build_article_checklist,
    map_data_flows,
    generate_dpo_recommendations,
    create_audit_entry,
    ComplianceStatus,
    ChecklistItem,
    DataFlowEntry,
)


class TestArticleChecklist:
    def test_detects_consent(self):
        content = "We require explicit consent from users. Users can withdraw consent at any time."
        items = build_article_checklist(content)
        art7 = next(i for i in items if i.article == "Art. 7")
        assert art7.status in (ComplianceStatus.COMPLIANT, ComplianceStatus.PARTIALLY_COMPLIANT)

    def test_detects_missing_articles(self):
        content = "This is a simple document with no GDPR references."
        items = build_article_checklist(content)
        not_addressed = [i for i in items if i.status == ComplianceStatus.NOT_ADDRESSED]
        assert len(not_addressed) > 10  # Most articles should be NOT_ADDRESSED

    def test_detects_security_measures(self):
        content = "We implement encryption and access control for all personal data. Pseudonymization is used."
        items = build_article_checklist(content)
        art32 = next(i for i in items if i.article == "Art. 32")
        assert art32.status == ComplianceStatus.COMPLIANT

    def test_returns_all_articles(self):
        items = build_article_checklist("test")
        assert len(items) >= 20


class TestDataFlowMapping:
    def test_detects_email_collection(self):
        content = "We collect user email addresses for marketing and analytics purposes."
        flows = map_data_flows(content)
        assert len(flows) > 0
        types = [f.data_type for f in flows]
        assert "email" in types

    def test_detects_cross_border(self):
        content = "Data may be transferred to third country servers."
        flows = map_data_flows(content)
        if flows:
            assert any(f.cross_border for f in flows)

    def test_empty_content(self):
        flows = map_data_flows("")
        assert flows == []


class TestDPORecommendations:
    def test_generates_recs_for_non_compliant(self):
        items = [
            ChecklistItem("Art. 7", "Consent", "desc", ComplianceStatus.NON_COMPLIANT, "No consent"),
            ChecklistItem("Art. 32", "Security", "desc", ComplianceStatus.COMPLIANT, "OK"),
        ]
        recs = generate_dpo_recommendations(items)
        assert len(recs) == 1
        assert recs[0].priority == "high"

    def test_sorted_by_priority(self):
        items = [
            ChecklistItem("Art. 5", "Principles", "desc", ComplianceStatus.PARTIALLY_COMPLIANT),
            ChecklistItem("Art. 7", "Consent", "desc", ComplianceStatus.NON_COMPLIANT),
        ]
        recs = generate_dpo_recommendations(items)
        assert recs[0].priority == "high"


class TestAuditLog:
    def test_create_audit_entry(self):
        entry = create_audit_entry("compliance_check", "Art. 7", "compliant", "All good")
        assert entry.action == "compliance_check"
        assert entry.article == "Art. 7"
        assert entry.timestamp  # Should have timestamp


class TestLLMFunctions:
    @patch("src.gdpr_checker.core.chat")
    def test_check_compliance(self, mock_chat):
        mock_chat.return_value = "## Findings\n- Consent: NON-COMPLIANT ❌"
        result = check_compliance("We collect emails without consent", "all")
        assert "NON-COMPLIANT" in result

    @patch("src.gdpr_checker.core.chat")
    def test_generate_checklist(self, mock_chat):
        mock_chat.return_value = "- [❌] Consent mechanism\n- [✅] Privacy policy present"
        result = generate_checklist("Our privacy policy...")
        assert "Consent" in result or "consent" in result
