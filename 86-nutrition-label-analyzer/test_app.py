"""Tests for Nutrition Label Analyzer."""

import os
import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner

from app import cli, analyze_food, analyze_label, compare_foods, read_file


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


# --- Food Analysis Tests ---

class TestAnalyzeFood:
    """Tests for single food analysis with mocked LLM."""

    @patch("app.generate")
    def test_analyze_food_returns_result(self, mock_generate):
        """analyze_food should return LLM-generated analysis."""
        mock_generate.return_value = MOCK_ANALYSIS
        result = analyze_food("Big Mac")

        assert "Big Mac" in result
        assert "CALORIES" in result
        assert "HEALTH SCORE" in result
        mock_generate.assert_called_once()

    @patch("app.generate", side_effect=Exception("LLM unavailable"))
    def test_analyze_food_llm_error(self, mock_generate):
        """analyze_food should propagate LLM errors."""
        with pytest.raises(Exception, match="LLM unavailable"):
            analyze_food("Big Mac")


# --- Label Analysis Tests ---

class TestAnalyzeLabel:
    """Tests for nutrition label analysis."""

    @patch("app.generate")
    def test_analyze_label_returns_result(self, mock_generate):
        """analyze_label should send label text to LLM and return analysis."""
        mock_generate.return_value = MOCK_LABEL_ANALYSIS
        label_text = "Calories: 200\nFat: 8g\nSodium: 800mg"

        result = analyze_label(label_text)

        assert "HEALTH SCORE" in result
        mock_generate.assert_called_once()
        call_args = mock_generate.call_args
        assert "Calories: 200" in call_args.kwargs.get("prompt", call_args[0][0] if call_args[0] else "")

    def test_read_file(self, tmp_path):
        """Reading a nutrition label file should return its content."""
        label_file = tmp_path / "nutrition.txt"
        label_file.write_text("Calories: 200\nFat: 8g", encoding="utf-8")

        content = read_file(str(label_file))
        assert "Calories: 200" in content

    def test_read_file_not_found(self):
        """Reading a non-existent file should raise FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            read_file("nonexistent_label_file.txt")


# --- Comparison Tests ---

class TestCompareFoods:
    """Tests for food comparison."""

    @patch("app.generate")
    def test_compare_two_foods(self, mock_generate):
        """compare_foods should compare multiple items and return analysis."""
        mock_generate.return_value = MOCK_COMPARISON
        result = compare_foods(["Big Mac", "Grilled Chicken Salad"])

        assert "Big Mac" in result
        assert "Grilled Chicken Salad" in result
        assert "RECOMMENDATION" in result
        mock_generate.assert_called_once()


# --- CLI Tests ---

class TestCLI:
    """Tests for the CLI interface."""

    @patch("app.check_ollama_running", return_value=True)
    @patch("app.generate", return_value=MOCK_ANALYSIS)
    def test_analyze_command(self, mock_generate, mock_ollama):
        """The analyze command should display food analysis."""
        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "--food", "Big Mac"])

        assert result.exit_code == 0
        assert mock_generate.called

    @patch("app.check_ollama_running", return_value=False)
    def test_analyze_no_ollama(self, mock_ollama):
        """Should fail gracefully when Ollama is not running."""
        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "--food", "Big Mac"])

        assert result.exit_code != 0

    @patch("app.check_ollama_running", return_value=True)
    @patch("app.generate", return_value=MOCK_LABEL_ANALYSIS)
    def test_label_command(self, mock_generate, mock_ollama, tmp_path):
        """The label command should process a nutrition label file."""
        label_file = tmp_path / "label.txt"
        label_file.write_text("Calories: 200\nFat: 8g", encoding="utf-8")

        runner = CliRunner()
        result = runner.invoke(cli, ["label", "--file", str(label_file)])

        assert result.exit_code == 0
        assert mock_generate.called

    @patch("app.check_ollama_running", return_value=True)
    @patch("app.generate", return_value=MOCK_COMPARISON)
    def test_compare_command(self, mock_generate, mock_ollama):
        """The compare command should compare multiple foods."""
        runner = CliRunner()
        result = runner.invoke(cli, ["compare", "--foods", "Big Mac,Grilled Chicken Salad"])

        assert result.exit_code == 0
        assert mock_generate.called

    @patch("app.check_ollama_running", return_value=True)
    def test_compare_single_food_error(self, mock_ollama):
        """The compare command should reject a single food item."""
        runner = CliRunner()
        result = runner.invoke(cli, ["compare", "--foods", "Big Mac"])

        assert result.exit_code != 0
