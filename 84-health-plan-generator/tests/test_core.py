"""Tests for health_planner.core module."""

import datetime
from unittest.mock import patch

import pytest

from health_planner.core import (
    DISCLAIMER,
    GOAL_MILESTONES,
    WEEKLY_CHECKIN_QUESTIONS,
    ProgressTracker,
    _build_prompt,
    generate_adaptive_recommendation,
    generate_plan,
    get_milestones_for_goal,
)

# ---------------------------------------------------------------------------
# Mock plan fixture
# ---------------------------------------------------------------------------
MOCK_PLAN = """## Overview
A 1-month plan focused on improving sleep quality.

## Diet Suggestions
- Avoid caffeine after 2 PM.

## Exercise Plan
- 30 minutes of moderate activity daily.

## Sleep Recommendations
- Maintain a consistent sleep schedule.

## Stress Management
- Practice deep breathing before bed.

## Sample Weekly Schedule
| Day | Morning | Evening |
|-----|---------|---------|
| Mon | Walk    | Wind-down |

⚠️ Consult a healthcare professional before starting any new program.
"""


# ===========================================================================
# _build_prompt
# ===========================================================================
class TestBuildPrompt:
    """Tests for prompt construction."""

    def test_prompt_contains_goal(self):
        prompt = _build_prompt("better sleep", None, None, None)
        assert "better sleep" in prompt

    def test_prompt_contains_age(self):
        prompt = _build_prompt("lose weight", 30, None, None)
        assert "30" in prompt

    def test_prompt_contains_lifestyle(self):
        prompt = _build_prompt("gain muscle", None, "active", None)
        assert "active" in prompt

    def test_prompt_contains_duration_1week(self):
        prompt = _build_prompt("better sleep", None, None, "1week")
        assert "1 week" in prompt

    def test_prompt_contains_duration_1month(self):
        prompt = _build_prompt("better sleep", None, None, "1month")
        assert "1 month" in prompt

    def test_prompt_contains_duration_3months(self):
        prompt = _build_prompt("better sleep", None, None, "3months")
        assert "3 months" in prompt

    def test_prompt_all_params(self):
        prompt = _build_prompt("lose weight", 25, "sedentary", "1month")
        assert "lose weight" in prompt
        assert "25" in prompt
        assert "sedentary" in prompt
        assert "1 month" in prompt

    def test_prompt_no_optional_params(self):
        prompt = _build_prompt("general wellness", None, None, None)
        assert "general wellness" in prompt
        assert "Age" not in prompt
        assert "lifestyle" not in prompt.lower() or "activity" not in prompt.lower()


# ===========================================================================
# generate_plan
# ===========================================================================
class TestGeneratePlan:
    """Tests for the generate_plan function."""

    @patch("health_planner.core.generate")
    def test_generate_plan_returns_response(self, mock_generate):
        mock_generate.return_value = MOCK_PLAN
        result = generate_plan("better sleep")
        assert result == MOCK_PLAN
        mock_generate.assert_called_once()

    @patch("health_planner.core.generate")
    def test_generate_plan_with_all_params(self, mock_generate):
        mock_generate.return_value = MOCK_PLAN
        result = generate_plan("lose weight", age=30, lifestyle="sedentary", duration="3months")
        assert result == MOCK_PLAN
        call_kwargs = mock_generate.call_args
        prompt = call_kwargs.kwargs.get("prompt", str(call_kwargs))
        assert "lose weight" in prompt


# ===========================================================================
# ProgressTracker
# ===========================================================================
class TestProgressTracker:
    """Tests for ProgressTracker class."""

    def test_start_plan(self):
        t = ProgressTracker()
        t.start_plan("lose weight")
        assert t.goal == "lose weight"
        assert t.current_week == 1
        assert t.start_date == datetime.date.today().isoformat()
        assert t.checkins == []

    def test_add_checkin(self):
        t = ProgressTracker()
        t.start_plan("fitness")
        entry = t.add_checkin({"energy": 7, "sleep": 6})
        assert entry["week"] == 1
        assert t.current_week == 2
        assert len(t.checkins) == 1

    def test_multiple_checkins(self):
        t = ProgressTracker()
        t.start_plan("fitness")
        t.add_checkin({"energy": 7, "sleep": 6})
        t.add_checkin({"energy": 8, "sleep": 7})
        assert t.current_week == 3
        assert len(t.checkins) == 2

    def test_progress_summary_no_checkins(self):
        t = ProgressTracker()
        t.start_plan("fitness")
        summary = t.get_progress_summary()
        assert summary["weeks_completed"] == 0
        assert summary["status"] == "No check-ins recorded yet"

    def test_progress_summary_with_checkins(self):
        t = ProgressTracker()
        t.start_plan("fitness")
        t.add_checkin({"energy": 6, "sleep": 8})
        t.add_checkin({"energy": 8, "sleep": 6})
        summary = t.get_progress_summary()
        assert summary["weeks_completed"] == 2
        assert summary["avg_energy"] == 7.0
        assert summary["avg_sleep"] == 7.0
        assert summary["goal"] == "fitness"

    def test_progress_summary_missing_fields(self):
        t = ProgressTracker()
        t.start_plan("general")
        t.add_checkin({"challenge": "time"})
        summary = t.get_progress_summary()
        assert summary["avg_energy"] is None
        assert summary["avg_sleep"] is None
        assert summary["weeks_completed"] == 1

    def test_normalize_goal_weight(self):
        t = ProgressTracker()
        t.goal = "lose weight fast"
        assert t._normalize_goal() == "weight_loss"

    def test_normalize_goal_sleep(self):
        t = ProgressTracker()
        t.goal = "better sleep"
        assert t._normalize_goal() == "better_sleep"

    def test_normalize_goal_fitness(self):
        t = ProgressTracker()
        t.goal = "get fit and strong"
        assert t._normalize_goal() == "fitness"

    def test_normalize_goal_stress(self):
        t = ProgressTracker()
        t.goal = "reduce stress"
        assert t._normalize_goal() == "stress_management"

    def test_normalize_goal_general(self):
        t = ProgressTracker()
        t.goal = "be healthier"
        assert t._normalize_goal() == "general_wellness"

    def test_normalize_goal_none(self):
        t = ProgressTracker()
        t.goal = None
        assert t._normalize_goal() == "general_wellness"

    def test_get_current_milestone_week_1(self):
        t = ProgressTracker()
        t.start_plan("lose weight")
        m = t.get_current_milestone()
        assert m is not None
        assert m["week"] == 1

    def test_get_current_milestone_advances(self):
        t = ProgressTracker()
        t.start_plan("lose weight")
        t.add_checkin({"energy": 5})
        t.add_checkin({"energy": 6})
        # current_week is now 3, next milestone should be week 4
        m = t.get_current_milestone()
        assert m is not None
        assert m["week"] >= t.current_week

    def test_get_current_milestone_past_all(self):
        t = ProgressTracker()
        t.start_plan("better sleep")
        # Advance past all milestones
        for _ in range(20):
            t.add_checkin({"energy": 7})
        m = t.get_current_milestone()
        # Should return last milestone
        assert m is not None

    def test_to_dict_and_from_dict(self):
        t = ProgressTracker()
        t.start_plan("fitness")
        t.add_checkin({"energy": 7, "sleep": 8})
        data = t.to_dict()
        t2 = ProgressTracker.from_dict(data)
        assert t2.goal == "fitness"
        assert t2.current_week == 2
        assert len(t2.checkins) == 1

    def test_from_dict_empty(self):
        t = ProgressTracker.from_dict({})
        assert t.goal is None
        assert t.current_week == 1
        assert t.checkins == []


# ===========================================================================
# get_milestones_for_goal
# ===========================================================================
class TestGetMilestonesForGoal:
    """Tests for get_milestones_for_goal."""

    def test_weight_loss_milestones(self):
        milestones = get_milestones_for_goal("lose weight")
        assert len(milestones) > 0
        assert milestones[0]["week"] == 1

    def test_sleep_milestones(self):
        milestones = get_milestones_for_goal("better sleep")
        assert len(milestones) > 0

    def test_fitness_milestones(self):
        milestones = get_milestones_for_goal("get fit")
        assert len(milestones) > 0

    def test_stress_milestones(self):
        milestones = get_milestones_for_goal("manage stress")
        assert len(milestones) > 0

    def test_unknown_goal_returns_general(self):
        milestones = get_milestones_for_goal("something random")
        assert milestones == GOAL_MILESTONES["general_wellness"]


# ===========================================================================
# generate_adaptive_recommendation
# ===========================================================================
class TestGenerateAdaptiveRecommendation:
    """Tests for generate_adaptive_recommendation."""

    def test_low_energy_recommendation(self):
        t = ProgressTracker()
        t.start_plan("fitness")
        t.add_checkin({"energy": 3, "sleep": 7})
        rec = generate_adaptive_recommendation(t)
        assert "energy" in rec.lower()

    def test_low_sleep_recommendation(self):
        t = ProgressTracker()
        t.start_plan("general wellness")
        t.add_checkin({"energy": 7, "sleep": 3})
        rec = generate_adaptive_recommendation(t)
        assert "sleep" in rec.lower()

    def test_weeks_completed_message(self):
        t = ProgressTracker()
        t.start_plan("fitness")
        t.add_checkin({"energy": 8, "sleep": 8})
        rec = generate_adaptive_recommendation(t)
        assert "1 week" in rec

    def test_milestone_in_recommendation(self):
        t = ProgressTracker()
        t.start_plan("lose weight")
        rec = generate_adaptive_recommendation(t)
        assert "milestone" in rec.lower() or "Week" in rec

    def test_no_checkins_still_works(self):
        t = ProgressTracker()
        t.start_plan("fitness")
        rec = generate_adaptive_recommendation(t)
        assert len(rec) > 0

    def test_no_goal_fallback(self):
        t = ProgressTracker()
        rec = generate_adaptive_recommendation(t)
        assert len(rec) > 0


# ===========================================================================
# Data integrity
# ===========================================================================
class TestDataIntegrity:
    """Verify constants and data structures."""

    def test_disclaimer_not_empty(self):
        assert len(DISCLAIMER) > 50

    def test_disclaimer_contains_warning(self):
        assert "NOT" in DISCLAIMER
        assert "medical" in DISCLAIMER.lower()

    def test_checkin_questions_count(self):
        assert len(WEEKLY_CHECKIN_QUESTIONS) == 9

    def test_all_milestone_categories_have_entries(self):
        for key, milestones in GOAL_MILESTONES.items():
            assert len(milestones) > 0, f"{key} has no milestones"
            for m in milestones:
                assert "week" in m
                assert "milestone" in m
                assert "tip" in m
