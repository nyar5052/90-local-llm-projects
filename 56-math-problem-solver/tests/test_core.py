"""Unit tests for Math Problem Solver core module."""

import json
import pytest
from unittest.mock import patch, MagicMock

from src.math_solver.core import (
    solve_problem,
    generate_practice_problems,
    get_formula_library,
    _parse_json_response,
    _result_from_dict,
    MathProblemResult,
    SolutionStep,
    Solution,
)


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
                "explanation": "Isolate the variable term",
            },
            {
                "step_number": 2,
                "description": "Divide both sides by 2",
                "work": "2x / 2 = 10 / 2\nx = 5",
                "explanation": "Solve for x",
            },
        ],
    },
    "concepts_used": ["Linear equations", "Inverse operations"],
    "tips": ["Always perform the same operation on both sides"],
    "related_problems": ["Solve 3x - 7 = 20"],
    "latex_output": "x = 5",
}


class TestParseJsonResponse:
    def test_plain_json(self):
        result = _parse_json_response(json.dumps({"key": "value"}))
        assert result == {"key": "value"}

    def test_json_in_code_fence(self):
        text = "```json\n{\"key\": \"value\"}\n```"
        result = _parse_json_response(text)
        assert result == {"key": "value"}

    def test_invalid_json_raises(self):
        with pytest.raises(json.JSONDecodeError):
            _parse_json_response("not json")


class TestResultFromDict:
    def test_converts_correctly(self):
        result = _result_from_dict(SAMPLE_SOLUTION)
        assert isinstance(result, MathProblemResult)
        assert result.solution.answer == "x = 5"
        assert len(result.solution.steps) == 2
        assert result.category == "algebra"


class TestGetFormulaLibrary:
    def test_returns_all_categories(self):
        data = get_formula_library()
        assert "categories" in data

    def test_returns_single_category(self):
        data = get_formula_library("algebra")
        assert data["category"] == "algebra"
        assert len(data["formulas"]) > 0

    def test_unknown_category_returns_all(self):
        data = get_formula_library("unknown")
        assert "categories" in data


@patch("src.math_solver.core._get_llm_client")
def test_solve_problem(mock_client):
    mock_chat = MagicMock(return_value=json.dumps(SAMPLE_SOLUTION))
    mock_client.return_value = (mock_chat, MagicMock())
    result = solve_problem("Solve 2x + 5 = 15")
    assert result.solution.answer == "x = 5"
    assert len(result.solution.steps) == 2


@patch("src.math_solver.core._get_llm_client")
def test_solve_problem_with_category(mock_client):
    mock_chat = MagicMock(return_value=json.dumps(SAMPLE_SOLUTION))
    mock_client.return_value = (mock_chat, MagicMock())
    result = solve_problem("2x + 5 = 15", category="algebra")
    call_content = mock_chat.call_args[1]["messages"][0]["content"]
    assert "algebra" in call_content


@patch("src.math_solver.core._get_llm_client")
def test_generate_practice_problems(mock_client):
    practice_data = {
        "category": "algebra",
        "difficulty": "basic",
        "problems": [{"number": 1, "problem": "x+1=2", "hint": "subtract", "answer": "1"}],
    }
    mock_chat = MagicMock(return_value=json.dumps(practice_data))
    mock_client.return_value = (mock_chat, MagicMock())
    result = generate_practice_problems("algebra", "basic", 1)
    assert len(result["problems"]) == 1
