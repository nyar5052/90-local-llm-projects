"""Unit tests for Curriculum Planner core module."""

import json
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path

from src.curriculum_planner.core import (
    generate_curriculum,
    validate_curriculum_data,
    export_curriculum,
    build_course_design,
    parse_response,
    LearningOutcome,
    WeekPlan,
    Resource,
    Prerequisite,
    Assessment,
    CourseDesign,
    OutcomeMapper,
    AssessmentPlanner,
    PrerequisiteTracker,
    ConfigManager,
)


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


# ---------------------------------------------------------------------------
# generate_curriculum
# ---------------------------------------------------------------------------


@patch("src.curriculum_planner.core.chat")
def test_generate_curriculum_parses_json(mock_chat):
    """Test that generate_curriculum correctly parses LLM JSON response."""
    mock_chat.return_value = json.dumps(SAMPLE_CURRICULUM)
    result = generate_curriculum("Intro to ML", 4, "beginner")
    assert result["course_title"] == "Intro to Machine Learning"
    assert len(result["weekly_plan"]) == 2


@patch("src.curriculum_planner.core.chat")
def test_generate_curriculum_with_focus(mock_chat):
    """Test curriculum generation with special focus areas."""
    mock_chat.return_value = json.dumps(SAMPLE_CURRICULUM)
    result = generate_curriculum("ML", 4, "beginner", focus="neural networks")
    call_content = mock_chat.call_args[1]["messages"][0]["content"]
    assert "neural networks" in call_content


@patch("src.curriculum_planner.core.chat")
def test_generate_curriculum_strips_markdown_fences(mock_chat):
    """Test that markdown code fences are stripped before parsing."""
    mock_chat.return_value = "```json\n" + json.dumps(SAMPLE_CURRICULUM) + "\n```"
    result = generate_curriculum("ML", 4, "beginner")
    assert result["course_title"] == "Intro to Machine Learning"


@patch("src.curriculum_planner.core.chat")
def test_generate_curriculum_invalid_json(mock_chat):
    """Test that ValueError is raised on invalid JSON."""
    mock_chat.return_value = "this is not json"
    with pytest.raises(ValueError, match="Could not parse"):
        generate_curriculum("ML", 4, "beginner")


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


def test_learning_outcome_dataclass():
    """Test LearningOutcome dataclass creation and defaults."""
    outcome = LearningOutcome(id="LO-1", description="Understand ML basics")
    assert outcome.id == "LO-1"
    assert outcome.bloom_level == "Understand"
    assert outcome.assessments == []

    outcome2 = LearningOutcome(
        id="LO-2",
        description="Apply regression",
        bloom_level="Apply",
        assessments=["Assignment 1"],
    )
    assert outcome2.bloom_level == "Apply"
    assert len(outcome2.assessments) == 1


def test_week_plan_dataclass():
    """Test WeekPlan dataclass."""
    wp = WeekPlan(week=1, title="Intro")
    assert wp.week == 1
    assert wp.topics == []
    assert wp.outcomes == []


def test_resource_dataclass():
    """Test Resource dataclass."""
    r = Resource(type="textbook", title="Test Book", description="A book")
    assert r.required is False
    assert r.url == ""


def test_prerequisite_dataclass():
    """Test Prerequisite dataclass."""
    p = Prerequisite(name="Python")
    assert p.required is True
    assert p.alternatives == []


# ---------------------------------------------------------------------------
# OutcomeMapper
# ---------------------------------------------------------------------------


def test_outcome_mapper_check_coverage():
    """Test that check_coverage identifies unmapped outcomes."""
    outcomes = [
        LearningOutcome(id="LO-1", description="Understand ML"),
        LearningOutcome(id="LO-2", description="Apply regression"),
        LearningOutcome(id="LO-3", description="Evaluate models"),
    ]
    weekly_plan = [
        WeekPlan(week=1, title="Intro", outcomes=["LO-1"]),
        WeekPlan(week=2, title="Regression", outcomes=["LO-2"]),
    ]
    mapper = OutcomeMapper(outcomes, weekly_plan)

    uncovered = mapper.check_coverage()
    assert len(uncovered) == 1
    assert uncovered[0].id == "LO-3"


def test_outcome_mapper_map_outcomes_to_weeks():
    """Test outcome-to-week mapping."""
    outcomes = [LearningOutcome(id="LO-1", description="Test")]
    weekly_plan = [
        WeekPlan(week=1, title="W1", outcomes=["LO-1"]),
        WeekPlan(week=3, title="W3", outcomes=["LO-1"]),
    ]
    mapper = OutcomeMapper(outcomes, weekly_plan)
    mapping = mapper.map_outcomes_to_weeks()
    assert mapping["LO-1"] == [1, 3]


def test_outcome_mapper_generate_matrix():
    """Test 2-D outcome matrix generation."""
    outcomes = [LearningOutcome(id="LO-1", description="Test")]
    weekly_plan = [
        WeekPlan(week=1, title="W1", outcomes=["LO-1"]),
        WeekPlan(week=2, title="W2", outcomes=[]),
    ]
    mapper = OutcomeMapper(outcomes, weekly_plan)
    matrix = mapper.generate_outcome_matrix()
    assert len(matrix) == 1
    assert matrix[0][0] == "LO-1"
    assert matrix[0][1] == "X"
    assert matrix[0][2] == ""


# ---------------------------------------------------------------------------
# AssessmentPlanner
# ---------------------------------------------------------------------------


def test_assessment_planner_weights():
    """Test that calculate_weights normalizes to 100."""
    assessments = [
        Assessment(name="Quiz 1", type="quiz", week=3, weight=30),
        Assessment(name="Project", type="project", week=6, weight=30),
        Assessment(name="Exam", type="exam", week=8, weight=40),
    ]
    planner = AssessmentPlanner(assessments)
    planner.calculate_weights()
    total = sum(a.weight for a in planner.assessments)
    assert total == 100.0


def test_assessment_planner_normalizes_unbalanced_weights():
    """Test weight normalization when total != 100."""
    assessments = [
        Assessment(name="A", type="quiz", week=1, weight=10),
        Assessment(name="B", type="exam", week=4, weight=10),
    ]
    planner = AssessmentPlanner(assessments)
    planner.calculate_weights()
    total = sum(a.weight for a in planner.assessments)
    assert abs(total - 100.0) < 0.01


def test_assessment_planner_plan_assessments():
    """Test automatic assessment planning."""
    outcomes = [LearningOutcome(id="LO-1", description="Test")]
    planner = AssessmentPlanner()
    planned = planner.plan_assessments(outcomes, 12)
    assert len(planned) > 0
    assert all(isinstance(a, Assessment) for a in planned)


def test_assessment_planner_calendar():
    """Test assessment calendar generation."""
    assessments = [
        Assessment(name="Exam", type="exam", week=12, weight=50),
        Assessment(name="Quiz", type="quiz", week=4, weight=50),
    ]
    planner = AssessmentPlanner(assessments)
    calendar = planner.get_assessment_calendar()
    assert calendar[0]["week"] == 4  # sorted by week
    assert calendar[1]["week"] == 12


# ---------------------------------------------------------------------------
# PrerequisiteTracker
# ---------------------------------------------------------------------------


def test_prerequisite_tracker():
    """Test prerequisite tracking and tree generation."""
    tracker = PrerequisiteTracker()
    tracker.add_prerequisite(Prerequisite(name="Python", required=True))
    tracker.add_prerequisite(Prerequisite(
        name="Statistics", required=False, alternatives=["Probability"]
    ))
    tracker.add_prerequisite(Prerequisite(name="Linear Algebra", required=True))

    required = tracker.check_prerequisites()
    assert len(required) == 2
    assert required[0].name == "Python"

    tree = tracker.generate_prerequisite_tree()
    assert len(tree["required"]) == 2
    assert len(tree["optional"]) == 1
    assert tree["optional"][0]["alternatives"] == ["Probability"]


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def test_validate_curriculum_data():
    """Test curriculum data validation."""
    issues = validate_curriculum_data(SAMPLE_CURRICULUM)
    assert issues == []


def test_validate_curriculum_data_missing_fields():
    """Test validation catches missing required fields."""
    issues = validate_curriculum_data({})
    assert any("course_title" in i for i in issues)
    assert any("weekly_plan" in i for i in issues)
    assert any("learning_objectives" in i for i in issues)


def test_validate_curriculum_data_invalid_level():
    """Test validation catches invalid level."""
    data = {**SAMPLE_CURRICULUM, "level": "expert"}
    issues = validate_curriculum_data(data)
    assert any("Invalid level" in i for i in issues)


# ---------------------------------------------------------------------------
# Export
# ---------------------------------------------------------------------------


def test_export_curriculum_json(tmp_path):
    """Test JSON export."""
    outfile = str(tmp_path / "test_curriculum.json")
    export_curriculum(SAMPLE_CURRICULUM, outfile, fmt="json")
    with open(outfile, "r", encoding="utf-8") as f:
        loaded = json.load(f)
    assert loaded["course_title"] == "Intro to Machine Learning"


def test_export_curriculum_markdown(tmp_path):
    """Test Markdown export."""
    outfile = str(tmp_path / "test_curriculum.md")
    export_curriculum(SAMPLE_CURRICULUM, outfile, fmt="markdown")
    content = Path(outfile).read_text(encoding="utf-8")
    assert "# Intro to Machine Learning" in content
    assert "## Weekly Plan" in content


# ---------------------------------------------------------------------------
# Build CourseDesign
# ---------------------------------------------------------------------------


def test_build_course_design():
    """Test converting raw dict to CourseDesign dataclass."""
    design = build_course_design(SAMPLE_CURRICULUM)
    assert design.title == "Intro to Machine Learning"
    assert design.level == "beginner"
    assert len(design.weekly_plan) == 2
    assert len(design.resources) == 2
    assert len(design.prerequisites) == 2
    assert design.prerequisites[0].name == "Basic Python"


# ---------------------------------------------------------------------------
# parse_response
# ---------------------------------------------------------------------------


def test_parse_response_plain_json():
    """Test parsing plain JSON."""
    result = parse_response(json.dumps({"key": "value"}))
    assert result == {"key": "value"}


def test_parse_response_fenced_json():
    """Test parsing JSON wrapped in markdown fences."""
    result = parse_response('```json\n{"key": "value"}\n```')
    assert result == {"key": "value"}


def test_parse_response_invalid():
    """Test that invalid JSON raises JSONDecodeError."""
    with pytest.raises(json.JSONDecodeError):
        parse_response("not json")
