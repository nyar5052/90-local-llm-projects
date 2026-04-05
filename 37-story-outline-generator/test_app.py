"""Tests for Story Outline Generator."""

import pytest
from unittest.mock import patch
from click.testing import CliRunner

from app import main, build_prompt, generate_outline


@pytest.fixture
def runner():
    return CliRunner()


class TestBuildPrompt:
    def test_prompt_contains_genre(self):
        prompt = build_prompt("sci-fi", "AI awakens", 10, 4)
        assert "sci-fi" in prompt

    def test_prompt_contains_premise(self):
        prompt = build_prompt("fantasy", "dragons return", 12, 5)
        assert "dragons return" in prompt

    def test_prompt_contains_chapter_count(self):
        prompt = build_prompt("mystery", "murder on train", 15, 3)
        assert "15" in prompt

    def test_prompt_requests_characters(self):
        prompt = build_prompt("thriller", "spy mission", 10, 6)
        assert "6" in prompt

    def test_prompt_includes_plot_structure(self):
        prompt = build_prompt("romance", "love story", 10, 2)
        assert "Act 1" in prompt
        assert "Act 2" in prompt
        assert "Act 3" in prompt


class TestGenerateOutline:
    @patch("app.chat")
    def test_generate_returns_content(self, mock_chat):
        mock_chat.return_value = "# Story: The Awakening\n\n## Characters\n- Ada: protagonist..."
        result = generate_outline("sci-fi", "AI awakens", 10, 4)
        assert "Awakening" in result
        mock_chat.assert_called_once()

    @patch("app.chat")
    def test_generate_uses_creative_temperature(self, mock_chat):
        mock_chat.return_value = "Outline content"
        generate_outline("fantasy", "premise", 10, 4)
        _, kwargs = mock_chat.call_args
        assert kwargs["temperature"] == 0.8


class TestCLI:
    @patch("app.check_ollama_running", return_value=True)
    @patch("app.chat")
    def test_cli_basic(self, mock_chat, mock_check, runner):
        mock_chat.return_value = "# Story Outline\n\n## Characters\n..."
        result = runner.invoke(main, ["--genre", "sci-fi", "--premise", "AI awakens"])
        assert result.exit_code == 0

    @patch("app.check_ollama_running", return_value=False)
    def test_cli_ollama_not_running(self, mock_check, runner):
        result = runner.invoke(main, ["--genre", "fantasy", "--premise", "magic"])
        assert result.exit_code != 0

    @patch("app.check_ollama_running", return_value=True)
    @patch("app.chat")
    def test_cli_all_options(self, mock_chat, mock_check, runner):
        mock_chat.return_value = "# Detailed Outline\n\n## Chapter 1\n..."
        result = runner.invoke(
            main,
            ["--genre", "sci-fi", "--premise", "AI awakens", "--chapters", "15", "--characters", "6"],
        )
        assert result.exit_code == 0
