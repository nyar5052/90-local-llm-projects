"""Unit tests for Reading Comprehension Builder."""

import json
import pytest
from unittest.mock import patch
from click.testing import CliRunner

from app import main, generate_comprehension, display_exercise


SAMPLE_EXERCISE = {
    "title": "Understanding Climate Change",
    "topic": "Climate Change",
    "reading_level": "high school",
    "passage": "Climate change refers to long-term shifts in temperatures and weather patterns. These shifts may be natural, such as through variations in the solar cycle. But since the 1800s, human activities have been the main driver of climate change, primarily due to burning fossil fuels like coal, oil, and gas.",
    "word_count": 350,
    "vocabulary_words": [
        {"word": "fossil fuels", "definition": "Natural fuels formed from remains of organisms"},
        {"word": "greenhouse effect", "definition": "Warming of Earth's surface by trapped heat"}
    ],
    "questions": [
        {
            "number": 1,
            "type": "factual",
            "question": "What has been the main driver of climate change since the 1800s?",
            "options": [
                "A) Solar variations",
                "B) Human activities",
                "C) Volcanic eruptions",
                "D) Ocean currents"
            ],
            "answer": "B",
            "explanation": "The passage states human activities have been the main driver.",
            "difficulty": "easy"
        },
        {
            "number": 2,
            "type": "vocabulary",
            "question": "What are 'fossil fuels' as used in the passage?",
            "options": [
                "A) Renewable energy sources",
                "B) Fuels from remains of ancient organisms",
                "C) Synthetic chemicals",
                "D) Nuclear materials"
            ],
            "answer": "B",
            "explanation": "Fossil fuels are formed from remains of ancient organisms.",
            "difficulty": "easy"
        },
        {
            "number": 3,
            "type": "inferential",
            "question": "What can be inferred about climate change before the 1800s?",
            "options": [
                "A) It did not occur",
                "B) It was primarily driven by natural causes",
                "C) It was caused by agriculture",
                "D) It was more severe than today"
            ],
            "answer": "B",
            "explanation": "The passage implies natural factors drove climate shifts before industrialization.",
            "difficulty": "medium"
        }
    ],
    "summary": "The passage explains climate change, its causes, and the role of human activities."
}


@patch("app.chat")
def test_generate_comprehension_parses_json(mock_chat):
    """Test that generate_comprehension correctly parses LLM JSON response."""
    mock_chat.return_value = json.dumps(SAMPLE_EXERCISE)
    result = generate_comprehension("Climate Change", "high school", 3)
    assert result["title"] == "Understanding Climate Change"
    assert len(result["questions"]) == 3
    assert result["passage"] != ""


@patch("app.chat")
def test_generate_comprehension_with_length(mock_chat):
    """Test exercise generation with different passage lengths."""
    mock_chat.return_value = json.dumps(SAMPLE_EXERCISE)
    generate_comprehension("Science", "middle school", 5, "long")
    call_content = mock_chat.call_args[1]["messages"][0]["content"]
    assert "600" in call_content


@patch("app.check_ollama_running", return_value=True)
@patch("app.chat")
def test_cli_basic_run(mock_chat, mock_check):
    """Test CLI runs successfully."""
    mock_chat.return_value = json.dumps(SAMPLE_EXERCISE)
    runner = CliRunner()
    result = runner.invoke(main, ["--topic", "Climate Change", "--level", "high school"])
    assert result.exit_code == 0
    assert "Reading Comprehension Builder" in result.output


@patch("app.check_ollama_running", return_value=True)
@patch("app.chat")
def test_cli_save_output(mock_chat, mock_check, tmp_path):
    """Test CLI saves exercise to JSON file."""
    mock_chat.return_value = json.dumps(SAMPLE_EXERCISE)
    outfile = str(tmp_path / "exercise.json")
    runner = CliRunner()
    result = runner.invoke(main, ["--topic", "Climate", "--output", outfile])
    assert result.exit_code == 0
    with open(outfile) as f:
        data = json.load(f)
    assert data["title"] == "Understanding Climate Change"


@patch("app.check_ollama_running", return_value=False)
def test_cli_ollama_not_running(mock_check):
    """Test CLI exits when Ollama is not running."""
    runner = CliRunner()
    result = runner.invoke(main, ["--topic", "Science"])
    assert result.exit_code != 0
    assert "Ollama is not running" in result.output
