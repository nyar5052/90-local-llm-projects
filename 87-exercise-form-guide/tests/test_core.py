"""Tests for Exercise Form Guide core logic and data."""

import pytest
from unittest.mock import patch

from exercise_guide.core import (
    MUSCLE_GROUP_DATABASE,
    PROGRESSION_PATHS,
    VALID_LEVELS,
    VALID_MUSCLE_GROUPS,
    VALID_GOALS,
    get_warmup_routine,
    get_cooldown_routine,
    get_exercise_variations,
    get_muscle_info,
    generate_guide,
    generate_routine,
)


class TestMuscleDatabase:
    """Tests for the MUSCLE_GROUP_DATABASE."""

    def test_all_muscle_groups_present(self):
        """All expected muscle groups should exist in the database."""
        for group in VALID_MUSCLE_GROUPS:
            assert group in MUSCLE_GROUP_DATABASE, f"Missing muscle group: {group}"

    def test_muscle_group_has_required_keys(self):
        """Each muscle group entry should have muscles, description, and common_exercises."""
        required_keys = {"muscles", "description", "common_exercises"}
        for group, data in MUSCLE_GROUP_DATABASE.items():
            assert required_keys.issubset(data.keys()), (
                f"Muscle group '{group}' missing keys: {required_keys - data.keys()}"
            )

    def test_muscles_is_non_empty_list(self):
        """Each muscle group should have at least one muscle listed."""
        for group, data in MUSCLE_GROUP_DATABASE.items():
            assert isinstance(data["muscles"], list)
            assert len(data["muscles"]) > 0, f"'{group}' has empty muscles list"

    def test_common_exercises_is_non_empty_list(self):
        """Each muscle group should have at least one common exercise."""
        for group, data in MUSCLE_GROUP_DATABASE.items():
            assert isinstance(data["common_exercises"], list)
            assert len(data["common_exercises"]) > 0, f"'{group}' has empty exercises list"

    def test_description_is_non_empty_string(self):
        """Each muscle group should have a non-empty description."""
        for group, data in MUSCLE_GROUP_DATABASE.items():
            assert isinstance(data["description"], str)
            assert len(data["description"]) > 0, f"'{group}' has empty description"


class TestProgressionPaths:
    """Tests for the PROGRESSION_PATHS data."""

    def test_expected_exercises_present(self):
        """Expected progression exercises should exist."""
        expected = ["push-up", "squat", "pull-up", "plank", "deadlift"]
        for ex in expected:
            assert ex in PROGRESSION_PATHS, f"Missing progression: {ex}"

    def test_paths_are_lists(self):
        """Each progression path should be a list."""
        for ex, path in PROGRESSION_PATHS.items():
            assert isinstance(path, list), f"'{ex}' path is not a list"

    def test_paths_have_at_least_three_items(self):
        """Each progression path should have at least 3 steps."""
        for ex, path in PROGRESSION_PATHS.items():
            assert len(path) >= 3, f"'{ex}' has fewer than 3 steps"


class TestWarmup:
    """Tests for get_warmup_routine."""

    def test_returns_list_of_dicts(self):
        """Warm-up routine should return a list of dicts."""
        result = get_warmup_routine("chest")
        assert isinstance(result, list)
        assert len(result) > 0
        for item in result:
            assert isinstance(item, dict)

    def test_dict_has_required_keys(self):
        """Each warm-up exercise dict should have name, duration, description."""
        for group in VALID_MUSCLE_GROUPS:
            result = get_warmup_routine(group)
            for item in result:
                assert "name" in item
                assert "duration" in item
                assert "description" in item

    def test_unknown_group_returns_empty(self):
        """An unknown muscle group should return an empty list."""
        result = get_warmup_routine("nonexistent")
        assert result == []


class TestCooldown:
    """Tests for get_cooldown_routine."""

    def test_returns_list_of_dicts(self):
        """Cool-down routine should return a list of dicts."""
        result = get_cooldown_routine("legs")
        assert isinstance(result, list)
        assert len(result) > 0
        for item in result:
            assert isinstance(item, dict)

    def test_dict_has_required_keys(self):
        """Each cool-down stretch dict should have name, duration, description."""
        for group in VALID_MUSCLE_GROUPS:
            result = get_cooldown_routine(group)
            for item in result:
                assert "name" in item
                assert "duration" in item
                assert "description" in item

    def test_unknown_group_returns_empty(self):
        """An unknown muscle group should return an empty list."""
        result = get_cooldown_routine("nonexistent")
        assert result == []


class TestExerciseVariations:
    """Tests for get_exercise_variations."""

    def test_known_exercise_returns_list(self):
        """A known exercise should return its progression list."""
        result = get_exercise_variations("push-up")
        assert isinstance(result, list)
        assert len(result) >= 3

    def test_unknown_exercise_returns_empty(self):
        """An unknown exercise should return an empty list."""
        result = get_exercise_variations("triple backflip")
        assert result == []

    def test_case_insensitive(self):
        """Lookup should be case-insensitive."""
        result = get_exercise_variations("Push-Up")
        assert isinstance(result, list)
        assert len(result) >= 3


class TestMuscleInfo:
    """Tests for get_muscle_info."""

    def test_valid_group_returns_dict(self):
        """A valid muscle group should return a non-empty dict."""
        result = get_muscle_info("chest")
        assert isinstance(result, dict)
        assert "muscles" in result
        assert "description" in result
        assert "common_exercises" in result

    def test_invalid_group_returns_empty_dict(self):
        """An invalid muscle group should return an empty dict."""
        result = get_muscle_info("nonexistent_group")
        assert result == {}

    def test_case_insensitive(self):
        """Lookup should be case-insensitive."""
        result = get_muscle_info("CHEST")
        assert isinstance(result, dict)
        assert len(result) > 0


class TestGuide:
    """Tests for generate_guide (LLM-powered)."""

    @patch("exercise_guide.core.generate")
    def test_generate_guide_calls_llm(self, mock_gen):
        """generate_guide should call the LLM and return its response."""
        mock_gen.return_value = "## Deadlift Guide\nStep 1: ..."
        result = generate_guide("deadlift", "beginner")
        assert result == "## Deadlift Guide\nStep 1: ..."
        mock_gen.assert_called_once()
        call_kwargs = mock_gen.call_args
        assert "deadlift" in call_kwargs.kwargs["prompt"].lower()
        assert "beginner" in call_kwargs.kwargs["prompt"].lower()


class TestRoutine:
    """Tests for generate_routine (LLM-powered)."""

    @patch("exercise_guide.core.generate")
    def test_generate_routine_calls_llm(self, mock_gen):
        """generate_routine should call the LLM and return its response."""
        mock_gen.return_value = "## Strength Routine\nDay 1: ..."
        result = generate_routine("strength", "intermediate")
        assert result == "## Strength Routine\nDay 1: ..."
        mock_gen.assert_called_once()
        call_kwargs = mock_gen.call_args
        assert "strength" in call_kwargs.kwargs["prompt"].lower()
        assert "intermediate" in call_kwargs.kwargs["prompt"].lower()
