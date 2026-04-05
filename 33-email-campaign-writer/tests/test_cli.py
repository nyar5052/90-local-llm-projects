"""Tests for email_campaign.cli module."""

import pytest
from unittest.mock import patch
from click.testing import CliRunner

from email_campaign.cli import main


@pytest.fixture
def runner():
    return CliRunner()


class TestCLIBasic:
    @patch("email_campaign.cli.check_ollama_running", return_value=True)
    @patch("email_campaign.core.chat")
    def test_cli_basic(self, mock_chat, mock_check, runner):
        mock_chat.return_value = "## Email 1\nSubject: Test\n\nBody"
        result = runner.invoke(main, ["--product", "SaaS Tool", "--audience", "developers"])
        assert result.exit_code == 0

    @patch("email_campaign.cli.check_ollama_running", return_value=False)
    def test_cli_ollama_not_running(self, mock_check, runner):
        result = runner.invoke(main, ["--product", "App", "--audience", "users"])
        assert result.exit_code != 0

    @patch("email_campaign.cli.check_ollama_running", return_value=True)
    @patch("email_campaign.core.chat")
    def test_cli_with_type(self, mock_chat, mock_check, runner):
        mock_chat.return_value = "## Email 1\nWelcome!\n\n## Email 2\nFollow up!"
        result = runner.invoke(
            main,
            ["--product", "SaaS Tool", "--audience", "developers", "--emails", "5", "--type", "welcome"],
        )
        assert result.exit_code == 0


class TestCLISubjectTest:
    @patch("email_campaign.cli.check_ollama_running", return_value=True)
    @patch("email_campaign.core.chat")
    def test_subject_test_flag(self, mock_chat, mock_check, runner):
        mock_chat.side_effect = [
            "1. Subject A\n2. Subject B\n3. Subject C",
            "## Email 1\nContent here",
        ]
        result = runner.invoke(
            main,
            ["--product", "Tool", "--audience", "devs", "--subject-test"],
        )
        assert result.exit_code == 0


class TestCLITimeline:
    @patch("email_campaign.cli.check_ollama_running", return_value=True)
    @patch("email_campaign.core.chat")
    def test_timeline_flag(self, mock_chat, mock_check, runner):
        mock_chat.return_value = "Campaign content"
        result = runner.invoke(
            main,
            ["--product", "Tool", "--audience", "devs", "--timeline"],
        )
        assert result.exit_code == 0


class TestCLIPersonalize:
    @patch("email_campaign.cli.check_ollama_running", return_value=True)
    @patch("email_campaign.core.chat")
    def test_personalize_option(self, mock_chat, mock_check, runner):
        mock_chat.return_value = "Hello {{first_name}}, welcome!"
        result = runner.invoke(
            main,
            ["--product", "Tool", "--audience", "devs", "--personalize", '{"first_name":"Jane"}'],
        )
        assert result.exit_code == 0

    @patch("email_campaign.cli.check_ollama_running", return_value=True)
    @patch("email_campaign.core.chat")
    def test_personalize_invalid_json(self, mock_chat, mock_check, runner):
        mock_chat.return_value = "Hello"
        result = runner.invoke(
            main,
            ["--product", "Tool", "--audience", "devs", "--personalize", "not-json"],
        )
        assert result.exit_code != 0


class TestCLIHtmlPreview:
    @patch("email_campaign.cli.check_ollama_running", return_value=True)
    @patch("email_campaign.core.chat")
    def test_html_preview_flag(self, mock_chat, mock_check, runner, tmp_path):
        mock_chat.return_value = "Campaign content"
        result = runner.invoke(
            main,
            ["--product", "Tool", "--audience", "devs", "--html-preview"],
        )
        assert result.exit_code == 0
