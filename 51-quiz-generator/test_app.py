"""Unit tests for Quiz Generator."""

import json
import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner

from app import main, generate_quiz, display_quiz, SYSTEM_PROMPT


SAMPLE_QUIZ = {
    "title": "World War II Quiz",
    "topic": "World War II",
    "questions": [
        {
            "number": 1,
            "type": "multiple-choice",
            "question": "When did World War II begin?",
            "options": ["A) 1935", "B) 1939", "C) 1941", "D) 1945"],
            "answer": "B",
            "explanation": "WWII started in September 1939."
        },
        {
            "number": 2,
            "type": "true-false",
            "question": "The United States entered WWII after Pearl Harbor.",
            "options": ["True", "False"],
            "answer": "True",
            "explanation": "Pearl Harbor was attacked on December 7, 1941."
        },
        {
            "number": 3,
            "type": "short-answer",
            "question": "Who was the British Prime Minister during most of WWII?",
            "answer": "Winston Churchill",
            "explanation": "Churchill served as PM from 1940 to 1945."
        }
    ]
}


@patch("app.chat")
def test_generate_quiz_parses_json(mock_chat):
    """Test that generate_quiz correctly parses LLM JSON response."""
    mock_chat.return_value = json.dumps(SAMPLE_QUIZ)
    result = generate_quiz("World War II", 3, "mixed", "medium")
    assert result["title"] == "World War II Quiz"
    assert len(result["questions"]) == 3
    mock_chat.assert_called_once()


@patch("app.chat")
def test_generate_quiz_handles_code_blocks(mock_chat):
    """Test that generate_quiz strips markdown code blocks."""
    mock_chat.return_value = f"```json\n{json.dumps(SAMPLE_QUIZ)}\n```"
    result = generate_quiz("World War II", 3, "mixed", "medium")
    assert result["title"] == "World War II Quiz"
    assert len(result["questions"]) == 3


@patch("app.check_ollama_running", return_value=True)
@patch("app.chat")
def test_cli_basic_run(mock_chat, mock_check):
    """Test CLI runs successfully with basic options."""
    mock_chat.return_value = json.dumps(SAMPLE_QUIZ)
    runner = CliRunner()
    result = runner.invoke(main, ["--topic", "World War II", "--questions", "3"])
    assert result.exit_code == 0
    assert "Quiz Generator" in result.output


@patch("app.check_ollama_running", return_value=True)
@patch("app.chat")
def test_cli_output_to_file(mock_chat, mock_check, tmp_path):
    """Test CLI saves quiz to JSON file."""
    mock_chat.return_value = json.dumps(SAMPLE_QUIZ)
    outfile = str(tmp_path / "quiz.json")
    runner = CliRunner()
    result = runner.invoke(main, ["--topic", "History", "--output", outfile])
    assert result.exit_code == 0
    with open(outfile) as f:
        data = json.load(f)
    assert data["title"] == "World War II Quiz"


@patch("app.check_ollama_running", return_value=False)
def test_cli_ollama_not_running(mock_check):
    """Test CLI exits gracefully when Ollama is not running."""
    runner = CliRunner()
    result = runner.invoke(main, ["--topic", "Math"])
    assert result.exit_code != 0
    assert "Ollama is not running" in result.output
