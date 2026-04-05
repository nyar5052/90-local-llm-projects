"""Tests for Newsletter Editor."""

import pytest
from unittest.mock import patch, mock_open
from click.testing import CliRunner

from app import main, build_prompt, generate_newsletter, read_input_file


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def sample_notes():
    return "AI news: GPT-5 released. New chip from NVIDIA. Python 3.13 out. React 19 stable."


class TestBuildPrompt:
    def test_prompt_contains_content(self, sample_notes):
        prompt = build_prompt(sample_notes, "Tech Weekly", 4, "informative")
        assert "GPT-5" in prompt

    def test_prompt_contains_name(self, sample_notes):
        prompt = build_prompt(sample_notes, "Tech Weekly", 4, "informative")
        assert "Tech Weekly" in prompt

    def test_prompt_contains_sections(self, sample_notes):
        prompt = build_prompt(sample_notes, "Tech Weekly", 5, "casual")
        assert "5" in prompt

    def test_prompt_contains_tone(self, sample_notes):
        prompt = build_prompt(sample_notes, "Newsletter", 3, "witty")
        assert "witty" in prompt


class TestReadInputFile:
    def test_reads_existing_file(self, tmp_path):
        f = tmp_path / "notes.txt"
        f.write_text("Some raw notes")
        result = read_input_file(str(f))
        assert result == "Some raw notes"

    def test_nonexistent_file_exits(self):
        with pytest.raises(SystemExit):
            read_input_file("nonexistent_file.txt")


class TestGenerateNewsletter:
    @patch("app.chat")
    def test_generate_returns_content(self, mock_chat, sample_notes):
        mock_chat.return_value = "# Tech Weekly\n\n## Section 1\nAI news..."
        result = generate_newsletter(sample_notes, "Tech Weekly", 4, "informative")
        assert "Tech Weekly" in result
        mock_chat.assert_called_once()

    @patch("app.chat")
    def test_generate_uses_correct_max_tokens(self, mock_chat, sample_notes):
        mock_chat.return_value = "Newsletter content"
        generate_newsletter(sample_notes, "Newsletter", 3, "casual")
        _, kwargs = mock_chat.call_args
        assert kwargs["max_tokens"] == 4096


class TestCLI:
    @patch("app.check_ollama_running", return_value=True)
    @patch("app.chat")
    def test_cli_basic(self, mock_chat, mock_check, runner, tmp_path):
        notes = tmp_path / "notes.txt"
        notes.write_text("Raw content about AI and tech")
        mock_chat.return_value = "# Tech Weekly\n\nNewsletter content."
        result = runner.invoke(main, ["--input", str(notes), "--name", "Tech Weekly"])
        assert result.exit_code == 0

    @patch("app.check_ollama_running", return_value=False)
    def test_cli_ollama_not_running(self, mock_check, runner, tmp_path):
        notes = tmp_path / "notes.txt"
        notes.write_text("Content")
        result = runner.invoke(main, ["--input", str(notes), "--name", "Test"])
        assert result.exit_code != 0
