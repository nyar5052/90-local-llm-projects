"""Tests for Log File Analyzer core module."""

import pytest
from unittest.mock import patch

from src.log_analyzer.core import (
    analyze_logs,
    cluster_errors,
    read_log_file,
    match_patterns,
    detect_anomalies,
    cluster_errors_local,
    build_timeline,
    evaluate_alert_rules,
    LogLevel,
    PatternMatch,
    ErrorCluster,
    AnomalyResult,
)

SAMPLE_LOGS = (
    "2024-01-15 10:00:01 ERROR: Database connection timeout after 30s\n"
    "2024-01-15 10:00:05 ERROR: Database connection timeout after 30s\n"
    "2024-01-15 10:00:10 WARN: High memory usage: 92%\n"
    "2024-01-15 10:01:00 ERROR: HTTP 500 Internal Server Error /api/users\n"
    "2024-01-15 10:01:15 INFO: Request completed in 2.5s\n"
    "2024-01-15 10:02:00 CRITICAL: Out of memory - process killed\n"
    "2024-01-15 10:02:05 ERROR: Connection refused to redis:6379\n"
)


class TestPatternMatching:
    def test_detects_database_error(self):
        matches = match_patterns(SAMPLE_LOGS)
        patterns = [m.pattern_name for m in matches]
        assert "database_error" in patterns or "timeout" in patterns

    def test_detects_http_error(self):
        matches = match_patterns(SAMPLE_LOGS)
        patterns = [m.pattern_name for m in matches]
        assert "http_error" in patterns

    def test_detects_memory_issue(self):
        matches = match_patterns(SAMPLE_LOGS)
        patterns = [m.pattern_name for m in matches]
        assert "memory_issue" in patterns

    def test_detects_connection_error(self):
        matches = match_patterns(SAMPLE_LOGS)
        patterns = [m.pattern_name for m in matches]
        assert "connection_error" in patterns

    def test_empty_logs(self):
        assert match_patterns("") == []

    def test_no_matches(self):
        matches = match_patterns("2024-01-15 10:00:00 INFO: Everything is fine\n")
        assert len(matches) == 0


class TestAnomalyDetection:
    def test_error_burst(self):
        burst_logs = "\n".join(
            f"2024-01-15 10:00:{i:02d} ERROR: Error {i}" for i in range(10)
        )
        anomalies = detect_anomalies(burst_logs)
        types = [a.anomaly_type for a in anomalies]
        assert "error_burst" in types

    def test_repeated_message(self):
        repeated = "\n".join(["ERROR: Same error message"] * 15)
        anomalies = detect_anomalies(repeated)
        types = [a.anomaly_type for a in anomalies]
        assert "repeated_message" in types

    def test_no_anomalies(self):
        clean_logs = "2024-01-15 10:00:00 INFO: All good\n2024-01-15 10:01:00 INFO: Still good\n"
        anomalies = detect_anomalies(clean_logs)
        assert len(anomalies) == 0


class TestErrorClustering:
    def test_clusters_similar_errors(self):
        clusters = cluster_errors_local(SAMPLE_LOGS)
        assert len(clusters) > 0
        # DB timeout should cluster
        db_cluster = [c for c in clusters if c.count >= 2]
        assert len(db_cluster) > 0

    def test_cluster_severity(self):
        logs = "2024-01-15 10:00:00 CRITICAL: Fatal error\n2024-01-15 10:00:01 CRITICAL: Fatal error\n"
        clusters = cluster_errors_local(logs)
        if clusters:
            assert clusters[0].severity == LogLevel.CRITICAL


class TestTimeline:
    def test_builds_timeline(self):
        events = build_timeline(SAMPLE_LOGS)
        assert len(events) > 0
        assert events[0].timestamp.startswith("2024-01-15")

    def test_empty_logs(self):
        events = build_timeline("")
        assert events == []


class TestAlertRules:
    def test_critical_alert_triggers(self):
        rules = evaluate_alert_rules(SAMPLE_LOGS)
        critical_rule = next(r for r in rules if r.name == "Critical Events")
        assert critical_rule.current_value >= 1

    def test_error_rate_alert(self):
        many_errors = "\n".join(f"ERROR: Error {i}" for i in range(20))
        rules = evaluate_alert_rules(many_errors)
        error_rule = next(r for r in rules if r.name == "Error Rate")
        assert error_rule.triggered is True


class TestReadLogFile:
    def test_read_last_n(self, tmp_path):
        log_file = tmp_path / "test.log"
        log_file.write_text("line1\nline2\nline3\nline4\nline5\n")
        content = read_log_file(str(log_file), last_n=2)
        assert "line4" in content
        assert "line5" in content
        assert "line1" not in content


class TestLLMFunctions:
    @patch("src.log_analyzer.core.chat")
    def test_analyze_logs(self, mock_chat):
        mock_chat.return_value = "## Findings\n- Database timeout errors detected."
        result = analyze_logs("ERROR: DB timeout", "errors")
        assert "timeout" in result.lower() or "Findings" in result

    @patch("src.log_analyzer.core.chat")
    def test_cluster_errors(self, mock_chat):
        mock_chat.return_value = "## Cluster 1: DB Timeouts\n- Count: 5"
        result = cluster_errors("ERROR: DB timeout\nERROR: DB timeout")
        assert "Cluster" in result
