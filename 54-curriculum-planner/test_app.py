"""Unit tests for Curriculum Planner."""

import json
import pytest
from unittest.mock import patch
from click.testing import CliRunner

from app import main, generate_curriculum, display_curriculum


SAMPLE_CURRICULUM = {
    "course_title": "Intro to Machine Learning",
    "level": "beginner",
    "duration_weeks": 4,
    "description": "A foundational course in machine learning concepts.",
    "learning_objectives": [
        "Understand basic ML concepts",
        "Implement simple models in Python"
    ],
    "prerequisites": ["Basic Python", "Linear Algebra"],
    "weekly_plan": [
        {
            "week": 1,
            "title": "Introduction to ML",
            "topics": ["What is ML?", "Types of learning"],
            "learning_goals": ["Define ML"],
            "activities": ["Read chapter 1", "Setup environment"],
            "assessment": "Quiz 1"
        },
        {
            "week": 2,
            "title": "Supervised Learning",
            "topics": ["Regression", "Classification"],
            "learning_goals": ["Implement linear regression"],
            "activities": ["Lab: Linear regression"],
            "assessment": "Assignment 1"
        }
    ],
    "resources": [
        {"type": "textbook", "title": "Hands-On ML", "description": "By Aurélien Géron"},
        {"type": "video", "title": "ML Course", "description": "Stanford CS229"}
    ],
    "assessment_strategy": "Weekly quizzes, 2 assignments, final project."
}


@patch("app.chat")
def test_generate_curriculum_parses_json(mock_chat):
    """Test that generate_curriculum correctly parses LLM JSON response."""
    mock_chat.return_value = json.dumps(SAMPLE_CURRICULUM)
    result = generate_curriculum("Intro to ML", 4, "beginner")
    assert result["course_title"] == "Intro to Machine Learning"
    assert len(result["weekly_plan"]) == 2


@patch("app.chat")
def test_generate_curriculum_with_focus(mock_chat):
    """Test curriculum generation with special focus areas."""
    mock_chat.return_value = json.dumps(SAMPLE_CURRICULUM)
    result = generate_curriculum("ML", 4, "beginner", focus="neural networks")
    call_content = mock_chat.call_args[1]["messages"][0]["content"]
    assert "neural networks" in call_content


@patch("app.check_ollama_running", return_value=True)
@patch("app.chat")
def test_cli_basic_run(mock_chat, mock_check):
    """Test CLI runs successfully."""
    mock_chat.return_value = json.dumps(SAMPLE_CURRICULUM)
    runner = CliRunner()
    result = runner.invoke(main, ["--course", "ML Intro", "--weeks", "4"])
    assert result.exit_code == 0
    assert "Curriculum Planner" in result.output


@patch("app.check_ollama_running", return_value=True)
@patch("app.chat")
def test_cli_save_output(mock_chat, mock_check, tmp_path):
    """Test CLI saves curriculum to JSON file."""
    mock_chat.return_value = json.dumps(SAMPLE_CURRICULUM)
    outfile = str(tmp_path / "curriculum.json")
    runner = CliRunner()
    result = runner.invoke(main, ["--course", "ML", "--output", outfile])
    assert result.exit_code == 0
    with open(outfile) as f:
        data = json.load(f)
    assert data["course_title"] == "Intro to Machine Learning"


@patch("app.check_ollama_running", return_value=False)
def test_cli_ollama_not_running(mock_check):
    """Test CLI exits when Ollama is not running."""
    runner = CliRunner()
    result = runner.invoke(main, ["--course", "ML"])
    assert result.exit_code != 0
    assert "Ollama is not running" in result.output
