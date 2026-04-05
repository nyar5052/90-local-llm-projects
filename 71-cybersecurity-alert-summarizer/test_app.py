"""Tests for Cybersecurity Alert Summarizer."""

import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner

from app import main, summarize_alert, prioritize_alerts


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def sample_alert(tmp_path):
    alert_file = tmp_path / "alert.txt"
    alert_file.write_text(
        "CVE-2024-1234: Remote code execution in OpenSSL 3.0.x. "
        "CVSS Score: 9.8. Affects all Linux servers running OpenSSL 3.0.0-3.0.9."
    )
    return str(alert_file)


@patch("app.chat")
def test_summarize_alert(mock_chat):
    """Test basic alert summarization."""
    mock_chat.return_value = "## Summary\nCritical RCE vulnerability in OpenSSL."
    result = summarize_alert("CVE-2024-1234: RCE in OpenSSL", "high")
    assert "OpenSSL" in result
    mock_chat.assert_called_once()
    call_args = mock_chat.call_args
    assert call_args[1]["temperature"] == 0.3


@patch("app.chat")
def test_prioritize_alerts(mock_chat):
    """Test alert prioritization."""
    mock_chat.return_value = "1. CVE-2024-1234 - Critical\n2. CVE-2024-5678 - Medium"
    result = prioritize_alerts("CVE-2024-1234: RCE\nCVE-2024-5678: XSS")
    assert "Critical" in result
    mock_chat.assert_called_once()


@patch("app.check_ollama_running", return_value=True)
@patch("app.chat", return_value="## Summary\nHigh severity alert detected.")
def test_cli_with_file(mock_chat, mock_check, runner, sample_alert):
    """Test CLI with alert file input."""
    result = runner.invoke(main, ["--alert", sample_alert, "--severity", "high"])
    assert result.exit_code == 0
    mock_chat.assert_called_once()


@patch("app.check_ollama_running", return_value=True)
@patch("app.chat", return_value="## Priority\n1. Critical threat found.")
def test_cli_with_text_and_prioritize(mock_chat, mock_check, runner):
    """Test CLI with inline text and prioritization."""
    result = runner.invoke(main, ["--text", "Multiple CVEs detected", "--prioritize"])
    assert result.exit_code == 0
    mock_chat.assert_called_once()


@patch("app.check_ollama_running", return_value=False)
def test_cli_ollama_not_running(mock_check, runner):
    """Test error when Ollama is not running."""
    result = runner.invoke(main, ["--text", "test"])
    assert result.exit_code != 0
