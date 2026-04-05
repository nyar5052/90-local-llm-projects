"""Tests for Incident Report Generator CLI."""

import pytest
from unittest.mock import patch
from click.testing import CliRunner

from src.incident_reporter.cli import main


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def sample_logs(tmp_path):
    log_file = tmp_path / "incident_logs.txt"
    log_file.write_text(
        "2024-01-15 10:23:45 ALERT: Unauthorized SSH login from 192.168.1.100\n"
        "2024-01-15 10:24:01 WARN: Multiple failed auth attempts detected\n"
        "2024-01-15 10:25:30 CRITICAL: Root access gained from external IP\n"
    )
    return str(log_file)


class TestCLI:
    @patch("src.incident_reporter.cli.check_ollama_running", return_value=True)
    @patch("src.incident_reporter.core.chat", return_value="# Incident Report\nSecurity breach detected.")
    def test_cli_full_report(self, mock_chat, mock_check, runner, sample_logs):
        result = runner.invoke(main, ["--logs", sample_logs, "--type", "security"])
        assert result.exit_code == 0

    @patch("src.incident_reporter.cli.check_ollama_running", return_value=True)
    @patch("src.incident_reporter.core.chat", return_value="[10:23] - Event 1\n[10:25] - Event 2")
    def test_cli_timeline_only(self, mock_chat, mock_check, runner, sample_logs):
        result = runner.invoke(main, ["--logs", sample_logs, "--timeline-only"])
        assert result.exit_code == 0

    def test_cli_impact_assessment(self, runner, sample_logs):
        result = runner.invoke(main, ["--logs", sample_logs, "--impact", "--affected-users", "500"])
        assert result.exit_code == 0

    @patch("src.incident_reporter.cli.check_ollama_running", return_value=False)
    def test_cli_ollama_not_running(self, mock_check, runner, sample_logs):
        result = runner.invoke(main, ["--logs", sample_logs])
        assert result.exit_code != 0
