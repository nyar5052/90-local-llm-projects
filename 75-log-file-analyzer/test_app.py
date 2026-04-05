"""Tests for Log File Analyzer."""

import pytest
from unittest.mock import patch
from click.testing import CliRunner

from app import main, analyze_logs, cluster_errors, read_log_file


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def sample_log(tmp_path):
    log_file = tmp_path / "server.log"
    log_file.write_text(
        "2024-01-15 10:00:01 ERROR: Database connection timeout after 30s\n"
        "2024-01-15 10:00:05 ERROR: Database connection timeout after 30s\n"
        "2024-01-15 10:00:10 WARN: High memory usage: 92%\n"
        "2024-01-15 10:01:00 ERROR: HTTP 500 Internal Server Error /api/users\n"
        "2024-01-15 10:01:15 INFO: Request completed in 2.5s\n"
    )
    return str(log_file)


@patch("app.chat")
def test_analyze_logs(mock_chat):
    """Test log analysis."""
    mock_chat.return_value = "## Findings\n- Database timeout errors detected."
    result = analyze_logs("ERROR: DB timeout", "errors")
    assert "timeout" in result.lower() or "Findings" in result
    mock_chat.assert_called_once()


@patch("app.chat")
def test_cluster_errors(mock_chat):
    """Test error clustering."""
    mock_chat.return_value = "## Cluster 1: DB Timeouts\n- Count: 5\n- Cause: Connection pool"
    result = cluster_errors("ERROR: DB timeout\nERROR: DB timeout")
    assert "Cluster" in result
    mock_chat.assert_called_once()


def test_read_log_file_last_n(tmp_path):
    """Test reading last N lines."""
    log_file = tmp_path / "test.log"
    log_file.write_text("line1\nline2\nline3\nline4\nline5\n")
    content = read_log_file(str(log_file), last_n=2)
    assert "line4" in content
    assert "line5" in content
    assert "line1" not in content


@patch("app.check_ollama_running", return_value=True)
@patch("app.chat", return_value="## Analysis\n3 error patterns found.")
def test_cli_analyze(mock_chat, mock_check, runner, sample_log):
    """Test CLI log analysis."""
    result = runner.invoke(main, ["--file", sample_log, "--focus", "errors", "--last", "1000"])
    assert result.exit_code == 0
    mock_chat.assert_called_once()


@patch("app.check_ollama_running", return_value=False)
def test_cli_ollama_not_running(mock_check, runner, sample_log):
    """Test error when Ollama is not running."""
    result = runner.invoke(main, ["--file", sample_log])
    assert result.exit_code != 0
