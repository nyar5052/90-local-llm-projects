"""Tests for Cybersecurity Alert Summarizer core module."""

import pytest
from unittest.mock import patch, MagicMock

from src.cyber_alert.core import (
    summarize_alert,
    prioritize_alerts,
    extract_iocs,
    extract_cves,
    lookup_cve,
    calculate_threat_score,
    correlate_alerts,
    Severity,
    IOCResult,
    CVEInfo,
    ThreatScore,
)


# ---------------------------------------------------------------------------
# IOC Extraction Tests
# ---------------------------------------------------------------------------

class TestExtractIOCs:
    def test_extracts_ipv4(self):
        text = "Alert from source IP 192.168.1.100 detected."
        iocs = extract_iocs(text)
        values = [i.value for i in iocs]
        assert "192.168.1.100" in values

    def test_extracts_email(self):
        text = "Phishing email from attacker@malicious.com found."
        iocs = extract_iocs(text)
        values = [i.value for i in iocs]
        assert "attacker@malicious.com" in values

    def test_extracts_url(self):
        text = "Payload downloaded from https://evil.com/payload.exe"
        iocs = extract_iocs(text)
        types = [i.ioc_type for i in iocs]
        assert "url" in types

    def test_extracts_md5_hash(self):
        text = "File hash: d41d8cd98f00b204e9800998ecf8427e"
        iocs = extract_iocs(text)
        types = [i.ioc_type for i in iocs]
        assert "md5" in types

    def test_empty_text_returns_empty(self):
        assert extract_iocs("") == []

    def test_no_duplicates(self):
        text = "IP 10.0.0.1 seen again 10.0.0.1"
        iocs = extract_iocs(text)
        ip_iocs = [i for i in iocs if i.value == "10.0.0.1"]
        assert len(ip_iocs) == 1


# ---------------------------------------------------------------------------
# CVE Lookup Tests
# ---------------------------------------------------------------------------

class TestCVELookup:
    def test_known_cve(self):
        info = lookup_cve("CVE-2024-3094")
        assert info.found_in_db is True
        assert info.cvss == 10.0
        assert info.severity == "critical"

    def test_unknown_cve(self):
        info = lookup_cve("CVE-9999-0001")
        assert info.found_in_db is False

    def test_case_insensitive(self):
        info = lookup_cve("cve-2024-3094")
        assert info.found_in_db is True

    def test_extract_cves_from_text(self):
        text = "Found CVE-2024-3094 and CVE-2024-21762 in the scan."
        cves = extract_cves(text)
        cve_ids = [c.cve_id for c in cves]
        assert "CVE-2024-3094" in cve_ids
        assert "CVE-2024-21762" in cve_ids


# ---------------------------------------------------------------------------
# Threat Scoring Tests
# ---------------------------------------------------------------------------

class TestThreatScoring:
    def test_critical_threat(self):
        text = "CVE-2024-3094 remote code execution backdoor from 192.168.1.1"
        score = calculate_threat_score(text)
        assert score.overall_score > 5.0
        assert score.severity in (Severity.CRITICAL, Severity.HIGH)

    def test_low_threat(self):
        text = "Info: routine log rotation completed successfully."
        score = calculate_threat_score(text)
        assert score.overall_score < 3.0

    def test_score_has_factors(self):
        score = calculate_threat_score("Test alert with CVE-2024-3094")
        assert "cve_severity" in score.factors
        assert "keyword_severity" in score.factors

    def test_threat_score_label(self):
        score = ThreatScore(overall_score=9.5)
        assert score.label == "CRITICAL"
        score = ThreatScore(overall_score=2.0)
        assert score.label == "LOW"


# ---------------------------------------------------------------------------
# Alert Correlation Tests
# ---------------------------------------------------------------------------

class TestAlertCorrelation:
    def test_shared_iocs(self):
        alerts = [
            "Attack from 192.168.1.100 detected",
            "Brute force from 192.168.1.100 on port 22",
        ]
        corrs = correlate_alerts(alerts)
        assert len(corrs) > 0
        assert corrs[0].correlation_type == "shared_iocs"

    def test_no_correlation(self):
        alerts = ["Alert one about system A", "Alert two about system B"]
        corrs = correlate_alerts(alerts)
        assert len(corrs) == 0


# ---------------------------------------------------------------------------
# LLM-based Function Tests (mocked)
# ---------------------------------------------------------------------------

class TestSummarizeAlert:
    @patch("src.cyber_alert.core.chat")
    def test_summarize_alert(self, mock_chat):
        mock_chat.return_value = "## Summary\nCritical RCE vulnerability in OpenSSL."
        result = summarize_alert("CVE-2024-1234: RCE in OpenSSL", "high")
        assert "OpenSSL" in result
        mock_chat.assert_called_once()
        assert mock_chat.call_args[1]["temperature"] == 0.3

    @patch("src.cyber_alert.core.chat")
    def test_prioritize_alerts(self, mock_chat):
        mock_chat.return_value = "1. CVE-2024-1234 - Critical\n2. CVE-2024-5678 - Medium"
        result = prioritize_alerts("CVE-2024-1234: RCE\nCVE-2024-5678: XSS")
        assert "Critical" in result
        mock_chat.assert_called_once()
