"""Tests for the Textbook Chapter Summarizer."""

import os
import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner

from app import (
    read_chapter_file,
    detect_chapter_info,
    summarize_chapter,
    display_summary,
    main,
    STYLE_PROMPTS,
)


SAMPLE_CHAPTER = (
    "Chapter 3: Thermodynamics\n\n"
    "Thermodynamics is the branch of physics that deals with heat, work, and "
    "temperature, and their relation to energy, entropy, and the physical "
    "properties of matter.\n\n"
    "Key definitions:\n"
    "- Entropy: A measure of the disorder or randomness in a system.\n"
    "- Enthalpy: The total heat content of a system.\n\n"
    "The first law of thermodynamics states that energy cannot be created or "
    "destroyed, only transformed. This is expressed as:\n"
    "  ΔU = Q - W\n"
    "where ΔU is internal energy change, Q is heat added, and W is work done.\n\n"
    "The second law states that entropy of an isolated system always increases.\n"
)

MOCK_SUMMARY = (
    "## Chapter Title\n"
    "Chapter 3: Thermodynamics\n\n"
    "## Key Concepts\n"
    "- First law of thermodynamics\n"
    "- Second law of thermodynamics\n\n"
    "## Definitions\n"
    "- **Entropy**: Measure of disorder in a system.\n"
    "- **Enthalpy**: Total heat content of a system.\n\n"
    "## Formulas & Equations\n"
    "- ΔU = Q - W\n\n"
    "## Summary\n"
    "This chapter covers the fundamentals of thermodynamics.\n\n"
    "## Review Questions\n"
    "- What is the first law of thermodynamics?\n"
    "- Define entropy.\n"
)


@pytest.fixture
def sample_file(tmp_path):
    """Create a temporary chapter text file for testing."""
    filepath = tmp_path / "chapter3.txt"
    filepath.write_text(SAMPLE_CHAPTER, encoding="utf-8")
    return str(filepath)


@pytest.fixture
def empty_file(tmp_path):
    """Create an empty temporary file for testing."""
    filepath = tmp_path / "empty.txt"
    filepath.write_text("", encoding="utf-8")
    return str(filepath)


class TestReadChapterFile:
    """Tests for the read_chapter_file function."""

    def test_read_valid_file(self, sample_file):
        """Test reading a valid chapter text file."""
        content = read_chapter_file(sample_file)
        assert "Thermodynamics" in content
        assert "ΔU = Q - W" in content
        assert len(content) > 0

    def test_read_nonexistent_file(self):
        """Test that reading a nonexistent file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError, match="File not found"):
            read_chapter_file("nonexistent_chapter.txt")

    def test_read_empty_file(self, empty_file):
        """Test reading an empty file returns an empty string."""
        content = read_chapter_file(empty_file)
        assert content == ""


class TestDetectChapterInfo:
    """Tests for the detect_chapter_info function."""

    def test_detect_standard_chapter(self):
        """Test detection of standard 'Chapter N: Title' format."""
        text = "Chapter 3: Thermodynamics\n\nSome content here."
        result = detect_chapter_info(text)
        assert "Chapter 3" in result
        assert "Thermodynamics" in result

    def test_detect_chapter_number_only(self):
        """Test detection of chapter number without title."""
        text = "Chapter 7\n\nContent follows."
        result = detect_chapter_info(text)
        assert "Chapter 7" in result

    def test_detect_unit_heading(self):
        """Test detection of 'Unit N: Title' format."""
        text = "Unit 2: Linear Algebra\n\nVectors and matrices."
        result = detect_chapter_info(text)
        assert "Unit 2" in result
        assert "Linear Algebra" in result

    def test_detect_lesson_heading(self):
        """Test detection of 'Lesson N: Title' format."""
        text = "Lesson 5: Cell Biology\n\nThe cell is the basic unit."
        result = detect_chapter_info(text)
        assert "Lesson 5" in result

    def test_unknown_chapter_no_heading(self):
        """Test that text without a chapter heading returns 'Unknown Chapter'."""
        text = "This is just some content without a chapter heading."
        result = detect_chapter_info(text)
        assert result == "Unknown Chapter"

    def test_detect_chapter_dash_separator(self):
        """Test detection with dash separator."""
        text = "Chapter 10 - Organic Chemistry\n\nCarbon compounds."
        result = detect_chapter_info(text)
        assert "Chapter 10" in result
        assert "Organic Chemistry" in result


class TestSummarizeChapter:
    """Tests for the summarize_chapter function."""

    @patch("app.generate", return_value=MOCK_SUMMARY)
    def test_summarize_concise_style(self, mock_generate):
        """Test summarization with the concise style."""
        result = summarize_chapter(SAMPLE_CHAPTER, style="concise")
        assert result == MOCK_SUMMARY
        mock_generate.assert_called_once()
        call_kwargs = mock_generate.call_args
        assert call_kwargs.kwargs["temperature"] == 0.4
        assert "concise" in call_kwargs.kwargs["prompt"].lower() or "bullet" in call_kwargs.kwargs["prompt"].lower()

    @patch("app.generate", return_value=MOCK_SUMMARY)
    def test_summarize_detailed_style(self, mock_generate):
        """Test summarization with the detailed style."""
        result = summarize_chapter(SAMPLE_CHAPTER, style="detailed")
        assert result == MOCK_SUMMARY
        mock_generate.assert_called_once()
        call_kwargs = mock_generate.call_args
        assert "detailed" in call_kwargs.kwargs["prompt"].lower() or "in-depth" in call_kwargs.kwargs["prompt"].lower()

    @patch("app.generate", return_value=MOCK_SUMMARY)
    def test_summarize_study_guide_style(self, mock_generate):
        """Test summarization with the study-guide style."""
        result = summarize_chapter(SAMPLE_CHAPTER, style="study-guide")
        assert result == MOCK_SUMMARY
        mock_generate.assert_called_once()
        call_kwargs = mock_generate.call_args
        assert "study guide" in call_kwargs.kwargs["prompt"].lower() or "flashcard" in call_kwargs.kwargs["prompt"].lower()

    def test_summarize_invalid_style(self):
        """Test that an invalid style raises ValueError."""
        with pytest.raises(ValueError, match="Invalid style"):
            summarize_chapter(SAMPLE_CHAPTER, style="invalid")

    @patch("app.generate", return_value=MOCK_SUMMARY)
    def test_summarize_passes_system_prompt(self, mock_generate):
        """Test that the system prompt is passed to the LLM."""
        summarize_chapter(SAMPLE_CHAPTER, style="concise")
        call_kwargs = mock_generate.call_args
        assert call_kwargs.kwargs["system_prompt"] is not None
        assert "tutor" in call_kwargs.kwargs["system_prompt"].lower()


class TestCLI:
    """Tests for the Click CLI interface."""

    @patch("app.check_ollama_running", return_value=True)
    @patch("app.generate", return_value=MOCK_SUMMARY)
    def test_cli_with_valid_file(self, mock_generate, mock_ollama, sample_file):
        """Test CLI with a valid file argument."""
        runner = CliRunner()
        result = runner.invoke(main, ["--file", sample_file, "--style", "concise"])
        assert result.exit_code == 0
        assert "Textbook Chapter Summarizer" in result.output

    def test_cli_missing_file_option(self):
        """Test CLI exits with error when --file is not provided."""
        runner = CliRunner()
        result = runner.invoke(main, [])
        assert result.exit_code != 0
        assert "Missing" in result.output or "required" in result.output.lower() or "Error" in result.output

    def test_cli_nonexistent_file(self):
        """Test CLI exits with error when file does not exist."""
        runner = CliRunner()
        result = runner.invoke(main, ["--file", "no_such_file.txt"])
        assert result.exit_code != 0

    def test_cli_invalid_style(self):
        """Test CLI rejects invalid style choices."""
        runner = CliRunner()
        result = runner.invoke(main, ["--file", "dummy.txt", "--style", "wrong"])
        assert result.exit_code != 0
        assert "Invalid" in result.output or "invalid" in result.output

    @patch("app.check_ollama_running", return_value=False)
    def test_cli_ollama_not_running(self, mock_ollama, sample_file):
        """Test CLI exits gracefully when Ollama is not running."""
        runner = CliRunner()
        result = runner.invoke(main, ["--file", sample_file])
        assert result.exit_code != 0
        assert "Ollama" in result.output

    @patch("app.check_ollama_running", return_value=True)
    @patch("app.generate", return_value=MOCK_SUMMARY)
    def test_cli_detailed_style(self, mock_generate, mock_ollama, sample_file):
        """Test CLI runs successfully with detailed style."""
        runner = CliRunner()
        result = runner.invoke(main, ["--file", sample_file, "--style", "detailed"])
        assert result.exit_code == 0

    @patch("app.check_ollama_running", return_value=True)
    @patch("app.generate", return_value=MOCK_SUMMARY)
    def test_cli_study_guide_style(self, mock_generate, mock_ollama, sample_file):
        """Test CLI runs successfully with study-guide style."""
        runner = CliRunner()
        result = runner.invoke(main, ["--file", sample_file, "--style", "study-guide"])
        assert result.exit_code == 0


class TestStylePrompts:
    """Tests for style prompt templates."""

    def test_all_styles_have_prompts(self):
        """Test that all three styles have corresponding prompt templates."""
        assert "concise" in STYLE_PROMPTS
        assert "detailed" in STYLE_PROMPTS
        assert "study-guide" in STYLE_PROMPTS

    def test_prompts_contain_text_placeholder(self):
        """Test that all prompts contain the {text} placeholder."""
        for style, prompt in STYLE_PROMPTS.items():
            assert "{text}" in prompt, f"Style '{style}' missing {{text}} placeholder"

    def test_prompts_request_required_sections(self):
        """Test that all prompts request the core sections."""
        required_sections = ["Key Concepts", "Definitions", "Summary"]
        for style, prompt in STYLE_PROMPTS.items():
            for section in required_sections:
                assert section in prompt, (
                    f"Style '{style}' missing required section '{section}'"
                )
