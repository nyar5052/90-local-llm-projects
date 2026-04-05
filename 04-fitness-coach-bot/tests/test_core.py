"""Tests for Fitness Coach Bot core logic."""

import pytest
from unittest.mock import patch

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.fitness_coach.core import generate_workout_plan, get_exercise_details, LEVELS, GOALS, SYSTEM_PROMPT
from src.fitness_coach.utils import search_exercises, EXERCISE_LIBRARY


class TestConfiguration:
    def test_levels_defined(self):
        assert "beginner" in LEVELS
        assert "intermediate" in LEVELS
        assert "advanced" in LEVELS

    def test_goals_defined(self):
        assert len(GOALS) >= 4
        assert "weight-loss" in GOALS
        assert "muscle-gain" in GOALS

    def test_system_prompt_safety(self):
        assert "doctor" in SYSTEM_PROMPT.lower() or "safety" in SYSTEM_PROMPT.lower()


class TestGenerateWorkoutPlan:
    @patch("src.fitness_coach.core.chat")
    def test_basic_plan(self, mock_chat):
        mock_chat.return_value = "Day 1: Upper Body\n- Push-ups 3x10\n- Pull-ups 3x5"
        result = generate_workout_plan("beginner", "weight-loss", "dumbbells")
        assert "Day 1" in result
        mock_chat.assert_called_once()

    @patch("src.fitness_coach.core.chat")
    def test_plan_includes_level(self, mock_chat):
        mock_chat.return_value = "Plan..."
        generate_workout_plan("advanced", "strength", "barbell,rack")
        messages = mock_chat.call_args[0][0]
        assert "advanced" in messages[0]["content"].lower()

    @patch("src.fitness_coach.core.chat")
    def test_plan_includes_equipment(self, mock_chat):
        mock_chat.return_value = "Plan..."
        generate_workout_plan("beginner", "general-fitness", "resistance bands,mat")
        messages = mock_chat.call_args[0][0]
        assert "resistance bands" in messages[0]["content"].lower()

    @patch("src.fitness_coach.core.chat")
    def test_custom_days_and_duration(self, mock_chat):
        mock_chat.return_value = "Plan..."
        generate_workout_plan("intermediate", "endurance", "bodyweight", days_per_week=3, session_minutes=30)
        messages = mock_chat.call_args[0][0]
        assert "3-day" in messages[0]["content"]
        assert "30 minutes" in messages[0]["content"]


class TestGetExerciseDetails:
    @patch("src.fitness_coach.core.chat")
    def test_returns_details(self, mock_chat):
        mock_chat.return_value = "Push-ups: Start in plank position..."
        result = get_exercise_details("Push-ups", "beginner")
        assert "Push-ups" in result

    @patch("src.fitness_coach.core.chat")
    def test_includes_level_context(self, mock_chat):
        mock_chat.return_value = "Details..."
        get_exercise_details("Deadlift", "advanced")
        messages = mock_chat.call_args[0][0]
        assert "advanced" in messages[0]["content"].lower()


class TestExerciseLibrary:
    def test_search_by_name(self):
        results = search_exercises("push")
        assert len(results) >= 1

    def test_search_by_muscle(self):
        results = search_exercises("chest")
        assert len(results) >= 1

    def test_filter_by_difficulty(self):
        results = search_exercises("", "beginner")
        assert all(e["difficulty"] == "beginner" for e in results)

    def test_library_not_empty(self):
        assert len(EXERCISE_LIBRARY) >= 5
