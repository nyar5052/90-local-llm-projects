"""Unit tests for science_explainer.core."""

import json
import pytest
from unittest.mock import patch, MagicMock

from src.science_explainer.core import (
    explain_experiment,
    parse_response,
    export_experiment,
    validate_experiment_data,
    DifficultyRating,
    Material,
    SafetyWarning,
    ProcedureStep,
    Equipment,
    ExperimentResult,
    SafetyDatabase,
    EquipmentManager,
)


SAMPLE_EXPERIMENT = {
    "experiment_name": "Baking Soda Volcano",
    "subject": "Chemistry",
    "grade_level": "middle school",
    "duration": "30 minutes",
    "objective": "Learn about acid-base reactions",
    "scientific_concepts": ["Acid-base reactions", "Chemical reactions", "Gas production"],
    "materials": [
        {"item": "Baking soda", "quantity": "2 tablespoons", "notes": "Sodium bicarbonate"},
        {"item": "Vinegar", "quantity": "1 cup", "notes": "White vinegar works best"},
        {"item": "Food coloring", "quantity": "A few drops", "notes": "Red for lava effect"},
    ],
    "safety_precautions": [
        "Wear safety goggles",
        "Perform in a well-ventilated area",
        "Adult supervision recommended",
    ],
    "procedure": [
        {"step": 1, "instruction": "Build the volcano shape with clay.", "tip": "Use a bottle inside"},
        {"step": 2, "instruction": "Add baking soda to the volcano.", "tip": ""},
        {"step": 3, "instruction": "Pour vinegar into the volcano.", "tip": "Add slowly for effect"},
    ],
    "expected_results": "Foamy eruption simulating a volcanic explosion.",
    "explanation": "Baking soda (base) reacts with vinegar (acid) producing CO2 gas.",
    "variations": ["Try different amounts of baking soda"],
    "discussion_questions": ["What gas is produced?", "Is this a physical or chemical change?"],
}


# ---------------------------------------------------------------------------
# explain_experiment
# ---------------------------------------------------------------------------


@patch("src.science_explainer.core.chat")
def test_explain_experiment_parses_json(mock_chat):
    """explain_experiment correctly parses a well-formed LLM JSON response."""
    mock_chat.return_value = json.dumps(SAMPLE_EXPERIMENT)
    result = explain_experiment("baking soda volcano", "middle school")
    assert result["experiment_name"] == "Baking Soda Volcano"
    assert len(result["materials"]) == 3
    assert len(result["procedure"]) == 3


@patch("src.science_explainer.core.chat")
def test_explain_experiment_with_detail(mock_chat):
    """Detail level is forwarded in the LLM prompt."""
    mock_chat.return_value = json.dumps(SAMPLE_EXPERIMENT)
    explain_experiment("volcano", "high school", detail="detailed")
    call_content = mock_chat.call_args[1]["messages"][0]["content"]
    assert "detailed" in call_content


# ---------------------------------------------------------------------------
# DifficultyRating enum
# ---------------------------------------------------------------------------


def test_difficulty_rating_enum():
    assert DifficultyRating.BEGINNER == 1
    assert DifficultyRating.INTERMEDIATE == 2
    assert DifficultyRating.ADVANCED == 3
    assert DifficultyRating.EXPERT == 4
    assert DifficultyRating.BEGINNER < DifficultyRating.EXPERT


# ---------------------------------------------------------------------------
# SafetyDatabase
# ---------------------------------------------------------------------------


def test_safety_database_get_safety_info():
    db = SafetyDatabase()
    info = db.get_safety_info("vinegar")
    assert info is not None
    assert info.level == "low"
    assert "safety goggles" in info.equipment_needed

    assert db.get_safety_info("unknown_material_xyz") is None


def test_safety_database_check_age_appropriate():
    db = SafetyDatabase()

    # HCl is restricted to high school+
    exp_hcl = {"materials": [{"item": "Hydrochloric acid"}]}
    assert db.check_age_appropriate(exp_hcl, "college") is True
    assert db.check_age_appropriate(exp_hcl, "high school") is True
    assert db.check_age_appropriate(exp_hcl, "middle school") is False
    assert db.check_age_appropriate(exp_hcl, "elementary") is False

    # Safe materials — always OK
    exp_safe = {"materials": [{"item": "Baking soda"}]}
    assert db.check_age_appropriate(exp_safe, "elementary") is True


def test_safety_database_get_risk_level():
    db = SafetyDatabase()
    exp = {"materials": [{"item": "Vinegar"}, {"item": "Baking soda"}]}
    assert db.get_risk_level(exp) == "low"

    exp_high = {"materials": [{"item": "Hydrochloric acid"}]}
    assert db.get_risk_level(exp_high) == "high"


def test_safety_database_get_required_ppe():
    db = SafetyDatabase()
    exp = {"materials": [{"item": "Hydrogen peroxide"}]}
    ppe = db.get_required_ppe(exp)
    assert "safety goggles" in ppe
    assert "gloves" in ppe


# ---------------------------------------------------------------------------
# EquipmentManager
# ---------------------------------------------------------------------------


def test_equipment_manager():
    mgr = EquipmentManager()
    alts = mgr.suggest_alternatives("beaker")
    assert "mason jar" in alts

    cost = mgr.estimate_cost(["beaker", "test tube"])
    assert cost == pytest.approx(7.0)

    assert mgr.suggest_alternatives("nonexistent_item_xyz") == []


# ---------------------------------------------------------------------------
# Material dataclass
# ---------------------------------------------------------------------------


def test_material_dataclass():
    m = Material(item="Beaker", quantity="1", notes="250 ml", substitute="Mason jar", cost_estimate=5.0)
    assert m.item == "Beaker"
    assert m.substitute == "Mason jar"
    assert m.cost_estimate == 5.0


# ---------------------------------------------------------------------------
# validate_experiment_data
# ---------------------------------------------------------------------------


def test_validate_experiment_data():
    errors = validate_experiment_data(SAMPLE_EXPERIMENT)
    assert errors == []

    errors_bad = validate_experiment_data({"subject": "Chemistry"})
    assert len(errors_bad) > 0
    field_names = " ".join(errors_bad)
    assert "experiment_name" in field_names


def test_validate_experiment_missing_instruction():
    data = {**SAMPLE_EXPERIMENT, "procedure": [{"step": 1}]}
    errors = validate_experiment_data(data)
    assert any("instruction" in e for e in errors)


# ---------------------------------------------------------------------------
# export_experiment
# ---------------------------------------------------------------------------


def test_export_experiment_json():
    result = export_experiment(SAMPLE_EXPERIMENT, "json")
    parsed = json.loads(result)
    assert parsed["experiment_name"] == "Baking Soda Volcano"


def test_export_experiment_markdown():
    result = export_experiment(SAMPLE_EXPERIMENT, "markdown")
    assert "# Baking Soda Volcano" in result
    assert "Safety Precautions" in result


def test_export_experiment_checklist():
    result = export_experiment(SAMPLE_EXPERIMENT, "checklist")
    assert "[ ]" in result
    assert "Baking soda" in result


def test_export_experiment_invalid_format():
    with pytest.raises(ValueError, match="Unsupported export format"):
        export_experiment(SAMPLE_EXPERIMENT, "pdf")


# ---------------------------------------------------------------------------
# parse_response
# ---------------------------------------------------------------------------


def test_parse_response_plain():
    raw = json.dumps({"key": "value"})
    assert parse_response(raw) == {"key": "value"}


def test_parse_response_code_fenced():
    raw = '```json\n{"key": "value"}\n```'
    assert parse_response(raw) == {"key": "value"}
