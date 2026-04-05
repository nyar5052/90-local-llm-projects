"""Tests for the Research Paper QA core module."""

import os
import pytest
from unittest.mock import patch

from src.research_qa.core import (
    load_paper,
    load_multiple_papers,
    build_system_prompt,
    build_multi_paper_content,
    ask_question,
    suggest_followup_questions,
    extract_citations,
)
from src.research_qa.utils import export_notes


@pytest.fixture
def sample_paper(tmp_path):
    paper_file = tmp_path / "sample_paper.txt"
    paper_file.write_text(
        "Title: Neural Networks for NLP\n\n"
        "Abstract: This paper explores the use of neural networks "
        "for natural language processing tasks.\n\n"
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
    paper_file = tmp_path / "empty.txt"
    paper_file.write_text("", encoding="utf-8")
    return str(paper_file)


@pytest.fixture
def second_paper(tmp_path):
    paper_file = tmp_path / "paper2.txt"
    paper_file.write_text(
        "Title: CNN for Image Recognition\n\n"
        "Abstract: This paper studies convolutional neural networks.",
        encoding="utf-8",
    )
    return str(paper_file)


class TestLoadPaper:
    def test_load_valid_paper(self, sample_paper):
        content = load_paper(sample_paper)
        assert "Neural Networks for NLP" in content

    def test_load_nonexistent_file(self):
        with pytest.raises(FileNotFoundError, match="Paper not found"):
            load_paper("nonexistent_paper.txt")

    def test_load_empty_paper(self, empty_paper):
        with pytest.raises(ValueError, match="Paper file is empty"):
            load_paper(empty_paper)

    def test_load_paper_content_complete(self, sample_paper):
        content = load_paper(sample_paper)
        assert "Abstract" in content
        assert "Methodology" in content
        assert "Conclusion" in content


class TestMultiPaper:
    def test_load_multiple_papers(self, sample_paper, second_paper):
        papers = load_multiple_papers([sample_paper, second_paper])
        assert len(papers) == 2

    def test_build_multi_paper_content(self):
        papers = {"paper1.txt": "Content 1", "paper2.txt": "Content 2"}
        combined = build_multi_paper_content(papers)
        assert "paper1.txt" in combined
        assert "paper2.txt" in combined
        assert "Content 1" in combined


class TestBuildSystemPrompt:
    def test_system_prompt_contains_paper(self):
        paper = "This is a test paper about quantum computing."
        prompt = build_system_prompt(paper)
        assert "quantum computing" in prompt
        assert "PAPER CONTENT" in prompt

    def test_system_prompt_has_instructions(self):
        prompt = build_system_prompt("Some paper content.")
        assert "research paper" in prompt.lower()


class TestAskQuestion:
    @patch("src.research_qa.core.chat")
    def test_ask_question_returns_response(self, mock_chat):
        mock_chat.return_value = "The paper discusses neural networks."
        history = []
        answer = ask_question("What is the paper about?", history, "system prompt")
        assert answer == "The paper discusses neural networks."

    @patch("src.research_qa.core.chat")
    def test_ask_question_updates_history(self, mock_chat):
        mock_chat.return_value = "The accuracy was 95.2%."
        history = []
        ask_question("What was the accuracy?", history, "system prompt")
        assert len(history) == 2
        assert history[0]["role"] == "user"
        assert history[1]["role"] == "assistant"

    @patch("src.research_qa.core.chat")
    def test_ask_question_preserves_context(self, mock_chat):
        mock_chat.return_value = "Follow-up answer."
        history = [
            {"role": "user", "content": "First question"},
            {"role": "assistant", "content": "First answer"},
        ]
        ask_question("Follow-up question", history, "system prompt")
        assert len(history) == 4


class TestSuggestFollowup:
    @patch("src.research_qa.core.chat")
    def test_suggest_followup_returns_suggestions(self, mock_chat):
        mock_chat.return_value = "1. What about the limitations?"
        history = [
            {"role": "user", "content": "What is this paper about?"},
            {"role": "assistant", "content": "It's about NLP."},
        ]
        result = suggest_followup_questions(history, "system prompt")
        assert "limitations" in result.lower()


class TestExtractCitations:
    def test_extract_paper_citation(self):
        text = "According to [Paper: main.txt, Section: 3], the accuracy was 95%."
        citations = extract_citations(text)
        assert len(citations) >= 1

    def test_no_citations(self):
        text = "There are no citations in this text."
        citations = extract_citations(text)
        assert len(citations) == 0


class TestExportNotes:
    def test_export_markdown(self, tmp_path):
        history = [
            {"role": "user", "content": "What is this about?"},
            {"role": "assistant", "content": "It's about AI."},
        ]
        filepath = str(tmp_path / "notes.md")
        saved = export_notes(history, filepath, fmt="markdown")
        assert os.path.exists(saved)
        content = open(saved, encoding="utf-8").read()
        assert "Question" in content

    def test_export_json(self, tmp_path):
        history = [{"role": "user", "content": "Test"}]
        filepath = str(tmp_path / "notes.json")
        saved = export_notes(history, filepath, fmt="json")
        assert os.path.exists(saved)

    def test_export_text(self, tmp_path):
        history = [{"role": "user", "content": "Test"}]
        filepath = str(tmp_path / "notes.txt")
        saved = export_notes(history, filepath, fmt="text")
        assert os.path.exists(saved)
