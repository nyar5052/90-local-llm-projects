"""Tests for Cybersecurity Alert Summarizer CLI."""

import pytest
from unittest.mock import patch
from click.testing import CliRunner

from src.cyber_alert.cli import main


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def sample_alert(tmp_path):
    alert_file = tmp_path / "alert.txt"
    alert_file.write_text(
        "CVE-2024-3094: XZ Utils backdoor. CVSS 10.0. "
        "Source IP: 192.168.1.100. Hash: d41d8cd98f00b204e9800998ecf8427e"
    )
    return str(alert_file)


class TestCLI:
    @patch("src.cyber_alert.cli.check_ollama_running", return_value=True)
    @patch("src.cyber_alert.core.chat", return_value="## Summary\nHigh severity alert detected.")
    def test_cli_with_file(self, mock_chat, mock_check, runner, sample_alert):
        result = runner.invoke(main, ["--alert", sample_alert, "--severity", "high"])
        assert result.exit_code == 0

    @patch("src.cyber_alert.cli.check_ollama_running", return_value=True)
    @patch("src.cyber_alert.core.chat", return_value="## Priority\n1. Critical threat found.")
    def test_cli_with_text_and_prioritize(self, mock_chat, mock_check, runner):
        result = runner.invoke(main, ["--text", "Multiple CVEs detected", "--prioritize"])
        assert result.exit_code == 0

    @patch("src.cyber_alert.cli.check_ollama_running", return_value=False)
    def test_cli_ollama_not_running(self, mock_check, runner):
        result = runner.invoke(main, ["--text", "test"])
        assert result.exit_code != 0

    def test_cli_ioc_extraction(self, runner, sample_alert):
        result = runner.invoke(main, ["--alert", sample_alert, "--iocs"])
        assert result.exit_code == 0

    def test_cli_cve_lookup(self, runner, sample_alert):
        result = runner.invoke(main, ["--alert", sample_alert, "--cves"])
        assert result.exit_code == 0

    def test_cli_threat_score(self, runner, sample_alert):
        result = runner.invoke(main, ["--alert", sample_alert, "--score"])
        assert result.exit_code == 0

    def test_cli_no_input(self, runner):
        result = runner.invoke(main, [])
        assert result.exit_code != 0
