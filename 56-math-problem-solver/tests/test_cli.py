"""Unit tests for Math Problem Solver CLI."""

import json
import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner

from src.math_solver.cli import cli
from src.math_solver.core import MathProblemResult, Solution, SolutionStep


SAMPLE_RESULT = MathProblemResult(
    problem="Solve 2x + 5 = 15",
    category="algebra",
    difficulty="basic",
    solution=Solution(
        answer="x = 5",
        steps=[
            SolutionStep(step_number=1, description="Subtract 5", work="2x=10", explanation="Isolate x"),
            SolutionStep(step_number=2, description="Divide by 2", work="x=5", explanation="Solve"),
        ],
    ),
    concepts_used=["Linear equations"],
    tips=["Check your work"],
    related_problems=["3x-7=20"],
    latex_output="x=5",
)


@patch("src.math_solver.cli.check_service", return_value=True)
@patch("src.math_solver.cli.solve_problem", return_value=SAMPLE_RESULT)
def test_cli_solve_basic(mock_solve, mock_check):
    runner = CliRunner()
    result = runner.invoke(cli, ["solve", "--problem", "solve 2x + 5 = 15"])
    assert result.exit_code == 0
    assert "Math Problem Solver" in result.output


@patch("src.math_solver.cli.check_service", return_value=True)
@patch("src.math_solver.cli.solve_problem", return_value=SAMPLE_RESULT)
def test_cli_solve_save_output(mock_solve, mock_check, tmp_path):
    outfile = str(tmp_path / "solution.json")
    runner = CliRunner()
    result = runner.invoke(cli, ["solve", "--problem", "2x=10", "--output", outfile])
    assert result.exit_code == 0
    with open(outfile) as f:
        data = json.load(f)
    assert data["solution"]["answer"] == "x = 5"


@patch("src.math_solver.cli.check_service", return_value=False)
def test_cli_solve_ollama_not_running(mock_check):
    runner = CliRunner()
    result = runner.invoke(cli, ["solve", "--problem", "2+2"])
    assert result.exit_code != 0
    assert "Ollama is not running" in result.output


def test_cli_formulas():
    runner = CliRunner()
    result = runner.invoke(cli, ["formulas", "--category", "algebra"])
    assert result.exit_code == 0
    assert "Quadratic" in result.output


@patch("src.math_solver.cli.check_service", return_value=True)
@patch("src.math_solver.cli.generate_practice_problems")
def test_cli_practice(mock_gen, mock_check):
    mock_gen.return_value = {
        "category": "algebra",
        "difficulty": "basic",
        "problems": [{"number": 1, "problem": "x+1=2", "hint": "subtract 1", "answer": "1"}],
    }
    runner = CliRunner()
    result = runner.invoke(cli, ["practice", "--category", "algebra"])
    assert result.exit_code == 0
    assert "Practice" in result.output
