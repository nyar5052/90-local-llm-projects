"""Tests for Social Media Writer."""

import pytest
from unittest.mock import patch
from click.testing import CliRunner

from app import main, build_prompt, generate_posts, PLATFORM_CONFIG


@pytest.fixture
def runner():
    return CliRunner()


class TestBuildPrompt:
    def test_twitter_prompt_has_char_limit(self):
        prompt = build_prompt("twitter", "product launch", "excited", 2)
        assert "280" in prompt

    def test_linkedin_prompt_has_platform_name(self):
        prompt = build_prompt("linkedin", "product launch", "professional", 1)
        assert "LinkedIn" in prompt

    def test_instagram_prompt_has_hashtag_count(self):
        prompt = build_prompt("instagram", "new feature", "casual", 1)
        assert "15" in prompt

    def test_prompt_contains_topic(self):
        prompt = build_prompt("twitter", "AI trends", "informative", 1)
        assert "AI trends" in prompt

    def test_prompt_contains_tone(self):
        prompt = build_prompt("linkedin", "hiring", "excited", 3)
        assert "excited" in prompt


class TestGeneratePosts:
    @patch("app.chat")
    def test_generate_returns_content(self, mock_chat):
        mock_chat.return_value = "Variant 1: Exciting news! #tech #launch"
        result = generate_posts("twitter", "launch", "excited", 1)
        assert "Variant 1" in result
        mock_chat.assert_called_once()

    @patch("app.chat")
    def test_generate_uses_high_temperature(self, mock_chat):
        mock_chat.return_value = "Post content"
        generate_posts("linkedin", "update", "professional", 1)
        _, kwargs = mock_chat.call_args
        assert kwargs["temperature"] == 0.8


class TestCLI:
    @patch("app.check_ollama_running", return_value=True)
    @patch("app.chat")
    def test_cli_basic(self, mock_chat, mock_check, runner):
        mock_chat.return_value = "Variant 1: Great post! #topic"
        result = runner.invoke(main, ["--platform", "twitter", "--topic", "new product launch"])
        assert result.exit_code == 0

    @patch("app.check_ollama_running", return_value=False)
    def test_cli_ollama_not_running(self, mock_check, runner):
        result = runner.invoke(main, ["--platform", "twitter", "--topic", "test"])
        assert result.exit_code != 0

    @patch("app.check_ollama_running", return_value=True)
    @patch("app.chat")
    def test_cli_all_options(self, mock_chat, mock_check, runner):
        mock_chat.return_value = "Variant 1: Post\nVariant 2: Post"
        result = runner.invoke(
            main,
            ["--platform", "linkedin", "--topic", "hiring update", "--tone", "excited", "--variants", "3"],
        )
        assert result.exit_code == 0
