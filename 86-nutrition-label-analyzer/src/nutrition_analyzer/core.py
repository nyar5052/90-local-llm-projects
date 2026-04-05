"""
Nutrition Label Analyzer - Core logic for AI-powered nutrition insights.

╔══════════════════════════════════════════════════════════════════════╗
║  DISCLAIMER: This tool is for EDUCATIONAL purposes only. The       ║
║  nutrition information and health insights provided are             ║
║  AI-generated ESTIMATES and may be inaccurate. This is NOT         ║
║  medical or dietary advice. Always consult a qualified healthcare   ║
║  professional or registered dietitian for personalized nutrition    ║
║  guidance. Do NOT use this for medical decisions.                   ║
╚══════════════════════════════════════════════════════════════════════╝
"""

import sys
import os
import logging
from dataclasses import dataclass, field
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from common.llm_client import generate, check_ollama_running

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Medical / Dietary Disclaimer
# ---------------------------------------------------------------------------

DISCLAIMER = (
    "[bold red]⚠ DISCLAIMER:[/bold red] This tool is for [bold]EDUCATIONAL purposes ONLY[/bold]. "
    "Nutrition data and health insights are [bold]AI-generated estimates[/bold] and may be "
    "inaccurate. This is [bold]NOT[/bold] medical or dietary advice. Always consult a qualified "
    "healthcare professional or registered dietitian before making dietary changes."
)

# ---------------------------------------------------------------------------
# FDA Daily Reference Values
# ---------------------------------------------------------------------------

DV_REFERENCE: dict[str, dict[str, float]] = {
    "calories":   {"value": 2000,  "unit": "kcal"},
    "total_fat":  {"value": 78,    "unit": "g"},
    "sat_fat":    {"value": 20,    "unit": "g"},
    "cholesterol":{"value": 300,   "unit": "mg"},
    "sodium":     {"value": 2300,  "unit": "mg"},
    "carbs":      {"value": 275,   "unit": "g"},
    "fiber":      {"value": 28,    "unit": "g"},
    "sugar":      {"value": 50,    "unit": "g"},
    "protein":    {"value": 50,    "unit": "g"},
    "vitamin_d":  {"value": 20,    "unit": "mcg"},
    "calcium":    {"value": 1300,  "unit": "mg"},
    "iron":       {"value": 18,    "unit": "mg"},
    "potassium":  {"value": 4700,  "unit": "mg"},
}

# ---------------------------------------------------------------------------
# Common Allergens (FDA Big 9)
# ---------------------------------------------------------------------------

COMMON_ALLERGENS: list[str] = [
    "milk", "eggs", "fish", "shellfish", "tree nuts",
    "peanuts", "wheat", "soybeans", "sesame",
]

# ---------------------------------------------------------------------------
# System Prompts
# ---------------------------------------------------------------------------

ANALYZE_SYSTEM_PROMPT = """You are a nutrition analysis expert. When given a food item, provide a
detailed nutritional analysis in the following EXACT format:

FOOD: [food name]
SERVING SIZE: [estimated standard serving]

CALORIES: [estimated calories]

MACRONUTRIENTS:
- Protein: [grams]g
- Total Fat: [grams]g
  - Saturated Fat: [grams]g
  - Trans Fat: [grams]g
- Total Carbohydrates: [grams]g
  - Dietary Fiber: [grams]g
  - Sugars: [grams]g

VITAMINS & MINERALS:
- [List key vitamins and minerals with estimated % Daily Value]

HEALTH SCORE: [1-10]/10
SCORE EXPLANATION: [Brief explanation of the score]

HEALTH PROS:
- [List positive health aspects]

HEALTH CONS:
- [List negative health aspects]

HEALTHIER ALTERNATIVES:
- [Suggest 2-3 healthier alternatives]

IMPORTANT: These are AI-generated estimates for educational purposes only. Actual nutrition
values may vary. This is NOT medical or dietary advice.
"""

LABEL_SYSTEM_PROMPT = """You are a nutrition label analysis expert. Given nutrition label data,
provide a health assessment in the following format:

PRODUCT ASSESSMENT:

CALORIE ANALYSIS: [assessment of calorie content]

MACRONUTRIENT BREAKDOWN:
- Protein: [assessment]
- Fats: [assessment including saturated/trans fat concerns]
- Carbohydrates: [assessment including fiber and sugar analysis]

HEALTH SCORE: [1-10]/10
SCORE EXPLANATION: [Brief explanation]

KEY CONCERNS:
- [List any nutritional concerns - high sodium, added sugars, etc.]

POSITIVE ASPECTS:
- [List nutritional strengths]

RECOMMENDATIONS:
- [Practical dietary recommendations]

HEALTHIER ALTERNATIVES:
- [Suggest 2-3 healthier alternatives if applicable]

IMPORTANT: This is an AI-generated assessment for educational purposes only. This is NOT
medical or dietary advice. Consult a registered dietitian for personalized guidance.
"""

COMPARE_SYSTEM_PROMPT = """You are a nutrition comparison expert. Given multiple food items,
provide a side-by-side nutritional comparison in the following format:

COMPARISON: [Food 1] vs [Food 2] [vs Food 3...]

For each food item, provide:
FOOD: [name]
- Calories: [estimate]
- Protein: [g]
- Total Fat: [g]
- Carbohydrates: [g]
- Fiber: [g]
- Sugar: [g]
- Health Score: [1-10]/10

COMPARISON SUMMARY:
- Best for protein: [food name]
- Lowest calorie: [food name]
- Most nutritious overall: [food name]
- Best health score: [food name]

DETAILED ANALYSIS:
[Paragraph comparing the nutritional profiles, highlighting significant differences]

RECOMMENDATION: [Which food is the healthiest choice and why]

IMPORTANT: These are AI-generated estimates for educational purposes only. Actual nutrition
values may vary. This is NOT medical or dietary advice.
"""

# ---------------------------------------------------------------------------
# Dietary Goals
# ---------------------------------------------------------------------------

@dataclass
class DietaryGoal:
    """Represents a dietary macro-nutrient goal."""
    name: str
    daily_calories: int
    protein_pct: float
    carb_pct: float
    fat_pct: float


PRESET_GOALS: dict[str, DietaryGoal] = {
    "balanced": DietaryGoal(
        name="Balanced",
        daily_calories=2000,
        protein_pct=0.30,
        carb_pct=0.40,
        fat_pct=0.30,
    ),
    "low_carb": DietaryGoal(
        name="Low Carb",
        daily_calories=1800,
        protein_pct=0.35,
        carb_pct=0.20,
        fat_pct=0.45,
    ),
    "high_protein": DietaryGoal(
        name="High Protein",
        daily_calories=2200,
        protein_pct=0.40,
        carb_pct=0.35,
        fat_pct=0.25,
    ),
    "keto": DietaryGoal(
        name="Keto",
        daily_calories=1800,
        protein_pct=0.25,
        carb_pct=0.05,
        fat_pct=0.70,
    ),
    "weight_loss": DietaryGoal(
        name="Weight Loss",
        daily_calories=1500,
        protein_pct=0.35,
        carb_pct=0.35,
        fat_pct=0.30,
    ),
}

# ---------------------------------------------------------------------------
# Meal Tracker
# ---------------------------------------------------------------------------

class MealTracker:
    """Tracks meals and nutrient totals for a day."""

    def __init__(self) -> None:
        self._meals: list[dict] = []

    def add_meal(self, name: str, nutrients: dict) -> None:
        """Add a meal with its nutrient values.

        Args:
            name: Description of the meal.
            nutrients: Dict mapping nutrient names to numeric values
                       (e.g. {"calories": 550, "protein": 25}).
        """
        logger.info("Adding meal: %s", name)
        self._meals.append({"name": name, "nutrients": nutrients})

    def get_daily_totals(self) -> dict:
        """Return summed nutrient totals across all tracked meals."""
        totals: dict[str, float] = {}
        for meal in self._meals:
            for nutrient, value in meal["nutrients"].items():
                totals[nutrient] = totals.get(nutrient, 0) + value
        return totals

    def get_remaining_budget(self, goal: Optional[DietaryGoal] = None) -> dict:
        """Return remaining nutrient budget based on a goal.

        Args:
            goal: A DietaryGoal to compare against. Defaults to 'balanced'.

        Returns:
            Dict with remaining calories and macro gram budgets.
        """
        if goal is None:
            goal = PRESET_GOALS["balanced"]
        totals = self.get_daily_totals()
        cal = goal.daily_calories
        remaining = {
            "calories": cal - totals.get("calories", 0),
            "protein_g": round(cal * goal.protein_pct / 4 - totals.get("protein", 0), 1),
            "carbs_g": round(cal * goal.carb_pct / 4 - totals.get("carbs", 0), 1),
            "fat_g": round(cal * goal.fat_pct / 9 - totals.get("fat", 0), 1),
        }
        return remaining

    def reset(self) -> None:
        """Clear all tracked meals."""
        logger.info("Resetting meal tracker")
        self._meals.clear()

    @property
    def meals(self) -> list[dict]:
        return list(self._meals)

# ---------------------------------------------------------------------------
# Core Analysis Functions
# ---------------------------------------------------------------------------

def analyze_food(food: str) -> str:
    """Analyze nutrition for a single food item.

    Args:
        food: Name of the food item to analyze.

    Returns:
        LLM-generated nutritional analysis.
    """
    logger.info("Analyzing food: %s", food)
    prompt = f"Analyze the nutrition of: {food}"

    return generate(
        prompt=prompt,
        system_prompt=ANALYZE_SYSTEM_PROMPT,
        temperature=0.3,
        max_tokens=2048,
    )


def analyze_label(label_text: str) -> str:
    """Analyze nutrition label data from text.

    Args:
        label_text: Raw nutrition label text data.

    Returns:
        LLM-generated label assessment.
    """
    logger.info("Analyzing nutrition label (%d chars)", len(label_text))
    prompt = f"Analyze this nutrition label:\n\n{label_text}"

    return generate(
        prompt=prompt,
        system_prompt=LABEL_SYSTEM_PROMPT,
        temperature=0.3,
        max_tokens=2048,
    )


def compare_foods(foods: list[str]) -> str:
    """Compare nutrition across multiple food items.

    Args:
        foods: List of food item names to compare.

    Returns:
        LLM-generated nutritional comparison.
    """
    food_list = ", ".join(foods)
    logger.info("Comparing foods: %s", food_list)
    prompt = f"Compare the nutrition of these foods: {food_list}"

    return generate(
        prompt=prompt,
        system_prompt=COMPARE_SYSTEM_PROMPT,
        temperature=0.3,
        max_tokens=3072,
    )


def read_file(file_path: str) -> str:
    """Read text content from a file."""
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


# ---------------------------------------------------------------------------
# Daily Value Calculations
# ---------------------------------------------------------------------------

def calculate_daily_values(nutrients: dict) -> dict:
    """Calculate percent Daily Value for each nutrient.

    Args:
        nutrients: Dict mapping nutrient names to numeric amounts.
                   Keys should match DV_REFERENCE keys (e.g. "calories",
                   "total_fat", "sodium", etc.).

    Returns:
        Dict mapping nutrient names to their %DV (float).
    """
    result: dict[str, float] = {}
    for nutrient, amount in nutrients.items():
        ref = DV_REFERENCE.get(nutrient)
        if ref and ref["value"] > 0:
            pct = round((amount / ref["value"]) * 100, 1)
            result[nutrient] = pct
        else:
            logger.debug("No DV reference for nutrient: %s", nutrient)
    return result


# ---------------------------------------------------------------------------
# Allergen Checking
# ---------------------------------------------------------------------------

def check_allergens(food: str, allergen_list: Optional[list[str]] = None) -> list[str]:
    """Check a food description for potential allergens.

    Performs a simple case-insensitive substring match of each allergen
    against the food string. This is a heuristic helper – users should
    always verify allergen information from official sources.

    Args:
        food: Food name or description to scan.
        allergen_list: List of allergens to check. Defaults to COMMON_ALLERGENS.

    Returns:
        List of matching allergen strings found in the food description.
    """
    if allergen_list is None:
        allergen_list = COMMON_ALLERGENS
    food_lower = food.lower()
    found = []
    for a in allergen_list:
        a_lower = a.lower()
        if a_lower in food_lower:
            found.append(a)
        elif a_lower.endswith("s") and a_lower[:-1] in food_lower:
            found.append(a)
        elif f"{a_lower}s" in food_lower:
            found.append(a)
    logger.info("Allergen check for '%s': found %s", food, found)
    return found
