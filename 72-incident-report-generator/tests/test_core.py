"""Tests for Incident Report Generator core module."""

import pytest
from unittest.mock import patch

from src.incident_reporter.core import (
    generate_report,
    generate_timeline,
    build_timeline,
    calculate_impact,
    generate_lessons_learned,
    get_template,
    Priority,
    TimelineEntry,
    ImpactAssessment,
    INCIDENT_TYPES,
)


class TestBuildTimeline:
    def test_parses_standard_log(self):
        logs = (
            "2024-01-15 10:23:45 ALERT: Unauthorized SSH login from 192.168.1.100\n"
            "2024-01-15 10:24:01 WARN: Multiple failed auth attempts detected\n"
            "2024-01-15 10:25:30 CRITICAL: Root access gained from external IP\n"
        )
        entries = build_timeline(logs)
        assert len(entries) == 3
        assert entries[0].severity == "alert"
        assert entries[2].severity == "critical"

    def test_empty_logs(self):
        assert build_timeline("") == []

    def test_non_matching_lines(self):
        assert build_timeline("just some random text\nno timestamps here") == []


class TestCalculateImpact:
    def test_data_breach_detected(self):
        logs = "CRITICAL: data breach detected, PII exposed"
        result = calculate_impact(logs, affected_users=5000, downtime_minutes=120)
        assert result.data_compromised is True
        assert result.severity_score > 5.0

    def test_low_impact(self):
        logs = "INFO: routine maintenance completed"
        result = calculate_impact(logs, affected_users=0, downtime_minutes=0)
        assert result.severity_score < 3.0

    def test_severity_label(self):
        a = ImpactAssessment(severity_score=9.5)
        assert a.severity_label == "CATASTROPHIC"
        a = ImpactAssessment(severity_score=2.0)
        assert a.severity_label == "MINOR"


class TestPriorityTemplates:
    def test_p1_template(self):
        t = get_template(Priority.P1)
        assert "15 minutes" in t["response_time"]
        assert "CISO" in t["escalation"]

    def test_p4_template(self):
        t = get_template(Priority.P4)
        assert "Next business day" in t["response_time"]


class TestLLMFunctions:
    @patch("src.incident_reporter.core.chat")
    def test_generate_report(self, mock_chat):
        mock_chat.return_value = "# Incident Report\n## Executive Summary\nBreach detected."
        result = generate_report("SSH brute force logs", "security", "SSH Breach")
        assert "Incident Report" in result
        mock_chat.assert_called_once()

    @patch("src.incident_reporter.core.chat")
    def test_generate_timeline(self, mock_chat):
        mock_chat.return_value = "[10:23] - SSH login attempt\n[10:25] - Root access gained"
        result = generate_timeline("SSH brute force logs")
        assert "SSH" in result

    @patch("src.incident_reporter.core.chat")
    def test_generate_lessons_learned(self, mock_chat):
        mock_chat.return_value = "## Detection\n- Lesson 1: Improve monitoring"
        result = generate_lessons_learned("incident data", "security")
        assert "Detection" in result or "Lesson" in result
