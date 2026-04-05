"""Tests for Presentation Generator."""

import pytest
from unittest.mock import patch
from click.testing import CliRunner

from app import main, build_prompt, generate_presentation


@pytest.fixture
def runner():
    return CliRunner()


class TestBuildPrompt:
    def test_prompt_contains_topic(self):
        prompt = build_prompt("Machine Learning 101", 12, "beginners", "standard")
        assert "Machine Learning 101" in prompt

    def test_prompt_contains_slide_count(self):
        prompt = build_prompt("Topic", 15, "experts", "standard")
        assert "15" in prompt

    def test_prompt_contains_audience(self):
        prompt = build_prompt("Topic", 10, "executives", "keynote")
        assert "executives" in prompt

    def test_prompt_contains_format(self):
        prompt = build_prompt("Topic", 20, "general", "pecha-kucha")
        assert "pecha-kucha" in prompt.lower() or "20 slides" in prompt

    def test_prompt_requests_speaker_notes(self):
        prompt = build_prompt("Topic", 10, "general", "standard")
        assert "Speaker Notes" in prompt


class TestGeneratePresentation:
    @patch("app.chat")
    def test_generate_returns_content(self, mock_chat):
        mock_chat.return_value = "### Slide 1: Introduction\n**Content:**\n- Welcome..."
        result = generate_presentation("ML 101", 12, "beginners", "standard")
        assert "Slide 1" in result
        mock_chat.assert_called_once()

    @patch("app.chat")
    def test_generate_uses_correct_max_tokens(self, mock_chat):
        mock_chat.return_value = "Presentation"
        generate_presentation("Topic", 10, "general", "standard")
        _, kwargs = mock_chat.call_args
        assert kwargs["max_tokens"] == 4096


class TestCLI:
    @patch("app.check_ollama_running", return_value=True)
    @patch("app.chat")
    def test_cli_basic(self, mock_chat, mock_check, runner):
        mock_chat.return_value = "### Slide 1: Title\nContent here"
        result = runner.invoke(main, ["--topic", "Machine Learning 101"])
        assert result.exit_code == 0

    @patch("app.check_ollama_running", return_value=False)
    def test_cli_ollama_not_running(self, mock_check, runner):
        result = runner.invoke(main, ["--topic", "Test"])
        assert result.exit_code != 0

    @patch("app.check_ollama_running", return_value=True)
    @patch("app.chat")
    def test_cli_all_options(self, mock_chat, mock_check, runner):
        mock_chat.return_value = "### Slide 1\nKeynote content"
        result = runner.invoke(
            main,
            ["--topic", "Machine Learning 101", "--slides", "15", "--audience", "beginners", "--format", "keynote"],
        )
        assert result.exit_code == 0
