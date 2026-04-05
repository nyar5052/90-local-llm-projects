"""Tests for Meal Planner Bot core logic."""

import pytest
from unittest.mock import patch

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.meal_planner.core import generate_meal_plan, get_recipe_details, DIETS, SYSTEM_PROMPT
from src.meal_planner.utils import parse_calories_from_plan, total_calories


class TestDietOptions:
    def test_all_diets_defined(self):
        assert len(DIETS) >= 5

    def test_common_diets_included(self):
        assert "vegetarian" in DIETS
        assert "vegan" in DIETS
        assert "keto" in DIETS

    def test_system_prompt_is_nutritionist(self):
        assert "nutritionist" in SYSTEM_PROMPT.lower() or "meal" in SYSTEM_PROMPT.lower()


class TestGenerateMealPlan:
    @patch("src.meal_planner.core.chat")
    def test_basic_plan(self, mock_chat):
        mock_chat.return_value = "Day 1:\nBreakfast: Oatmeal\nLunch: Salad\nDinner: Pasta"
        result = generate_meal_plan("vegetarian", 7)
        assert "Day 1" in result
        mock_chat.assert_called_once()

    @patch("src.meal_planner.core.chat")
    def test_plan_with_allergies(self, mock_chat):
        mock_chat.return_value = "Nut-free meal plan..."
        generate_meal_plan("omnivore", 3, allergies="nuts,shellfish")
        messages = mock_chat.call_args[0][0]
        assert "nuts" in messages[0]["content"].lower()

    @patch("src.meal_planner.core.chat")
    def test_plan_with_calories(self, mock_chat):
        mock_chat.return_value = "1500 calorie plan..."
        generate_meal_plan("keto", 5, calories=1500)
        messages = mock_chat.call_args[0][0]
        assert "1500" in messages[0]["content"]

    @patch("src.meal_planner.core.chat")
    def test_plan_uses_system_prompt(self, mock_chat):
        mock_chat.return_value = "Plan..."
        generate_meal_plan("vegan", 1)
        assert mock_chat.call_args[1]["system_prompt"] == SYSTEM_PROMPT


class TestGetRecipeDetails:
    @patch("src.meal_planner.core.chat")
    def test_returns_recipe(self, mock_chat):
        mock_chat.return_value = "Recipe: Grilled Tofu\nIngredients: ..."
        result = get_recipe_details("Grilled Tofu", "vegan")
        assert "Grilled Tofu" in result

    @patch("src.meal_planner.core.chat")
    def test_recipe_mentions_diet(self, mock_chat):
        mock_chat.return_value = "Recipe..."
        get_recipe_details("Salad", "keto")
        messages = mock_chat.call_args[0][0]
        assert "keto" in messages[0]["content"].lower()


class TestCalorieTracking:
    def test_parse_calories(self):
        text = "Breakfast: Oatmeal (350 calories)\nLunch: Salad (400 cal)"
        entries = parse_calories_from_plan(text)
        assert len(entries) == 2
        assert total_calories(entries) == 750

    def test_no_calories_found(self):
        entries = parse_calories_from_plan("No calorie info here")
        assert len(entries) == 0
