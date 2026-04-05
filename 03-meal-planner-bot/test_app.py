"""Tests for Meal Planner Bot."""

import pytest
from unittest.mock import patch
from click.testing import CliRunner

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app import generate_meal_plan, get_recipe_details, main, DIETS, SYSTEM_PROMPT


class TestDietOptions:
    """Tests for diet configuration."""

    def test_all_diets_defined(self):
        assert len(DIETS) >= 5

    def test_common_diets_included(self):
        assert "vegetarian" in DIETS
        assert "vegan" in DIETS
        assert "keto" in DIETS

    def test_system_prompt_is_nutritionist(self):
        assert "nutritionist" in SYSTEM_PROMPT.lower() or "meal" in SYSTEM_PROMPT.lower()


class TestGenerateMealPlan:
    """Tests for meal plan generation."""

    @patch("app.chat")
    def test_basic_plan(self, mock_chat):
        mock_chat.return_value = "Day 1:\nBreakfast: Oatmeal\nLunch: Salad\nDinner: Pasta"
        result = generate_meal_plan("vegetarian", 7)
        assert "Day 1" in result
        mock_chat.assert_called_once()

    @patch("app.chat")
    def test_plan_with_allergies(self, mock_chat):
        mock_chat.return_value = "Nut-free meal plan..."
        generate_meal_plan("omnivore", 3, allergies="nuts,shellfish")
        call_args = mock_chat.call_args
        messages = call_args[0][0]
        assert "nuts" in messages[0]["content"].lower()

    @patch("app.chat")
    def test_plan_with_calories(self, mock_chat):
        mock_chat.return_value = "1500 calorie plan..."
        generate_meal_plan("keto", 5, calories=1500)
        call_args = mock_chat.call_args
        messages = call_args[0][0]
        assert "1500" in messages[0]["content"]

    @patch("app.chat")
    def test_plan_uses_system_prompt(self, mock_chat):
        mock_chat.return_value = "Plan..."
        generate_meal_plan("vegan", 1)
        assert mock_chat.call_args[1]["system_prompt"] == SYSTEM_PROMPT


class TestGetRecipeDetails:
    """Tests for recipe detail retrieval."""

    @patch("app.chat")
    def test_returns_recipe(self, mock_chat):
        mock_chat.return_value = "Recipe: Grilled Tofu\nIngredients: ..."
        result = get_recipe_details("Grilled Tofu", "vegan")
        assert "Grilled Tofu" in result

    @patch("app.chat")
    def test_recipe_mentions_diet(self, mock_chat):
        mock_chat.return_value = "Recipe..."
        get_recipe_details("Salad", "keto")
        call_args = mock_chat.call_args
        messages = call_args[0][0]
        assert "keto" in messages[0]["content"].lower()


class TestCLI:
    """Tests for the CLI interface."""

    @patch("app.check_ollama_running", return_value=False)
    def test_exits_when_ollama_down(self, mock_check):
        runner = CliRunner()
        result = runner.invoke(main, ["--diet", "vegan", "--days", "3"])
        assert result.exit_code != 0
