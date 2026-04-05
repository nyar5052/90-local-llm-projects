"""Tests for the Research Paper Q&A application."""

import os
import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner

from app import load_paper, build_system_prompt, ask_question, display_history, main


@pytest.fixture
def sample_paper(tmp_path):
    """Create a temporary sample paper file."""
    paper_file = tmp_path / "sample_paper.txt"
    paper_file.write_text(
        "Title: Neural Networks for NLP\n\n"
        "Abstract: This paper explores the use of neural networks "
        "for natural language processing tasks. We demonstrate that "
        "transformer-based models achieve state-of-the-art results.\n\n"
        "1. Introduction\n"
        "Natural language processing has seen remarkable advances.\n\n"
        "2. Methodology\n"
        "We used a transformer architecture with 12 layers.\n\n"
        "3. Results\n"
        "Our model achieved 95.2% accuracy on the benchmark.\n\n"
        "4. Conclusion\n"
        "Transformers are effective for NLP tasks.",
        encoding="utf-8",
    )
    return str(paper_file)


@pytest.fixture
def empty_paper(tmp_path):
    """Create an empty paper file."""
    paper_file = tmp_path / "empty.txt"
    paper_file.write_text("", encoding="utf-8")
    return str(paper_file)


class TestLoadPaper:
    """Tests for the load_paper function."""

    def test_load_valid_paper(self, sample_paper):
        """Test loading a valid paper file returns its content."""
        content = load_paper(sample_paper)
        assert "Neural Networks for NLP" in content
        assert "transformer" in content.lower()

    def test_load_nonexistent_file(self):
        """Test that loading a nonexistent file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError, match="Paper not found"):
            load_paper("nonexistent_paper.txt")

    def test_load_empty_paper(self, empty_paper):
        """Test that loading an empty paper raises ValueError."""
        with pytest.raises(ValueError, match="Paper file is empty"):
            load_paper(empty_paper)

    def test_load_paper_content_complete(self, sample_paper):
        """Test that the full paper content is loaded."""
        content = load_paper(sample_paper)
        assert "Abstract" in content
        assert "Methodology" in content
        assert "Results" in content
        assert "Conclusion" in content


class TestBuildSystemPrompt:
    """Tests for the build_system_prompt function."""

    def test_system_prompt_contains_paper(self):
        """Test that the system prompt embeds the paper content."""
        paper = "This is a test paper about quantum computing."
        prompt = build_system_prompt(paper)
        assert "quantum computing" in prompt
        assert "PAPER CONTENT" in prompt

    def test_system_prompt_has_instructions(self):
        """Test that the system prompt includes analysis instructions."""
        prompt = build_system_prompt("Some paper content.")
        assert "research paper" in prompt.lower()
        assert "answer" in prompt.lower()


class TestAskQuestion:
    """Tests for the ask_question function."""

    @patch("app.chat")
    def test_ask_question_returns_response(self, mock_chat):
        """Test that ask_question returns the LLM response."""
        mock_chat.return_value = "The paper discusses neural networks."
        history = []
        system_prompt = "You are a helpful assistant."

        answer = ask_question("What is the paper about?", history, system_prompt)

        assert answer == "The paper discusses neural networks."
        mock_chat.assert_called_once()

    @patch("app.chat")
    def test_ask_question_updates_history(self, mock_chat):
        """Test that conversation history is updated after a question."""
        mock_chat.return_value = "The accuracy was 95.2%."
        history = []
        system_prompt = "You are a helpful assistant."

        ask_question("What was the accuracy?", history, system_prompt)

        assert len(history) == 2
        assert history[0] == {"role": "user", "content": "What was the accuracy?"}
        assert history[1] == {"role": "assistant", "content": "The accuracy was 95.2%."}

    @patch("app.chat")
    def test_ask_question_preserves_context(self, mock_chat):
        """Test that previous messages are sent for context."""
        mock_chat.return_value = "Follow-up answer."
        history = [
            {"role": "user", "content": "First question"},
            {"role": "assistant", "content": "First answer"},
        ]
        system_prompt = "You are a helpful assistant."

        ask_question("Follow-up question", history, system_prompt)

        call_args = mock_chat.call_args
        messages = call_args.kwargs.get("messages") or call_args[0][0]
        # History has 2 prior + 1 new user message at call time, then assistant appended after
        assert len(history) == 4
        assert history[0]["content"] == "First question"
        assert history[2]["content"] == "Follow-up question"
        assert history[3]["content"] == "Follow-up answer."

    @patch("app.chat")
    def test_ask_question_passes_system_prompt(self, mock_chat):
        """Test that the system prompt is passed to the LLM."""
        mock_chat.return_value = "Response."
        system_prompt = "Analyze this paper: test content"

        ask_question("Question?", [], system_prompt)

        call_args = mock_chat.call_args
        assert call_args.kwargs.get("system_prompt") == system_prompt


class TestConversationHistory:
    """Tests for conversation history management."""

    @patch("app.chat")
    def test_multi_turn_conversation(self, mock_chat):
        """Test that multi-turn conversations accumulate history."""
        mock_chat.side_effect = ["Answer 1", "Answer 2", "Answer 3"]
        history = []
        system_prompt = "Assistant prompt."

        ask_question("Q1", history, system_prompt)
        ask_question("Q2", history, system_prompt)
        ask_question("Q3", history, system_prompt)

        assert len(history) == 6  # 3 user + 3 assistant
        assert history[0]["content"] == "Q1"
        assert history[5]["content"] == "Answer 3"

    def test_clear_history(self):
        """Test that clearing history resets the conversation."""
        history = [
            {"role": "user", "content": "Q1"},
            {"role": "assistant", "content": "A1"},
        ]
        history.clear()
        assert len(history) == 0


class TestCLI:
    """Tests for the CLI interface."""

    def test_cli_missing_paper_option(self):
        """Test that CLI fails without --paper option."""
        runner = CliRunner()
        result = runner.invoke(main, [])
        assert result.exit_code != 0

    def test_cli_nonexistent_paper_file(self):
        """Test that CLI fails with a nonexistent paper file."""
        runner = CliRunner()
        result = runner.invoke(main, ["--paper", "does_not_exist.txt"])
        assert result.exit_code != 0

    @patch("app.check_ollama_running", return_value=False)
    def test_cli_ollama_not_running(self, mock_check, tmp_path):
        """Test that CLI exits when Ollama is not running."""
        paper = tmp_path / "paper.txt"
        paper.write_text("Some paper content.")
        runner = CliRunner()
        result = runner.invoke(main, ["--paper", str(paper)])
        assert result.exit_code != 0
        assert "Ollama" in result.output or "not running" in result.output


class TestDisplayHistory:
    """Tests for the display_history function."""

    def test_display_empty_history(self, capsys):
        """Test displaying empty history shows appropriate message."""
        display_history([])
        # No exception should be raised

    def test_display_with_entries(self):
        """Test displaying history with conversation entries."""
        history = [
            {"role": "user", "content": "What is this paper about?"},
            {"role": "assistant", "content": "This paper discusses AI."},
        ]
        # Should not raise any exceptions
        display_history(history)
