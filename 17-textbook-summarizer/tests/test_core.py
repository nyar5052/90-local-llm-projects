"""Tests for the Textbook Summarizer core module."""

import os
import pytest
from unittest.mock import patch

from src.textbook_summarizer.core import (
    read_chapter_file,
    detect_chapter_info,
    summarize_chapter,
    generate_glossary,
    generate_concept_map,
    generate_study_questions,
    STYLE_PROMPTS,
)
from src.textbook_summarizer.utils import split_chapters, count_words


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
    filepath = tmp_path / "chapter3.txt"
    filepath.write_text(SAMPLE_CHAPTER, encoding="utf-8")
    return str(filepath)


@pytest.fixture
def empty_file(tmp_path):
    filepath = tmp_path / "empty.txt"
    filepath.write_text("", encoding="utf-8")
    return str(filepath)


class TestReadChapterFile:
    def test_read_valid_file(self, sample_file):
        content = read_chapter_file(sample_file)
        assert "Thermodynamics" in content

    def test_read_nonexistent_file(self):
        with pytest.raises(FileNotFoundError, match="File not found"):
            read_chapter_file("nonexistent_chapter.txt")

    def test_read_empty_file(self, empty_file):
        content = read_chapter_file(empty_file)
        assert content == ""


class TestDetectChapterInfo:
    def test_detect_standard_chapter(self):
        text = "Chapter 3: Thermodynamics\n\nSome content here."
        result = detect_chapter_info(text)
        assert "Chapter 3" in result

    def test_detect_chapter_number_only(self):
        text = "Chapter 7\n\nContent follows."
        result = detect_chapter_info(text)
        assert "Chapter 7" in result

    def test_unknown_chapter_no_heading(self):
        text = "This is just some content without a chapter heading."
        result = detect_chapter_info(text)
        assert result == "Unknown Chapter"


class TestSummarizeChapter:
    @patch("src.textbook_summarizer.core.generate", return_value=MOCK_SUMMARY)
    def test_summarize_concise_style(self, mock_generate):
        result = summarize_chapter(SAMPLE_CHAPTER, style="concise")
        assert result == MOCK_SUMMARY
        mock_generate.assert_called_once()

    @patch("src.textbook_summarizer.core.generate", return_value=MOCK_SUMMARY)
    def test_summarize_detailed_style(self, mock_generate):
        result = summarize_chapter(SAMPLE_CHAPTER, style="detailed")
        assert result == MOCK_SUMMARY

    def test_summarize_invalid_style(self):
        with pytest.raises(ValueError, match="Invalid style"):
            summarize_chapter(SAMPLE_CHAPTER, style="invalid")


class TestGenerateGlossary:
    @patch("src.textbook_summarizer.core.generate", return_value="**Entropy**: disorder")
    def test_generate_glossary(self, mock_generate):
        result = generate_glossary(SAMPLE_CHAPTER)
        assert "Entropy" in result


class TestGenerateConceptMap:
    @patch("src.textbook_summarizer.core.generate", return_value="**Thermo** → Heat, Energy")
    def test_generate_concept_map(self, mock_generate):
        result = generate_concept_map(SAMPLE_CHAPTER)
        assert "Thermo" in result


class TestGenerateStudyQuestions:
    @patch("src.textbook_summarizer.core.generate", return_value="1. What is entropy?")
    def test_generate_study_questions(self, mock_generate):
        result = generate_study_questions(SAMPLE_CHAPTER, num_questions=5)
        assert "entropy" in result.lower()


class TestUtilities:
    def test_count_words(self):
        assert count_words("hello world foo bar") == 4

    def test_split_chapters_no_headings(self):
        chapters = split_chapters("Just some text without headings.")
        assert len(chapters) == 1
        assert chapters[0]["title"] == "Full Document"

    def test_split_chapters_with_headings(self):
        text = "Chapter 1: Intro\nContent 1\n\nChapter 2: Advanced\nContent 2"
        chapters = split_chapters(text)
        assert len(chapters) == 2


class TestStylePrompts:
    def test_all_styles_have_prompts(self):
        assert "concise" in STYLE_PROMPTS
        assert "detailed" in STYLE_PROMPTS
        assert "study-guide" in STYLE_PROMPTS

    def test_prompts_contain_text_placeholder(self):
        for style, prompt in STYLE_PROMPTS.items():
            assert "{text}" in prompt
