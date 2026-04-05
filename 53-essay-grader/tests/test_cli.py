"""Unit tests for Essay Grader CLI."""

import json
import pytest
from unittest.mock import patch
from click.testing import CliRunner

from src.essay_grader.cli import cli


SAMPLE_GRADE = {
    "overall_score": 7.5,
    "overall_grade": "B+",
    "criteria": [
        {"name": "clarity", "score": 8, "max_score": 10, "feedback": "Well written."},
        {"name": "argument", "score": 7, "max_score": 10, "feedback": "Solid thesis."},
    ],
    "strengths": ["Clear thesis"],
    "weaknesses": ["Needs more evidence"],
    "suggestions": ["Add sources"],
    "summary": "Solid essay.",
}


@patch("src.essay_grader.cli.check_ollama_running", return_value=True)
@patch("src.essay_grader.core.chat")
def test_cli_grade_basic(mock_chat, mock_check, tmp_path):
    """Test CLI grade command with a valid essay file."""
    mock_chat.return_value = json.dumps(SAMPLE_GRADE)
    essay_file = tmp_path / "essay.txt"
    essay_file.write_text("This is a test essay about climate change.")
    runner = CliRunner()
    result = runner.invoke(cli, ["grade", "--essay", str(essay_file)])
    assert result.exit_code == 0
    assert "Essay Grader" in result.output


@patch("src.essay_grader.cli.check_ollama_running", return_value=True)
@patch("src.essay_grader.core.chat")
def test_cli_grade_with_rubric(mock_chat, mock_check, tmp_path):
    """Test CLI grade command with a preset rubric."""
    mock_chat.return_value = json.dumps(SAMPLE_GRADE)
    essay_file = tmp_path / "essay.txt"
    essay_file.write_text("Test essay.")
    runner = CliRunner()
    result = runner.invoke(cli, ["grade", "--essay", str(essay_file), "--rubric", "academic"])
    assert result.exit_code == 0


def test_cli_list_rubrics():
    """Test CLI rubrics command lists presets."""
    runner = CliRunner()
    result = runner.invoke(cli, ["rubrics"])
    assert result.exit_code == 0
    assert "academic" in result.output.lower()
    assert "creative" in result.output.lower()


@patch("src.essay_grader.cli.check_ollama_running", return_value=False)
def test_cli_ollama_not_running(mock_check, tmp_path):
    """Test CLI exits when Ollama is not running."""
    essay_file = tmp_path / "essay.txt"
    essay_file.write_text("Test essay.")
    runner = CliRunner()
    result = runner.invoke(cli, ["grade", "--essay", str(essay_file)])
    assert result.exit_code != 0
    assert "Ollama is not running" in result.output
