"""Tests for Log File Analyzer CLI."""

import pytest
from unittest.mock import patch
from click.testing import CliRunner

from src.log_analyzer.cli import main


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


class TestCLI:
    @patch("src.log_analyzer.cli.check_ollama_running", return_value=True)
    @patch("src.log_analyzer.core.chat", return_value="## Analysis\n3 error patterns found.")
    def test_cli_analyze(self, mock_chat, mock_check, runner, sample_log):
        result = runner.invoke(main, ["--file", sample_log, "--focus", "errors"])
        assert result.exit_code == 0

    def test_cli_patterns(self, runner, sample_log):
        result = runner.invoke(main, ["--file", sample_log, "--patterns"])
        assert result.exit_code == 0

    def test_cli_anomalies(self, runner, sample_log):
        result = runner.invoke(main, ["--file", sample_log, "--anomalies"])
        assert result.exit_code == 0

    def test_cli_timeline(self, runner, sample_log):
        result = runner.invoke(main, ["--file", sample_log, "--timeline"])
        assert result.exit_code == 0

    def test_cli_alerts(self, runner, sample_log):
        result = runner.invoke(main, ["--file", sample_log, "--alerts"])
        assert result.exit_code == 0

    @patch("src.log_analyzer.cli.check_ollama_running", return_value=False)
    def test_cli_ollama_not_running(self, mock_check, runner, sample_log):
        result = runner.invoke(main, ["--file", sample_log])
        assert result.exit_code != 0
