"""Tests for stress_manager.core module."""

from unittest.mock import patch

import pytest

from stress_manager.core import (
    BREATHING_EXERCISES,
    CBT_WORKSHEETS,
    COPING_TOOLKIT,
    STRESS_QUESTIONS,
    calculate_stress_score,
    get_cbt_worksheet,
    get_coping_suggestions,
    run_breathing_exercise,
)


# ---------------------------------------------------------------------------
# Breathing exercises
# ---------------------------------------------------------------------------

class TestBreathingExercises:
    """Tests for breathing exercise definitions and execution."""

    def test_box_breathing_defined(self):
        assert "box" in BREATHING_EXERCISES

    def test_478_breathing_defined(self):
        assert "478" in BREATHING_EXERCISES

    @pytest.mark.parametrize("key", ["box", "478"])
    def test_exercise_has_required_keys(self, key):
        ex = BREATHING_EXERCISES[key]
        assert "name" in ex
        assert "description" in ex
        assert "steps" in ex
        assert "cycles" in ex
        assert len(ex["steps"]) > 0
        assert ex["cycles"] > 0

    @patch("stress_manager.core.time.sleep")
    def test_box_breathing_runs(self, mock_sleep):
        run_breathing_exercise("box")
        assert mock_sleep.call_count > 0

    @patch("stress_manager.core.time.sleep")
    def test_478_breathing_runs(self, mock_sleep):
        run_breathing_exercise("478")
        assert mock_sleep.call_count > 0


# ---------------------------------------------------------------------------
# Stress score
# ---------------------------------------------------------------------------

class TestStressScore:
    """Tests for calculate_stress_score."""

    def test_low_score(self):
        answers = {
            "stress_level": 2,
            "sleep_quality": 1,
            "energy_level": 3,
            "anxiety_level": 2,
            "concentration": 1,
        }
        result = calculate_stress_score(answers)
        assert result["severity"] == "low"
        assert result["total_score"] == 9
        assert len(result["recommendations"]) > 0
        assert "breakdown" in result

    def test_moderate_score(self):
        answers = {
            "stress_level": 5,
            "sleep_quality": 4,
            "energy_level": 6,
            "anxiety_level": 5,
            "concentration": 5,
        }
        result = calculate_stress_score(answers)
        assert result["severity"] == "moderate"
        assert result["total_score"] == 25

    def test_high_score(self):
        answers = {
            "stress_level": 8,
            "sleep_quality": 7,
            "energy_level": 8,
            "anxiety_level": 7,
            "concentration": 8,
        }
        result = calculate_stress_score(answers)
        assert result["severity"] == "high"
        assert result["total_score"] == 38

    def test_critical_score(self):
        answers = {
            "stress_level": 10,
            "sleep_quality": 9,
            "energy_level": 10,
            "anxiety_level": 10,
            "concentration": 9,
        }
        result = calculate_stress_score(answers)
        assert result["severity"] == "critical"
        assert result["total_score"] == 48
        assert any("988" in r for r in result["recommendations"])

    def test_breakdown_categories(self):
        answers = {
            "stress_level": 5,
            "sleep_quality": 5,
            "energy_level": 5,
            "anxiety_level": 5,
            "concentration": 5,
        }
        result = calculate_stress_score(answers)
        for cat in answers:
            assert cat in result["breakdown"]
            assert "score" in result["breakdown"][cat]
            assert "severity" in result["breakdown"][cat]


# ---------------------------------------------------------------------------
# CBT Worksheets
# ---------------------------------------------------------------------------

class TestCBTWorksheets:
    """Tests for CBT worksheet templates."""

    def test_thought_record_exists(self):
        assert "thought_record" in CBT_WORKSHEETS

    def test_behavioral_activation_exists(self):
        assert "behavioral_activation" in CBT_WORKSHEETS

    def test_worry_time_exists(self):
        assert "worry_time" in CBT_WORKSHEETS

    @pytest.mark.parametrize("ws_type", ["thought_record", "behavioral_activation", "worry_time"])
    def test_worksheet_has_required_keys(self, ws_type):
        ws = CBT_WORKSHEETS[ws_type]
        assert "name" in ws
        assert "description" in ws

    def test_thought_record_columns(self):
        ws = CBT_WORKSHEETS["thought_record"]
        assert "columns" in ws
        assert len(ws["columns"]) == 6

    def test_behavioral_activation_columns(self):
        ws = CBT_WORKSHEETS["behavioral_activation"]
        assert "columns" in ws
        assert len(ws["columns"]) == 4

    def test_worry_time_steps(self):
        ws = CBT_WORKSHEETS["worry_time"]
        assert "steps" in ws
        assert len(ws["steps"]) > 0

    def test_get_cbt_worksheet_valid(self):
        ws = get_cbt_worksheet("thought_record")
        assert ws["name"] == "Thought Record"

    def test_get_cbt_worksheet_invalid(self):
        ws = get_cbt_worksheet("nonexistent")
        assert ws == {}


# ---------------------------------------------------------------------------
# Coping Toolkit
# ---------------------------------------------------------------------------

class TestCopingToolkit:
    """Tests for coping toolkit and suggestions."""

    def test_physical_category(self):
        assert "physical" in COPING_TOOLKIT
        assert len(COPING_TOOLKIT["physical"]) > 0

    def test_cognitive_category(self):
        assert "cognitive" in COPING_TOOLKIT
        assert len(COPING_TOOLKIT["cognitive"]) > 0

    def test_social_category(self):
        assert "social" in COPING_TOOLKIT
        assert len(COPING_TOOLKIT["social"]) > 0

    def test_creative_category(self):
        assert "creative" in COPING_TOOLKIT
        assert len(COPING_TOOLKIT["creative"]) > 0

    def test_get_coping_suggestions_low(self):
        suggestions = get_coping_suggestions("low")
        assert isinstance(suggestions, list)
        assert len(suggestions) > 0

    def test_get_coping_suggestions_moderate(self):
        suggestions = get_coping_suggestions("moderate")
        assert isinstance(suggestions, list)
        assert len(suggestions) > 0

    def test_get_coping_suggestions_high(self):
        suggestions = get_coping_suggestions("high")
        assert isinstance(suggestions, list)
        assert len(suggestions) > 0

    def test_get_coping_suggestions_critical(self):
        suggestions = get_coping_suggestions("critical")
        assert isinstance(suggestions, list)
        assert len(suggestions) > 0


# ---------------------------------------------------------------------------
# Stress Questions
# ---------------------------------------------------------------------------

class TestStressQuestions:
    """Tests for STRESS_QUESTIONS definitions."""

    def test_five_questions_defined(self):
        assert len(STRESS_QUESTIONS) == 5

    def test_questions_are_tuples(self):
        for q in STRESS_QUESTIONS:
            assert isinstance(q, tuple)
            assert len(q) == 3

    def test_question_ranges(self):
        for question, low, high in STRESS_QUESTIONS:
            assert isinstance(question, str)
            assert low == 1
            assert high == 10
