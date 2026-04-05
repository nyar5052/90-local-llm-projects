"""Tests for nutrition_analyzer CLI module."""

import pytest
from unittest.mock import patch
from click.testing import CliRunner

from src.nutrition_analyzer.cli import cli, _tracker


MOCK_ANALYSIS = """FOOD: Big Mac
SERVING SIZE: 1 sandwich (200g)
CALORIES: 550
HEALTH SCORE: 3/10
"""

MOCK_COMPARISON = """COMPARISON: Big Mac vs Grilled Chicken Salad
RECOMMENDATION: The Grilled Chicken Salad is the healthier choice.
"""

MOCK_LABEL_ANALYSIS = """PRODUCT ASSESSMENT:
CALORIE ANALYSIS: 200 calories per serving is moderate.
HEALTH SCORE: 6/10
"""


# ---------------------------------------------------------------------------
# Existing Command Tests
# ---------------------------------------------------------------------------

class TestAnalyzeCommand:
    """Tests for the analyze CLI command."""

    @patch("src.nutrition_analyzer.cli.check_ollama_running", return_value=True)
    @patch("src.nutrition_analyzer.core.generate", return_value=MOCK_ANALYSIS)
    def test_analyze_command(self, mock_generate, mock_ollama):
        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "--food", "Big Mac"])
        assert result.exit_code == 0
        assert mock_generate.called

    @patch("src.nutrition_analyzer.cli.check_ollama_running", return_value=False)
    def test_analyze_no_ollama(self, mock_ollama):
        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "--food", "Big Mac"])
        assert result.exit_code != 0


class TestLabelCommand:
    """Tests for the label CLI command."""

    @patch("src.nutrition_analyzer.cli.check_ollama_running", return_value=True)
    @patch("src.nutrition_analyzer.core.generate", return_value=MOCK_LABEL_ANALYSIS)
    def test_label_command(self, mock_generate, mock_ollama, tmp_path):
        label_file = tmp_path / "label.txt"
        label_file.write_text("Calories: 200\nFat: 8g", encoding="utf-8")

        runner = CliRunner()
        result = runner.invoke(cli, ["label", "--file", str(label_file)])
        assert result.exit_code == 0
        assert mock_generate.called

    @patch("src.nutrition_analyzer.cli.check_ollama_running", return_value=True)
    def test_label_missing_file(self, mock_ollama):
        runner = CliRunner()
        result = runner.invoke(cli, ["label", "--file", "nonexistent.txt"])
        assert result.exit_code != 0


class TestCompareCommand:
    """Tests for the compare CLI command."""

    @patch("src.nutrition_analyzer.cli.check_ollama_running", return_value=True)
    @patch("src.nutrition_analyzer.core.generate", return_value=MOCK_COMPARISON)
    def test_compare_command(self, mock_generate, mock_ollama):
        runner = CliRunner()
        result = runner.invoke(cli, ["compare", "--foods", "Big Mac,Grilled Chicken Salad"])
        assert result.exit_code == 0
        assert mock_generate.called

    @patch("src.nutrition_analyzer.cli.check_ollama_running", return_value=True)
    def test_compare_single_food_error(self, mock_ollama):
        runner = CliRunner()
        result = runner.invoke(cli, ["compare", "--foods", "Big Mac"])
        assert result.exit_code != 0

    @patch("src.nutrition_analyzer.cli.check_ollama_running", return_value=False)
    def test_compare_no_ollama(self, mock_ollama):
        runner = CliRunner()
        result = runner.invoke(cli, ["compare", "--foods", "Big Mac,Salad"])
        assert result.exit_code != 0


# ---------------------------------------------------------------------------
# New Command Tests
# ---------------------------------------------------------------------------

class TestDailyValuesCommand:
    """Tests for the daily-values CLI command."""

    def test_daily_values_valid(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["daily-values", "--food", "calories=500,total_fat=39"])
        assert result.exit_code == 0
        assert "Daily Values" in result.output

    def test_daily_values_empty_input(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["daily-values", "--food", "no_equals_here"])
        assert result.exit_code != 0


class TestTrackCommand:
    """Tests for the track CLI command."""

    def setup_method(self):
        _tracker.reset()

    def test_track_add_meal(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["track", "--meal", "Lunch: calories=600,protein=30,carbs=50,fat=20"])
        assert result.exit_code == 0
        assert "Added meal" in result.output

    def test_track_reset(self):
        _tracker.add_meal("Test", {"calories": 100})
        runner = CliRunner()
        result = runner.invoke(cli, ["track", "--reset"])
        assert result.exit_code == 0
        assert "reset" in result.output.lower()

    def test_track_summary(self):
        _tracker.add_meal("Breakfast", {"calories": 400, "protein": 20})
        runner = CliRunner()
        result = runner.invoke(cli, ["track", "--summary"])
        assert result.exit_code == 0
        assert "Daily Nutrition Summary" in result.output


class TestAllergenCheckCommand:
    """Tests for the allergen-check CLI command."""

    def test_allergen_found(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["allergen-check", "--food", "peanut butter sandwich"])
        assert result.exit_code == 0
        assert "peanuts" in result.output.lower()

    def test_no_allergens(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["allergen-check", "--food", "grilled chicken"])
        assert result.exit_code == 0
        assert "No common allergens" in result.output

    def test_custom_allergens(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["allergen-check", "--food", "milk chocolate", "--allergens", "milk,soy"])
        assert result.exit_code == 0
        assert "milk" in result.output.lower()


class TestGoalsCommand:
    """Tests for the goals CLI command."""

    def test_goals_show_all(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["goals", "--show"])
        assert result.exit_code == 0
        assert "balanced" in result.output.lower()

    def test_goals_preset(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["goals", "--preset", "keto"])
        assert result.exit_code == 0
        assert "Keto" in result.output

    def test_goals_unknown_preset(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["goals", "--preset", "nonexistent"])
        assert result.exit_code != 0

    def test_goals_default_shows_all(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["goals"])
        assert result.exit_code == 0
        assert "Dietary Goal Presets" in result.output


# ---------------------------------------------------------------------------
# Missing Argument Tests
# ---------------------------------------------------------------------------

class TestMissingArgs:
    """Tests for missing required arguments."""

    def test_analyze_missing_food(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["analyze"])
        assert result.exit_code != 0

    def test_label_missing_file(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["label"])
        assert result.exit_code != 0

    def test_compare_missing_foods(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["compare"])
        assert result.exit_code != 0

    def test_daily_values_missing_food(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["daily-values"])
        assert result.exit_code != 0

    def test_allergen_check_missing_food(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["allergen-check"])
        assert result.exit_code != 0
