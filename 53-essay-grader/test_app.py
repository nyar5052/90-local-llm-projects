"""Unit tests for Essay Grader."""

import json
import pytest
from unittest.mock import patch
from click.testing import CliRunner

from app import main, grade_essay, read_essay, display_grade


SAMPLE_GRADE = {
    "overall_score": 7.5,
    "overall_grade": "B+",
    "criteria": [
        {"name": "clarity", "score": 8, "max_score": 10, "feedback": "Well written."},
        {"name": "argument", "score": 7, "max_score": 10, "feedback": "Solid thesis."},
        {"name": "evidence", "score": 7, "max_score": 10, "feedback": "Good sources."}
    ],
    "strengths": ["Clear thesis statement", "Good use of transitions"],
    "weaknesses": ["Needs more evidence in paragraph 3"],
    "suggestions": ["Add more primary sources", "Strengthen conclusion"],
    "summary": "A solid essay with room for improvement in evidence."
}


@patch("app.chat")
def test_grade_essay_parses_json(mock_chat):
    """Test that grade_essay correctly parses LLM JSON response."""
    mock_chat.return_value = json.dumps(SAMPLE_GRADE)
    result = grade_essay("This is a test essay.", ["clarity", "argument"])
    assert result["overall_score"] == 7.5
    assert len(result["criteria"]) == 3


@patch("app.chat")
def test_grade_essay_with_context(mock_chat):
    """Test grading with assignment context."""
    mock_chat.return_value = json.dumps(SAMPLE_GRADE)
    result = grade_essay("Test essay text.", ["clarity"], context="History assignment")
    mock_chat.assert_called_once()
    call_args = mock_chat.call_args
    assert "History assignment" in call_args[1]["messages"][0]["content"] or \
           "History assignment" in str(call_args)


def test_read_essay_valid_file(tmp_path):
    """Test reading a valid essay file."""
    essay_file = tmp_path / "essay.txt"
    essay_file.write_text("This is my essay about history.")
    result = read_essay(str(essay_file))
    assert result == "This is my essay about history."


@patch("app.check_ollama_running", return_value=True)
@patch("app.chat")
def test_cli_basic_run(mock_chat, mock_check, tmp_path):
    """Test CLI runs with a valid essay file."""
    mock_chat.return_value = json.dumps(SAMPLE_GRADE)
    essay_file = tmp_path / "essay.txt"
    essay_file.write_text("This is a test essay about climate change.")
    runner = CliRunner()
    result = runner.invoke(main, ["--essay", str(essay_file)])
    assert result.exit_code == 0
    assert "Essay Grader" in result.output


@patch("app.check_ollama_running", return_value=False)
def test_cli_ollama_not_running(mock_check, tmp_path):
    """Test CLI exits when Ollama is not running."""
    essay_file = tmp_path / "essay.txt"
    essay_file.write_text("Test essay.")
    runner = CliRunner()
    result = runner.invoke(main, ["--essay", str(essay_file)])
    assert result.exit_code != 0
    assert "Ollama is not running" in result.output
