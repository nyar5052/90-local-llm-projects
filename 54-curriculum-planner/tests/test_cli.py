"""Unit tests for Curriculum Planner CLI."""

import json
import pytest
from unittest.mock import patch
from click.testing import CliRunner

from src.curriculum_planner.cli import cli


SAMPLE_CURRICULUM = {
    "course_title": "Intro to Machine Learning",
    "level": "beginner",
    "duration_weeks": 4,
    "description": "A foundational course in machine learning concepts.",
    "learning_objectives": [
        "Understand basic ML concepts",
        "Implement simple models in Python",
    ],
    "prerequisites": ["Basic Python", "Linear Algebra"],
    "weekly_plan": [
        {
            "week": 1,
            "title": "Introduction to ML",
            "topics": ["What is ML?", "Types of learning"],
            "learning_goals": ["Define ML"],
            "activities": ["Read chapter 1", "Setup environment"],
            "assessment": "Quiz 1",
        },
        {
            "week": 2,
            "title": "Supervised Learning",
            "topics": ["Regression", "Classification"],
            "learning_goals": ["Implement linear regression"],
            "activities": ["Lab: Linear regression"],
            "assessment": "Assignment 1",
        },
    ],
    "resources": [
        {"type": "textbook", "title": "Hands-On ML", "description": "By Aurélien Géron"},
        {"type": "video", "title": "ML Course", "description": "Stanford CS229"},
    ],
    "assessment_strategy": "Weekly quizzes, 2 assignments, final project.",
}


@patch("src.curriculum_planner.cli.check_ollama_running", return_value=True)
@patch("src.curriculum_planner.cli.generate_curriculum")
def test_cli_design_basic(mock_gen, mock_check):
    """Test CLI design command runs successfully."""
    mock_gen.return_value = SAMPLE_CURRICULUM
    runner = CliRunner()
    result = runner.invoke(cli, ["design", "--course", "ML Intro", "--weeks", "4"])
    assert result.exit_code == 0
    assert "Curriculum Planner" in result.output


@patch("src.curriculum_planner.cli.check_ollama_running", return_value=True)
@patch("src.curriculum_planner.cli.generate_curriculum")
def test_cli_design_with_output(mock_gen, mock_check, tmp_path):
    """Test CLI design command saves output to file."""
    mock_gen.return_value = SAMPLE_CURRICULUM
    outfile = str(tmp_path / "curriculum.json")
    runner = CliRunner()
    result = runner.invoke(cli, ["design", "--course", "ML", "--output", outfile])
    assert result.exit_code == 0
    with open(outfile) as f:
        data = json.load(f)
    assert data["course_title"] == "Intro to Machine Learning"


@patch("src.curriculum_planner.cli.check_ollama_running", return_value=False)
def test_cli_ollama_not_running(mock_check):
    """Test CLI exits when Ollama is not running."""
    runner = CliRunner()
    result = runner.invoke(cli, ["design", "--course", "ML"])
    assert result.exit_code != 0
    assert "Ollama is not running" in result.output


def test_cli_help():
    """Test CLI help output."""
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "Curriculum Planner" in result.output


def test_cli_design_help():
    """Test CLI design subcommand help."""
    runner = CliRunner()
    result = runner.invoke(cli, ["design", "--help"])
    assert result.exit_code == 0
    assert "--course" in result.output
    assert "--weeks" in result.output
