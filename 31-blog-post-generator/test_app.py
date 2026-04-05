"""Tests for Blog Post Generator."""

import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner

from app import main, build_prompt, generate_blog_post


@pytest.fixture
def runner():
    return CliRunner()


class TestBuildPrompt:
    def test_prompt_contains_topic(self):
        prompt = build_prompt("AI in Healthcare", ["ML", "diagnosis"], "professional", 800)
        assert "AI in Healthcare" in prompt

    def test_prompt_contains_keywords(self):
        prompt = build_prompt("AI", ["ML", "diagnosis"], "professional", 800)
        assert "ML" in prompt
        assert "diagnosis" in prompt

    def test_prompt_contains_tone(self):
        prompt = build_prompt("AI", [], "casual", 500)
        assert "casual" in prompt

    def test_prompt_contains_length(self):
        prompt = build_prompt("AI", [], "technical", 1200)
        assert "1200" in prompt

    def test_prompt_no_keywords(self):
        prompt = build_prompt("AI", [], "professional", 800)
        assert "none specified" in prompt


class TestGenerateBlogPost:
    @patch("app.chat")
    def test_generate_returns_content(self, mock_chat):
        mock_chat.return_value = "# Test Blog Post\n\nThis is a test blog post."
        result = generate_blog_post("AI", ["ML"], "professional", 800)
        assert "Test Blog Post" in result
        mock_chat.assert_called_once()

    @patch("app.chat")
    def test_generate_passes_system_prompt(self, mock_chat):
        mock_chat.return_value = "# Post"
        generate_blog_post("AI", [], "casual", 500)
        _, kwargs = mock_chat.call_args
        assert "SEO" in kwargs["system_prompt"]


class TestCLI:
    @patch("app.check_ollama_running", return_value=True)
    @patch("app.chat")
    def test_cli_basic(self, mock_chat, mock_check, runner):
        mock_chat.return_value = "# Blog Post\n\nContent here."
        result = runner.invoke(main, ["--topic", "AI in Healthcare"])
        assert result.exit_code == 0

    @patch("app.check_ollama_running", return_value=False)
    def test_cli_ollama_not_running(self, mock_check, runner):
        result = runner.invoke(main, ["--topic", "AI"])
        assert result.exit_code != 0

    @patch("app.check_ollama_running", return_value=True)
    @patch("app.chat")
    def test_cli_with_all_options(self, mock_chat, mock_check, runner):
        mock_chat.return_value = "# Technical Post\n\nDetailed content."
        result = runner.invoke(
            main,
            ["--topic", "AI", "--keywords", "ML,deep learning", "--tone", "technical", "--length", "1200"],
        )
        assert result.exit_code == 0
