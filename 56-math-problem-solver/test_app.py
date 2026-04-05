"""Unit tests for Math Problem Solver."""

import json
import pytest
from unittest.mock import patch
from click.testing import CliRunner

from app import main, solve_problem, display_solution


SAMPLE_SOLUTION = {
    "problem": "Solve 2x + 5 = 15",
    "category": "algebra",
    "difficulty": "basic",
    "solution": {
        "answer": "x = 5",
        "steps": [
            {
                "step_number": 1,
                "description": "Subtract 5 from both sides",
                "work": "2x + 5 - 5 = 15 - 5\n2x = 10",
                "explanation": "Isolate the variable term"
            },
            {
                "step_number": 2,
                "description": "Divide both sides by 2",
                "work": "2x / 2 = 10 / 2\nx = 5",
                "explanation": "Solve for x"
            }
        ]
    },
    "concepts_used": ["Linear equations", "Inverse operations"],
    "tips": ["Always perform the same operation on both sides"],
    "related_problems": ["Solve 3x - 7 = 20"]
}


@patch("app.chat")
def test_solve_problem_parses_json(mock_chat):
    """Test that solve_problem correctly parses LLM JSON response."""
    mock_chat.return_value = json.dumps(SAMPLE_SOLUTION)
    result = solve_problem("Solve 2x + 5 = 15")
    assert result["solution"]["answer"] == "x = 5"
    assert len(result["solution"]["steps"]) == 2


@patch("app.chat")
def test_solve_problem_with_category(mock_chat):
    """Test solving with specific category."""
    mock_chat.return_value = json.dumps(SAMPLE_SOLUTION)
    result = solve_problem("2x + 5 = 15", category="algebra")
    call_content = mock_chat.call_args[1]["messages"][0]["content"]
    assert "algebra" in call_content


@patch("app.check_ollama_running", return_value=True)
@patch("app.chat")
def test_cli_basic_run(mock_chat, mock_check):
    """Test CLI runs successfully."""
    mock_chat.return_value = json.dumps(SAMPLE_SOLUTION)
    runner = CliRunner()
    result = runner.invoke(main, ["--problem", "solve 2x + 5 = 15", "--show-steps"])
    assert result.exit_code == 0
    assert "Math Problem Solver" in result.output


@patch("app.check_ollama_running", return_value=True)
@patch("app.chat")
def test_cli_save_output(mock_chat, mock_check, tmp_path):
    """Test CLI saves solution to JSON file."""
    mock_chat.return_value = json.dumps(SAMPLE_SOLUTION)
    outfile = str(tmp_path / "solution.json")
    runner = CliRunner()
    result = runner.invoke(main, ["--problem", "2x=10", "--output", outfile])
    assert result.exit_code == 0
    with open(outfile) as f:
        data = json.load(f)
    assert data["solution"]["answer"] == "x = 5"


@patch("app.check_ollama_running", return_value=False)
def test_cli_ollama_not_running(mock_check):
    """Test CLI exits when Ollama is not running."""
    runner = CliRunner()
    result = runner.invoke(main, ["--problem", "2+2"])
    assert result.exit_code != 0
    assert "Ollama is not running" in result.output
