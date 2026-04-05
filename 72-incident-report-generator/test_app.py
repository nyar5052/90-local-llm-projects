"""Tests for Incident Report Generator."""

import pytest
from unittest.mock import patch
from click.testing import CliRunner

from app import main, generate_report, generate_timeline


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


@patch("app.chat")
def test_generate_report(mock_chat):
    """Test incident report generation."""
    mock_chat.return_value = "# Incident Report\n## Executive Summary\nUnauthorized access detected."
    result = generate_report("SSH brute force logs", "security", "SSH Breach")
    assert "Incident Report" in result
    mock_chat.assert_called_once()


@patch("app.chat")
def test_generate_timeline(mock_chat):
    """Test timeline extraction."""
    mock_chat.return_value = "[10:23] - SSH login attempt\n[10:25] - Root access gained"
    result = generate_timeline("SSH brute force logs")
    assert "SSH" in result
    mock_chat.assert_called_once()


@patch("app.check_ollama_running", return_value=True)
@patch("app.chat", return_value="# Incident Report\nSecurity breach detected.")
def test_cli_full_report(mock_chat, mock_check, runner, sample_logs):
    """Test CLI generates full report."""
    result = runner.invoke(main, ["--logs", sample_logs, "--type", "security"])
    assert result.exit_code == 0
    mock_chat.assert_called_once()


@patch("app.check_ollama_running", return_value=True)
@patch("app.chat", return_value="[10:23] - Event 1\n[10:25] - Event 2")
def test_cli_timeline_only(mock_chat, mock_check, runner, sample_logs):
    """Test CLI with timeline-only flag."""
    result = runner.invoke(main, ["--logs", sample_logs, "--timeline-only"])
    assert result.exit_code == 0
    mock_chat.assert_called_once()


@patch("app.check_ollama_running", return_value=False)
def test_cli_ollama_not_running(mock_check, runner, sample_logs):
    """Test error when Ollama is not running."""
    result = runner.invoke(main, ["--logs", sample_logs])
    assert result.exit_code != 0
