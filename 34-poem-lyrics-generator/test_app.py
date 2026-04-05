"""Tests for Poem & Lyrics Generator."""

import pytest
from unittest.mock import patch
from click.testing import CliRunner

from app import main, build_prompt, generate_poem


@pytest.fixture
def runner():
    return CliRunner()


class TestBuildPrompt:
    def test_prompt_contains_theme(self):
        prompt = build_prompt("ocean sunset", "sonnet", None, None)
        assert "ocean sunset" in prompt

    def test_prompt_contains_style_instructions(self):
        prompt = build_prompt("love", "haiku", None, None)
        assert "5-7-5" in prompt

    def test_prompt_contains_mood(self):
        prompt = build_prompt("rain", "free-verse", "melancholic", None)
        assert "melancholic" in prompt

    def test_prompt_contains_title(self):
        prompt = build_prompt("stars", "sonnet", None, "Starlight")
        assert "Starlight" in prompt

    def test_rap_style_mentions_verses(self):
        prompt = build_prompt("city life", "rap", None, None)
        assert "verse" in prompt.lower()


class TestGeneratePoem:
    @patch("app.chat")
    def test_generate_returns_content(self, mock_chat):
        mock_chat.return_value = "Ocean Sunset\n\nWaves crash on the shore..."
        result = generate_poem("ocean sunset", "free-verse", None, None)
        assert "Ocean Sunset" in result
        mock_chat.assert_called_once()

    @patch("app.chat")
    def test_generate_uses_high_temperature(self, mock_chat):
        mock_chat.return_value = "A poem"
        generate_poem("love", "sonnet", "romantic", None)
        _, kwargs = mock_chat.call_args
        assert kwargs["temperature"] == 0.9


class TestCLI:
    @patch("app.check_ollama_running", return_value=True)
    @patch("app.chat")
    def test_cli_basic(self, mock_chat, mock_check, runner):
        mock_chat.return_value = "Sunset Haiku\n\nGolden light descends\nWaves whisper to the shoreline\nPeace fills the warm air"
        result = runner.invoke(main, ["--theme", "ocean sunset", "--style", "haiku"])
        assert result.exit_code == 0

    @patch("app.check_ollama_running", return_value=False)
    def test_cli_ollama_not_running(self, mock_check, runner):
        result = runner.invoke(main, ["--theme", "love"])
        assert result.exit_code != 0

    @patch("app.check_ollama_running", return_value=True)
    @patch("app.chat")
    def test_cli_all_options(self, mock_chat, mock_check, runner):
        mock_chat.return_value = "My Sonnet\n\nShall I compare thee..."
        result = runner.invoke(
            main,
            ["--theme", "ocean sunset", "--style", "sonnet", "--mood", "romantic", "--title", "Sea Dreams"],
        )
        assert result.exit_code == 0
