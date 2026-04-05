"""Tests for the Medical Literature Summarizer."""

import os
import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner

from app import read_paper, extract_section, summarize_paper, format_output, main, SECTIONS


SAMPLE_PAPER = """\
Title: Effects of Aspirin on Cardiovascular Mortality in Elderly Patients
Authors: Jane Smith, MD; John Doe, PhD; Alice Johnson, MPH

Abstract:
This randomized controlled trial examined the effects of low-dose aspirin
on cardiovascular mortality in adults aged 65 and older. A total of 5,000
participants were enrolled across 12 medical centers over a 5-year period.
Results showed a 15% reduction in cardiovascular events (p=0.003, 95% CI:
0.78-0.92). The study concludes that low-dose aspirin provides significant
cardiovascular protection in elderly populations, though gastrointestinal
side effects remain a concern.

Methodology:
Double-blind, placebo-controlled randomized trial. Participants were
randomly assigned to receive either 100mg aspirin daily or placebo.
Primary endpoint was composite cardiovascular mortality.

Results:
The aspirin group showed a 15% relative risk reduction in cardiovascular
events compared to placebo (HR=0.85, 95% CI: 0.78-0.92, p=0.003).
All-cause mortality was not significantly different between groups.

Conclusions:
Low-dose aspirin significantly reduces cardiovascular events in elderly
patients. Benefits must be weighed against bleeding risks.

Limitations:
The study population was predominantly Caucasian, limiting
generalizability. Adherence was self-reported.

Future Directions:
Further studies should examine diverse populations and explore
biomarkers for identifying patients most likely to benefit.
"""


@pytest.fixture
def sample_paper_file(tmp_path):
    """Create a temporary paper file for testing."""
    paper_file = tmp_path / "test_paper.txt"
    paper_file.write_text(SAMPLE_PAPER, encoding="utf-8")
    return str(paper_file)


@pytest.fixture
def empty_paper_file(tmp_path):
    """Create an empty temporary paper file."""
    paper_file = tmp_path / "empty_paper.txt"
    paper_file.write_text("", encoding="utf-8")
    return str(paper_file)


# --- Test file reading ---

class TestReadPaper:
    """Tests for the read_paper function."""

    def test_read_valid_file(self, sample_paper_file):
        """Test reading a valid paper file returns its contents."""
        content = read_paper(sample_paper_file)
        assert "Effects of Aspirin" in content
        assert "Methodology:" in content
        assert len(content) > 0

    def test_read_missing_file(self):
        """Test that reading a non-existent file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError, match="Paper file not found"):
            read_paper("nonexistent_paper.txt")

    def test_read_empty_file(self, empty_paper_file):
        """Test that reading an empty file raises ValueError."""
        with pytest.raises(ValueError, match="Paper file is empty"):
            read_paper(empty_paper_file)


# --- Test paper summarization (mock LLM) ---

class TestSummarizePaper:
    """Tests for the summarize_paper function with mocked LLM calls."""

    @patch("app.chat")
    def test_summarize_returns_all_sections(self, mock_chat):
        """Test that summarize_paper returns all expected section keys."""
        mock_chat.return_value = "Mocked LLM response for this section."

        results = summarize_paper(SAMPLE_PAPER, detail_level="standard")

        expected_keys = {key for key, _, _ in SECTIONS}
        assert set(results.keys()) == expected_keys

    @patch("app.chat")
    def test_summarize_calls_llm_per_section(self, mock_chat):
        """Test that summarize_paper calls the LLM once per section."""
        mock_chat.return_value = "Mocked response."

        summarize_paper(SAMPLE_PAPER, detail_level="standard")

        assert mock_chat.call_count == len(SECTIONS)

    @patch("app.chat")
    def test_summarize_handles_llm_error(self, mock_chat):
        """Test that a failing LLM call results in an error message in that section."""
        mock_chat.side_effect = Exception("LLM connection failed")

        results = summarize_paper(SAMPLE_PAPER, detail_level="standard")

        for value in results.values():
            assert "Error extracting section" in value

    @patch("app.chat")
    def test_extract_section_uses_system_prompt(self, mock_chat):
        """Test that extract_section sends the correct system prompt to the LLM."""
        mock_chat.return_value = "Section content."

        extract_section(SAMPLE_PAPER, "methodology", "Describe the methodology.", "standard")

        call_kwargs = mock_chat.call_args
        assert call_kwargs.kwargs.get("system_prompt") is not None
        assert "expert medical" in call_kwargs.kwargs["system_prompt"].lower()


# --- Test different detail levels ---

class TestDetailLevels:
    """Tests for different detail level configurations."""

    @patch("app.chat")
    def test_brief_detail_level(self, mock_chat):
        """Test that brief detail level passes concise instruction."""
        mock_chat.return_value = "Brief response."

        extract_section(SAMPLE_PAPER, "conclusions", "Summarize conclusions.", "brief")

        system_prompt = mock_chat.call_args.kwargs["system_prompt"]
        assert "concise" in system_prompt.lower()

    @patch("app.chat")
    def test_comprehensive_detail_level(self, mock_chat):
        """Test that comprehensive detail level passes in-depth instruction."""
        mock_chat.return_value = "Comprehensive response."

        extract_section(SAMPLE_PAPER, "conclusions", "Summarize conclusions.", "comprehensive")

        system_prompt = mock_chat.call_args.kwargs["system_prompt"]
        assert "in-depth" in system_prompt.lower()

    @patch("app.chat")
    def test_standard_detail_level(self, mock_chat):
        """Test that standard detail level passes moderate instruction."""
        mock_chat.return_value = "Standard response."

        extract_section(SAMPLE_PAPER, "conclusions", "Summarize conclusions.", "standard")

        system_prompt = mock_chat.call_args.kwargs["system_prompt"]
        assert "thorough" in system_prompt.lower()


# --- Test CLI with missing file ---

class TestCLI:
    """Tests for the Click CLI interface."""

    @patch("app.check_ollama_running", return_value=True)
    def test_cli_missing_paper_file(self, mock_ollama):
        """Test CLI exits with error when paper file doesn't exist."""
        runner = CliRunner()
        result = runner.invoke(main, ["--paper", "does_not_exist.txt"])
        assert result.exit_code != 0

    def test_cli_no_paper_argument(self):
        """Test CLI exits with error when --paper is not provided."""
        runner = CliRunner()
        result = runner.invoke(main, [])
        assert result.exit_code != 0
        assert "Missing" in result.output or "required" in result.output.lower() or "Error" in result.output

    @patch("app.check_ollama_running", return_value=False)
    def test_cli_ollama_not_running(self, mock_ollama):
        """Test CLI exits with error when Ollama is not available."""
        runner = CliRunner()
        result = runner.invoke(main, ["--paper", "some_file.txt"])
        assert result.exit_code != 0

    def test_cli_invalid_detail_level(self):
        """Test CLI rejects invalid detail level choices."""
        runner = CliRunner()
        result = runner.invoke(main, ["--paper", "paper.txt", "--detail", "extreme"])
        assert result.exit_code != 0


# --- Test output formatting ---

class TestFormatOutput:
    """Tests for the format_output display function."""

    def test_format_output_runs_without_error(self, capsys):
        """Test that format_output executes without raising exceptions."""
        results = {key: f"Sample content for {title}." for key, title, _ in SECTIONS}
        # Should not raise any exceptions
        format_output(results)

    def test_format_output_handles_missing_sections(self, capsys):
        """Test that format_output handles missing section keys gracefully."""
        results = {"title_authors": "Test Paper by Test Author"}
        # Should not raise even with partial results
        format_output(results)

    def test_format_output_handles_empty_results(self, capsys):
        """Test that format_output handles an empty results dictionary."""
        format_output({})
