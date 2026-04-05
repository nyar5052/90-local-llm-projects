"""Tests for GDPR Compliance Checker CLI."""

import pytest
from unittest.mock import patch
from click.testing import CliRunner

from src.gdpr_checker.cli import main


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def sample_policy(tmp_path):
    policy_file = tmp_path / "privacy_policy.txt"
    policy_file.write_text(
        "We collect user email addresses for marketing purposes. "
        "Data is stored indefinitely. Users can request data deletion by email."
    )
    return str(policy_file)


class TestCLI:
    @patch("src.gdpr_checker.cli.check_ollama_running", return_value=True)
    @patch("src.gdpr_checker.core.chat", return_value="## Compliance Report\nPartially compliant.")
    def test_cli_compliance_check(self, mock_chat, mock_check, runner, sample_policy):
        result = runner.invoke(main, ["--file", sample_policy, "--check", "all"])
        assert result.exit_code == 0

    def test_cli_article_checklist(self, runner, sample_policy):
        result = runner.invoke(main, ["--file", sample_policy, "--articles"])
        assert result.exit_code == 0

    def test_cli_data_flows(self, runner, sample_policy):
        result = runner.invoke(main, ["--file", sample_policy, "--data-flows"])
        assert result.exit_code == 0

    def test_cli_dpo_recommendations(self, runner, sample_policy):
        result = runner.invoke(main, ["--file", sample_policy, "--dpo"])
        assert result.exit_code == 0

    @patch("src.gdpr_checker.cli.check_ollama_running", return_value=False)
    def test_cli_ollama_not_running(self, mock_check, runner, sample_policy):
        result = runner.invoke(main, ["--file", sample_policy])
        assert result.exit_code != 0
