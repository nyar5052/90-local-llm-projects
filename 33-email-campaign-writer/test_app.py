"""Tests for Email Campaign Writer."""

import pytest
from unittest.mock import patch
from click.testing import CliRunner

from app import main, build_prompt, generate_campaign


@pytest.fixture
def runner():
    return CliRunner()


class TestBuildPrompt:
    def test_prompt_contains_product(self):
        prompt = build_prompt("SaaS Tool", "developers", 3, "promotional")
        assert "SaaS Tool" in prompt

    def test_prompt_contains_audience(self):
        prompt = build_prompt("SaaS Tool", "developers", 3, "promotional")
        assert "developers" in prompt

    def test_prompt_contains_email_count(self):
        prompt = build_prompt("SaaS Tool", "developers", 5, "promotional")
        assert "5" in prompt

    def test_prompt_contains_campaign_type(self):
        prompt = build_prompt("App", "users", 3, "welcome")
        assert "welcome" in prompt

    def test_prompt_requests_subject_lines(self):
        prompt = build_prompt("App", "users", 3, "nurture")
        assert "Subject Line" in prompt


class TestGenerateCampaign:
    @patch("app.chat")
    def test_generate_returns_content(self, mock_chat):
        mock_chat.return_value = "## Email 1\n**Subject:** Welcome!\n\nBody content..."
        result = generate_campaign("SaaS Tool", "developers", 3, "promotional")
        assert "Email 1" in result
        mock_chat.assert_called_once()

    @patch("app.chat")
    def test_generate_uses_correct_max_tokens(self, mock_chat):
        mock_chat.return_value = "Campaign content"
        generate_campaign("SaaS Tool", "developers", 3, "promotional")
        _, kwargs = mock_chat.call_args
        assert kwargs["max_tokens"] == 4096


class TestCLI:
    @patch("app.check_ollama_running", return_value=True)
    @patch("app.chat")
    def test_cli_basic(self, mock_chat, mock_check, runner):
        mock_chat.return_value = "## Email 1\nSubject: Test\n\nBody"
        result = runner.invoke(main, ["--product", "SaaS Tool", "--audience", "developers"])
        assert result.exit_code == 0

    @patch("app.check_ollama_running", return_value=False)
    def test_cli_ollama_not_running(self, mock_check, runner):
        result = runner.invoke(main, ["--product", "App", "--audience", "users"])
        assert result.exit_code != 0

    @patch("app.check_ollama_running", return_value=True)
    @patch("app.chat")
    def test_cli_with_options(self, mock_chat, mock_check, runner):
        mock_chat.return_value = "## Email 1\nWelcome!\n\n## Email 2\nFollow up!"
        result = runner.invoke(
            main,
            ["--product", "SaaS Tool", "--audience", "developers", "--emails", "5", "--type", "welcome"],
        )
        assert result.exit_code == 0
