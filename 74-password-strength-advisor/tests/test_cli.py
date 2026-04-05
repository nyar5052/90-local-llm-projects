"""Tests for Password Strength Advisor CLI."""

import pytest
from unittest.mock import patch
from click.testing import CliRunner

from src.password_advisor.cli import main


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def sample_policy(tmp_path):
    policy_file = tmp_path / "policy.txt"
    policy_file.write_text(
        "Minimum password length: 8 characters. "
        "Must contain uppercase and lowercase. "
        "Password rotation every 90 days. No MFA required."
    )
    return str(policy_file)


class TestCLI:
    def test_cli_password_entropy(self, runner):
        result = runner.invoke(main, ["--password", "MyStr0ng!Pass#2024"])
        assert result.exit_code == 0

    def test_cli_password_breach_check(self, runner):
        result = runner.invoke(main, ["--password", "password", "--breach-check"])
        assert result.exit_code == 0

    @patch("src.password_advisor.cli.check_ollama_running", return_value=True)
    @patch("src.password_advisor.core.chat", return_value="## Analysis\nPolicy needs improvement.")
    def test_cli_policy_analyze(self, mock_chat, mock_check, runner, sample_policy):
        result = runner.invoke(main, ["--policy", sample_policy, "--analyze"])
        assert result.exit_code == 0

    def test_cli_generate(self, runner):
        result = runner.invoke(main, ["generate", "--length", "20", "--count", "3"])
        assert result.exit_code == 0

    def test_cli_policy_subcommand(self, runner):
        result = runner.invoke(main, ["policy"])
        assert result.exit_code == 0

    def test_cli_no_args(self, runner):
        result = runner.invoke(main, [])
        assert result.exit_code == 0
