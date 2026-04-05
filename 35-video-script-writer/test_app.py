"""Tests for Video Script Writer."""

import pytest
from unittest.mock import patch
from click.testing import CliRunner

from app import main, build_prompt, generate_script


@pytest.fixture
def runner():
    return CliRunner()


class TestBuildPrompt:
    def test_prompt_contains_topic(self):
        prompt = build_prompt("Python Tips", 10, "educational", None)
        assert "Python Tips" in prompt

    def test_prompt_contains_duration(self):
        prompt = build_prompt("Python Tips", 15, "educational", None)
        assert "15 minutes" in prompt

    def test_prompt_contains_style(self):
        prompt = build_prompt("Review", 10, "review", None)
        assert "review" in prompt

    def test_prompt_includes_broll(self):
        prompt = build_prompt("Topic", 10, "tutorial", None)
        assert "B-ROLL" in prompt

    def test_prompt_includes_audience(self):
        prompt = build_prompt("Topic", 10, "educational", "beginners")
        assert "beginners" in prompt

    def test_prompt_without_audience(self):
        prompt = build_prompt("Topic", 10, "educational", None)
        assert "Target Audience" not in prompt


class TestGenerateScript:
    @patch("app.chat")
    def test_generate_returns_content(self, mock_chat):
        mock_chat.return_value = "## HOOK\n[0:00-0:15]\nHey everyone! Today we're diving into..."
        result = generate_script("Python Tips", 10, "educational", None)
        assert "HOOK" in result
        mock_chat.assert_called_once()

    @patch("app.chat")
    def test_generate_uses_correct_max_tokens(self, mock_chat):
        mock_chat.return_value = "Script content"
        generate_script("Topic", 10, "tutorial", None)
        _, kwargs = mock_chat.call_args
        assert kwargs["max_tokens"] == 4096


class TestCLI:
    @patch("app.check_ollama_running", return_value=True)
    @patch("app.chat")
    def test_cli_basic(self, mock_chat, mock_check, runner):
        mock_chat.return_value = "## HOOK\nHey everyone!\n\n## INTRO\nToday we..."
        result = runner.invoke(main, ["--topic", "Python Tips"])
        assert result.exit_code == 0

    @patch("app.check_ollama_running", return_value=False)
    def test_cli_ollama_not_running(self, mock_check, runner):
        result = runner.invoke(main, ["--topic", "Test"])
        assert result.exit_code != 0

    @patch("app.check_ollama_running", return_value=True)
    @patch("app.chat")
    def test_cli_all_options(self, mock_chat, mock_check, runner):
        mock_chat.return_value = "## Script\nFull script content here."
        result = runner.invoke(
            main,
            ["--topic", "Python Tips", "--duration", "15", "--style", "tutorial", "--audience", "beginners"],
        )
        assert result.exit_code == 0
