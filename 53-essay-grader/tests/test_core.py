"""Unit tests for Essay Grader core module."""

import json
import os
import pytest
from unittest.mock import patch, MagicMock
from dataclasses import asdict

from src.essay_grader.core import (
    grade_essay,
    read_essay,
    calculate_grade_letter,
    validate_grade_data,
    export_grade_report,
    parse_response,
    Rubric,
    RubricCriterion,
    GradeResult,
    GradeDistribution,
    InlineAnnotation,
    PlagiarismIndicator,
    PRESET_RUBRICS,
    ConfigManager,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

SAMPLE_GRADE = {
    "overall_score": 7.5,
    "overall_grade": "B+",
    "criteria": [
        {"name": "clarity", "score": 8, "max_score": 10, "feedback": "Well written."},
        {"name": "argument", "score": 7, "max_score": 10, "feedback": "Solid thesis."},
        {"name": "evidence", "score": 7, "max_score": 10, "feedback": "Good sources."},
    ],
    "strengths": ["Clear thesis statement", "Good use of transitions"],
    "weaknesses": ["Needs more evidence in paragraph 3"],
    "suggestions": ["Add more primary sources", "Strengthen conclusion"],
    "summary": "A solid essay with room for improvement in evidence.",
}


@pytest.fixture
def sample_grade():
    return SAMPLE_GRADE.copy()


# ---------------------------------------------------------------------------
# grade_essay
# ---------------------------------------------------------------------------

@patch("src.essay_grader.core.chat")
def test_grade_essay_parses_json(mock_chat):
    """Test that grade_essay correctly parses LLM JSON response."""
    mock_chat.return_value = json.dumps(SAMPLE_GRADE)
    result = grade_essay("This is a test essay.", rubric_criteria=["clarity", "argument"])
    assert result["overall_score"] == 7.5
    assert len(result["criteria"]) == 3


@patch("src.essay_grader.core.chat")
def test_grade_essay_with_context(mock_chat):
    """Test grading with assignment context."""
    mock_chat.return_value = json.dumps(SAMPLE_GRADE)
    result = grade_essay("Test essay text.", rubric_criteria=["clarity"], context="History assignment")
    mock_chat.assert_called_once()
    call_args = mock_chat.call_args
    assert "History assignment" in call_args[1]["messages"][0]["content"]


@patch("src.essay_grader.core.chat")
def test_grade_essay_with_rubric_object(mock_chat):
    """Test grading with a full Rubric object."""
    mock_chat.return_value = json.dumps(SAMPLE_GRADE)
    rubric = Rubric("test", [RubricCriterion("thesis", 1.5, 10, "Thesis strength")])
    result = grade_essay("Test essay.", rubric=rubric)
    assert result["overall_score"] == 7.5
    prompt_text = mock_chat.call_args[1]["messages"][0]["content"]
    assert "thesis" in prompt_text
    assert "weight 1.5" in prompt_text


@patch("src.essay_grader.core.chat")
def test_grade_essay_strips_code_fences(mock_chat):
    """Test that markdown code fences are stripped before parsing."""
    mock_chat.return_value = "```json\n" + json.dumps(SAMPLE_GRADE) + "\n```"
    result = grade_essay("Test essay.", rubric_criteria=["clarity"])
    assert result["overall_score"] == 7.5


# ---------------------------------------------------------------------------
# read_essay
# ---------------------------------------------------------------------------

def test_read_essay_valid_file(tmp_path):
    """Test reading a valid essay file."""
    essay_file = tmp_path / "essay.txt"
    essay_file.write_text("This is my essay about history.")
    result = read_essay(str(essay_file))
    assert result == "This is my essay about history."


def test_read_essay_missing_file():
    """Test that reading a missing file raises FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        read_essay("nonexistent_file_xyz.txt")


# ---------------------------------------------------------------------------
# Rubric dataclass
# ---------------------------------------------------------------------------

def test_rubric_dataclass():
    """Test Rubric and RubricCriterion dataclasses."""
    criterion = RubricCriterion("thesis", 1.5, 10, "Thesis strength")
    rubric = Rubric("academic", [criterion], "Academic essay rubric")
    assert rubric.name == "academic"
    assert len(rubric.criteria) == 1
    assert rubric.criteria[0].weight == 1.5
    assert rubric.criteria[0].max_score == 10


# ---------------------------------------------------------------------------
# Preset rubrics
# ---------------------------------------------------------------------------

def test_preset_rubrics_exist():
    """Test that all expected preset rubrics exist."""
    expected = {"academic", "creative_writing", "argumentative", "narrative", "research_paper"}
    assert expected.issubset(set(PRESET_RUBRICS.keys()))
    for name, rubric in PRESET_RUBRICS.items():
        assert len(rubric.criteria) >= 3, f"{name} should have at least 3 criteria"


# ---------------------------------------------------------------------------
# calculate_grade_letter
# ---------------------------------------------------------------------------

def test_calculate_grade_letter():
    """Test grade letter calculation for various scores."""
    assert calculate_grade_letter(9.8) == "A+"
    assert calculate_grade_letter(9.0) == "A"
    assert calculate_grade_letter(8.5) == "A-"
    assert calculate_grade_letter(8.0) == "B+"
    assert calculate_grade_letter(7.5) == "B"
    assert calculate_grade_letter(7.0) == "B-"
    assert calculate_grade_letter(6.5) == "C+"
    assert calculate_grade_letter(6.0) == "C"
    assert calculate_grade_letter(5.5) == "C-"
    assert calculate_grade_letter(4.0) == "D"
    assert calculate_grade_letter(2.0) == "F"
    assert calculate_grade_letter(0.0) == "F"


# ---------------------------------------------------------------------------
# GradeDistribution
# ---------------------------------------------------------------------------

def test_grade_distribution():
    """Test GradeDistribution statistics."""
    dist = GradeDistribution()
    assert dist.count == 0
    assert dist.mean == 0.0
    assert dist.median == 0.0
    assert dist.std == 0.0

    dist.add_score(8.0)
    dist.add_score(6.0)
    dist.add_score(7.0)
    assert dist.count == 3
    assert dist.mean == 7.0
    assert dist.median == 7.0
    assert dist.std > 0

    summary = dist.summary()
    assert summary["count"] == 3
    assert summary["min"] == 6.0
    assert summary["max"] == 8.0


# ---------------------------------------------------------------------------
# validate_grade_data
# ---------------------------------------------------------------------------

def test_validate_grade_data():
    """Test validation of well-formed grade data."""
    errors = validate_grade_data(SAMPLE_GRADE)
    assert errors == []


def test_validate_grade_data_missing_score():
    """Test validation catches missing overall_score."""
    errors = validate_grade_data({"criteria": []})
    assert any("overall_score" in e for e in errors)


def test_validate_grade_data_invalid_score():
    """Test validation catches out-of-range score."""
    errors = validate_grade_data({"overall_score": 15, "criteria": []})
    assert any("between 0 and 10" in e for e in errors)


def test_validate_grade_data_bad_criteria():
    """Test validation catches non-list criteria."""
    errors = validate_grade_data({"overall_score": 7, "criteria": "not a list"})
    assert any("criteria" in e for e in errors)


# ---------------------------------------------------------------------------
# export_grade_report
# ---------------------------------------------------------------------------

def test_export_grade_report_json(tmp_path):
    """Test exporting a grade report as JSON."""
    out = tmp_path / "report.json"
    path = export_grade_report(SAMPLE_GRADE, str(out), fmt="json")
    assert path.endswith(".json")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["overall_score"] == 7.5


def test_export_grade_report_markdown(tmp_path):
    """Test exporting a grade report as Markdown."""
    out = tmp_path / "report.md"
    path = export_grade_report(SAMPLE_GRADE, str(out), fmt="markdown", essay_text="My essay.")
    assert path.endswith(".md")
    content = open(path, "r", encoding="utf-8").read()
    assert "Essay Grade Report" in content
    assert "7.5" in content


def test_export_grade_report_invalid_format(tmp_path):
    """Test that invalid format raises ValueError."""
    with pytest.raises(ValueError, match="Unsupported format"):
        export_grade_report(SAMPLE_GRADE, str(tmp_path / "report.xyz"), fmt="xml")
