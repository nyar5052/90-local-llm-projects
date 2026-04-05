"""Tests for nutrition_analyzer core module."""

import os
import pytest
from unittest.mock import patch, MagicMock

from src.nutrition_analyzer.core import (
    analyze_food,
    analyze_label,
    compare_foods,
    read_file,
    calculate_daily_values,
    check_allergens,
    MealTracker,
    PRESET_GOALS,
    DV_REFERENCE,
    COMMON_ALLERGENS,
    DietaryGoal,
)


MOCK_ANALYSIS = """FOOD: Big Mac
SERVING SIZE: 1 sandwich (200g)

CALORIES: 550

MACRONUTRIENTS:
- Protein: 25g
- Total Fat: 30g
  - Saturated Fat: 11g
  - Trans Fat: 1g
- Total Carbohydrates: 45g
  - Dietary Fiber: 3g
  - Sugars: 9g

HEALTH SCORE: 3/10
"""

MOCK_COMPARISON = """COMPARISON: Big Mac vs Grilled Chicken Salad

FOOD: Big Mac
- Calories: 550
- Protein: 25g
- Health Score: 3/10

FOOD: Grilled Chicken Salad
- Calories: 250
- Protein: 30g
- Health Score: 8/10

RECOMMENDATION: The Grilled Chicken Salad is the healthier choice.
"""

MOCK_LABEL_ANALYSIS = """PRODUCT ASSESSMENT:

CALORIE ANALYSIS: 200 calories per serving is moderate.

HEALTH SCORE: 6/10
SCORE EXPLANATION: Reasonable calorie count but high sodium.
"""


# ---------------------------------------------------------------------------
# Food Analysis Tests
# ---------------------------------------------------------------------------

class TestAnalyzeFood:
    """Tests for single food analysis with mocked LLM."""

    @patch("src.nutrition_analyzer.core.generate")
    def test_analyze_food_returns_result(self, mock_generate):
        mock_generate.return_value = MOCK_ANALYSIS
        result = analyze_food("Big Mac")

        assert "Big Mac" in result
        assert "CALORIES" in result
        assert "HEALTH SCORE" in result
        mock_generate.assert_called_once()

    @patch("src.nutrition_analyzer.core.generate", side_effect=Exception("LLM unavailable"))
    def test_analyze_food_llm_error(self, mock_generate):
        with pytest.raises(Exception, match="LLM unavailable"):
            analyze_food("Big Mac")


# ---------------------------------------------------------------------------
# Label Analysis Tests
# ---------------------------------------------------------------------------

class TestAnalyzeLabel:
    """Tests for nutrition label analysis."""

    @patch("src.nutrition_analyzer.core.generate")
    def test_analyze_label_returns_result(self, mock_generate):
        mock_generate.return_value = MOCK_LABEL_ANALYSIS
        label_text = "Calories: 200\nFat: 8g\nSodium: 800mg"
        result = analyze_label(label_text)

        assert "HEALTH SCORE" in result
        mock_generate.assert_called_once()
        call_args = mock_generate.call_args
        prompt_val = call_args.kwargs.get("prompt", call_args[0][0] if call_args[0] else "")
        assert "Calories: 200" in prompt_val

    def test_read_file(self, tmp_path):
        label_file = tmp_path / "nutrition.txt"
        label_file.write_text("Calories: 200\nFat: 8g", encoding="utf-8")

        content = read_file(str(label_file))
        assert "Calories: 200" in content

    def test_read_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            read_file("nonexistent_label_file.txt")


# ---------------------------------------------------------------------------
# Comparison Tests
# ---------------------------------------------------------------------------

class TestCompareFoods:
    """Tests for food comparison."""

    @patch("src.nutrition_analyzer.core.generate")
    def test_compare_two_foods(self, mock_generate):
        mock_generate.return_value = MOCK_COMPARISON
        result = compare_foods(["Big Mac", "Grilled Chicken Salad"])

        assert "Big Mac" in result
        assert "Grilled Chicken Salad" in result
        assert "RECOMMENDATION" in result
        mock_generate.assert_called_once()


# ---------------------------------------------------------------------------
# Daily Value Calculation Tests
# ---------------------------------------------------------------------------

class TestDailyValues:
    """Tests for calculate_daily_values."""

    def test_known_inputs(self):
        nutrients = {"calories": 500, "total_fat": 39, "sodium": 1150}
        result = calculate_daily_values(nutrients)

        assert result["calories"] == 25.0  # 500/2000 * 100
        assert result["total_fat"] == 50.0  # 39/78 * 100
        assert result["sodium"] == 50.0  # 1150/2300 * 100

    def test_empty_input(self):
        result = calculate_daily_values({})
        assert result == {}

    def test_unknown_nutrient_ignored(self):
        result = calculate_daily_values({"unknown_vitamin": 100})
        assert result == {}

    def test_all_reference_nutrients(self):
        nutrients = {k: v["value"] for k, v in DV_REFERENCE.items()}
        result = calculate_daily_values(nutrients)
        for key in nutrients:
            assert result[key] == 100.0


# ---------------------------------------------------------------------------
# Meal Tracker Tests
# ---------------------------------------------------------------------------

class TestMealTracker:
    """Tests for MealTracker class."""

    def test_add_meal(self):
        tracker = MealTracker()
        tracker.add_meal("Lunch", {"calories": 600, "protein": 30})
        assert len(tracker.meals) == 1
        assert tracker.meals[0]["name"] == "Lunch"

    def test_get_daily_totals(self):
        tracker = MealTracker()
        tracker.add_meal("Breakfast", {"calories": 400, "protein": 20})
        tracker.add_meal("Lunch", {"calories": 600, "protein": 30})
        totals = tracker.get_daily_totals()
        assert totals["calories"] == 1000
        assert totals["protein"] == 50

    def test_get_daily_totals_empty(self):
        tracker = MealTracker()
        assert tracker.get_daily_totals() == {}

    def test_get_remaining_budget(self):
        tracker = MealTracker()
        tracker.add_meal("Lunch", {"calories": 500, "protein": 25, "carbs": 50, "fat": 20})
        remaining = tracker.get_remaining_budget()
        assert remaining["calories"] == 1500  # 2000 - 500
        assert remaining["protein_g"] > 0
        assert remaining["carbs_g"] > 0
        assert remaining["fat_g"] > 0

    def test_get_remaining_budget_custom_goal(self):
        tracker = MealTracker()
        tracker.add_meal("Snack", {"calories": 200, "protein": 10})
        goal = PRESET_GOALS["keto"]
        remaining = tracker.get_remaining_budget(goal)
        assert remaining["calories"] == 1600  # 1800 - 200

    def test_reset(self):
        tracker = MealTracker()
        tracker.add_meal("Lunch", {"calories": 600})
        tracker.reset()
        assert len(tracker.meals) == 0
        assert tracker.get_daily_totals() == {}


# ---------------------------------------------------------------------------
# Allergen Tests
# ---------------------------------------------------------------------------

class TestAllergens:
    """Tests for check_allergens."""

    def test_detects_allergen(self):
        found = check_allergens("peanut butter sandwich")
        assert "peanuts" in found

    def test_detects_multiple_allergens(self):
        found = check_allergens("peanut butter on wheat bread with milk")
        assert "peanuts" in found
        assert "wheat" in found
        assert "milk" in found

    def test_no_allergens(self):
        found = check_allergens("grilled chicken breast")
        assert found == []

    def test_custom_allergen_list(self):
        found = check_allergens("cheese pizza", ["dairy", "gluten"])
        assert found == []  # "dairy" and "gluten" not in "cheese pizza"

    def test_case_insensitive(self):
        found = check_allergens("PEANUT BUTTER")
        assert "peanuts" in found


# ---------------------------------------------------------------------------
# Dietary Goals Tests
# ---------------------------------------------------------------------------

class TestDietaryGoals:
    """Tests for dietary goal presets."""

    def test_presets_exist(self):
        assert "balanced" in PRESET_GOALS
        assert "low_carb" in PRESET_GOALS
        assert "high_protein" in PRESET_GOALS
        assert "keto" in PRESET_GOALS
        assert "weight_loss" in PRESET_GOALS

    def test_preset_structure(self):
        for key, goal in PRESET_GOALS.items():
            assert isinstance(goal, DietaryGoal)
            assert goal.daily_calories > 0
            assert 0 < goal.protein_pct <= 1
            assert 0 < goal.carb_pct <= 1
            assert 0 < goal.fat_pct <= 1

    def test_macros_sum_to_100(self):
        for key, goal in PRESET_GOALS.items():
            total = goal.protein_pct + goal.carb_pct + goal.fat_pct
            assert abs(total - 1.0) < 0.01, f"{key} macros sum to {total}, expected ~1.0"
