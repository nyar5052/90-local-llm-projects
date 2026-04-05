"""
Tests for Meeting Summarizer - Project 13
"""

import os
import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner

from app import (
    read_transcript,
    preprocess_transcript,
    summarize_meeting,
    parse_action_items,
    extract_section,
    save_summary,
    display_summary,
    main,
    MAX_TRANSCRIPT_LENGTH,
)


SAMPLE_TRANSCRIPT = """
Meeting: Weekly Team Sync
Date: 2025-01-15
Attendees: Alice (PM), Bob (Dev), Carol (Design), Dave (QA)

Alice: Let's get started. First item on the agenda is the Q1 roadmap.
Bob: I've drafted the technical spec for the new API. Should be ready for review by Friday.
Carol: The mockups for the dashboard redesign are done. I'll share them today.
Alice: Great. Let's make a decision - we'll go with Option B for the pricing page.
Dave: I'll start writing test cases for the API once Bob shares the spec.
Alice: Bob, can you also update the documentation by next Wednesday?
Bob: Sure, I'll handle that.
Alice: Follow-up: Carol, schedule a design review for next week.
Carol: Will do.
Alice: Alright, meeting adjourned.
"""

SAMPLE_LLM_RESPONSE = """## ATTENDEES
- Alice (PM)
- Bob (Dev)
- Carol (Design)
- Dave (QA)

## AGENDA TOPICS
- Q1 roadmap
- Technical spec for new API
- Dashboard redesign mockups
- Pricing page decision

## KEY DECISIONS
- Go with Option B for the pricing page

## ACTION ITEMS
| Who | What | When |
|-----|------|------|
| Bob | Share technical spec for review | Friday |
| Carol | Share dashboard mockups | Today |
| Dave | Write test cases for the API | After spec is shared |
| Bob | Update documentation | Next Wednesday |

## FOLLOW-UPS
- Carol to schedule a design review for next week

## SUMMARY
The team discussed the Q1 roadmap, reviewed progress on the API spec and dashboard redesign, \
and decided to go with Option B for the pricing page. Multiple action items were assigned with \
specific deadlines.
"""


class TestReadTranscript:
    """Tests for the read_transcript function."""

    def test_read_valid_file(self, tmp_path):
        """Test reading a valid transcript file."""
        file_path = tmp_path / "meeting.txt"
        file_path.write_text("Hello, this is a meeting.", encoding="utf-8")

        result = read_transcript(str(file_path))
        assert result == "Hello, this is a meeting."

    def test_read_missing_file(self):
        """Test reading a file that does not exist."""
        with pytest.raises(FileNotFoundError, match="Transcript file not found"):
            read_transcript("nonexistent_meeting.txt")

    def test_read_empty_file(self, tmp_path):
        """Test reading an empty transcript file."""
        file_path = tmp_path / "empty.txt"
        file_path.write_text("", encoding="utf-8")

        with pytest.raises(ValueError, match="empty or contains only whitespace"):
            read_transcript(str(file_path))

    def test_read_whitespace_only_file(self, tmp_path):
        """Test reading a file with only whitespace."""
        file_path = tmp_path / "whitespace.txt"
        file_path.write_text("   \n\n  \t  ", encoding="utf-8")

        with pytest.raises(ValueError, match="empty or contains only whitespace"):
            read_transcript(str(file_path))

    def test_read_unicode_content(self, tmp_path):
        """Test reading a file with unicode characters."""
        file_path = tmp_path / "unicode.txt"
        file_path.write_text("Meeting with José and François — résumé", encoding="utf-8")

        result = read_transcript(str(file_path))
        assert "José" in result
        assert "François" in result


class TestPreprocessTranscript:
    """Tests for the preprocess_transcript function."""

    def test_short_transcript_unchanged(self):
        """Test that short transcripts are returned unchanged."""
        text = "This is a short meeting transcript."
        result = preprocess_transcript(text)
        assert result == text

    def test_long_transcript_truncated(self):
        """Test that long transcripts are truncated with a notice."""
        text = "x" * (MAX_TRANSCRIPT_LENGTH + 1000)
        result = preprocess_transcript(text)
        assert len(result) <= MAX_TRANSCRIPT_LENGTH + 100  # allow for truncation notice
        assert "[...transcript truncated...]" in result

    def test_whitespace_stripped(self):
        """Test that leading/trailing whitespace is stripped."""
        text = "   Meeting notes here   "
        result = preprocess_transcript(text)
        assert result == "Meeting notes here"


class TestSummarizeMeeting:
    """Tests for the summarize_meeting function."""

    @patch("app.chat")
    def test_summarize_calls_llm(self, mock_chat):
        """Test that summarize_meeting calls the LLM with correct parameters."""
        mock_chat.return_value = SAMPLE_LLM_RESPONSE

        result = summarize_meeting(SAMPLE_TRANSCRIPT)

        mock_chat.assert_called_once()
        call_kwargs = mock_chat.call_args
        assert call_kwargs.kwargs["temperature"] == 0.3
        assert call_kwargs.kwargs["max_tokens"] == 4096
        assert call_kwargs.kwargs["system_prompt"] is not None
        assert result == SAMPLE_LLM_RESPONSE

    @patch("app.chat")
    def test_summarize_includes_transcript_in_prompt(self, mock_chat):
        """Test that the transcript text is included in the prompt sent to the LLM."""
        mock_chat.return_value = "Summary"

        summarize_meeting("Alice said hello to Bob.")

        call_kwargs = mock_chat.call_args
        messages = call_kwargs.kwargs.get("messages") or call_kwargs.args[0]
        assert "Alice said hello to Bob." in messages[0]["content"]


class TestParseActionItems:
    """Tests for the parse_action_items function."""

    def test_parse_valid_action_items(self):
        """Test parsing well-formatted action items."""
        items = parse_action_items(SAMPLE_LLM_RESPONSE)

        assert len(items) == 4
        assert items[0]["who"] == "Bob"
        assert "technical spec" in items[0]["what"]
        assert items[0]["when"] == "Friday"

    def test_parse_no_action_items(self):
        """Test parsing when there are no action items."""
        summary = """## ACTION ITEMS
| Who | What | When |
|-----|------|------|

## FOLLOW-UPS
- None
"""
        items = parse_action_items(summary)
        assert items == []

    def test_parse_missing_section(self):
        """Test parsing when action items section is missing entirely."""
        summary = "## SUMMARY\nJust a quick meeting."
        items = parse_action_items(summary)
        assert items == []

    def test_parse_single_action_item(self):
        """Test parsing a single action item."""
        summary = """## ACTION ITEMS
| Who | What | When |
|-----|------|------|
| Alice | Review the proposal | Monday |

## SUMMARY
Done.
"""
        items = parse_action_items(summary)
        assert len(items) == 1
        assert items[0]["who"] == "Alice"
        assert items[0]["what"] == "Review the proposal"
        assert items[0]["when"] == "Monday"


class TestExtractSection:
    """Tests for the extract_section function."""

    def test_extract_attendees(self):
        """Test extracting the ATTENDEES section."""
        result = extract_section(SAMPLE_LLM_RESPONSE, "ATTENDEES")
        assert "Alice (PM)" in result
        assert "Bob (Dev)" in result

    def test_extract_decisions(self):
        """Test extracting the KEY DECISIONS section."""
        result = extract_section(SAMPLE_LLM_RESPONSE, "KEY DECISIONS")
        assert "Option B" in result

    def test_extract_missing_section(self):
        """Test extracting a section that doesn't exist."""
        result = extract_section(SAMPLE_LLM_RESPONSE, "NONEXISTENT")
        assert result == "Not mentioned"

    def test_extract_summary(self):
        """Test extracting the SUMMARY section."""
        result = extract_section(SAMPLE_LLM_RESPONSE, "SUMMARY")
        assert "Q1 roadmap" in result


class TestDisplaySummary:
    """Tests for the display_summary function."""

    @patch("app.console")
    def test_display_calls_console(self, mock_console):
        """Test that display_summary outputs to the console."""
        display_summary(SAMPLE_LLM_RESPONSE)
        assert mock_console.print.called

    @patch("app.console")
    def test_display_handles_empty_summary(self, mock_console):
        """Test display with minimal summary content."""
        display_summary("## SUMMARY\nNothing to report.")
        assert mock_console.print.called


class TestSaveSummary:
    """Tests for the save_summary function."""

    def test_save_creates_file(self, tmp_path):
        """Test that save_summary writes content to the output file."""
        output_path = tmp_path / "output.md"
        save_summary(SAMPLE_LLM_RESPONSE, str(output_path))

        assert output_path.exists()
        content = output_path.read_text(encoding="utf-8")
        assert "## ATTENDEES" in content
        assert "## ACTION ITEMS" in content

    def test_save_overwrites_existing(self, tmp_path):
        """Test that save_summary overwrites an existing file."""
        output_path = tmp_path / "output.md"
        output_path.write_text("old content", encoding="utf-8")

        save_summary("new summary", str(output_path))
        content = output_path.read_text(encoding="utf-8")
        assert content == "new summary"


class TestCLI:
    """Tests for the Click CLI interface."""

    def test_cli_missing_transcript_option(self):
        """Test that CLI fails when --transcript is not provided."""
        runner = CliRunner()
        result = runner.invoke(main, [])
        assert result.exit_code != 0
        assert "Missing option" in result.output or "required" in result.output.lower()

    @patch("app.check_ollama_running", return_value=False)
    def test_cli_ollama_not_running(self, mock_check):
        """Test that CLI exits gracefully when Ollama is not running."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            with open("meeting.txt", "w") as f:
                f.write(SAMPLE_TRANSCRIPT)

            result = runner.invoke(main, ["--transcript", "meeting.txt"])
            assert result.exit_code != 0

    @patch("app.chat", return_value=SAMPLE_LLM_RESPONSE)
    @patch("app.check_ollama_running", return_value=True)
    def test_cli_successful_run(self, mock_check, mock_chat):
        """Test a successful CLI run with valid transcript."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            with open("meeting.txt", "w", encoding="utf-8") as f:
                f.write(SAMPLE_TRANSCRIPT)

            result = runner.invoke(main, ["--transcript", "meeting.txt"])
            assert result.exit_code == 0

    @patch("app.chat", return_value=SAMPLE_LLM_RESPONSE)
    @patch("app.check_ollama_running", return_value=True)
    def test_cli_with_output_file(self, mock_check, mock_chat):
        """Test CLI run with --output flag saves to file."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            with open("meeting.txt", "w", encoding="utf-8") as f:
                f.write(SAMPLE_TRANSCRIPT)

            result = runner.invoke(main, [
                "--transcript", "meeting.txt",
                "--output", "summary.md",
            ])
            assert result.exit_code == 0
            assert os.path.exists("summary.md")
            with open("summary.md", "r", encoding="utf-8") as f:
                content = f.read()
            assert "## ATTENDEES" in content

    @patch("app.check_ollama_running", return_value=True)
    def test_cli_nonexistent_transcript(self, mock_check):
        """Test CLI with a transcript file that doesn't exist."""
        runner = CliRunner()
        result = runner.invoke(main, ["--transcript", "does_not_exist.txt"])
        assert result.exit_code != 0
