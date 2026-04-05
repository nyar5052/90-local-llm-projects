"""Helper utilities for Meal Planner Bot."""

import json
import logging
import re
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


# ── Shopping List ─────────────────────────────────────────────────────────────

def generate_shopping_list_prompt(meal_plan: str) -> str:
    """Build a prompt to extract a shopping list from a meal plan."""
    return (
        "Based on the following meal plan, create a consolidated shopping list "
        "grouped by category (Produce, Proteins, Dairy, Grains, Pantry, Other). "
        "Combine duplicate ingredients and include approximate quantities.\n\n"
        f"Meal Plan:\n{meal_plan}\n\n"
        "Return the shopping list in Markdown format."
    )


def save_shopping_list(items: str, output_file: str = "shopping_list.json") -> str:
    """Save the shopping list text to a JSON file."""
    data = {"generated_at": datetime.now().isoformat(), "content": items}
    Path(output_file).write_text(json.dumps(data, indent=2), encoding="utf-8")
    logger.info("Shopping list saved to %s", output_file)
    return output_file


# ── Calorie Tracking ─────────────────────────────────────────────────────────

def parse_calories_from_plan(plan_text: str) -> list[dict]:
    """Attempt to extract calorie info from plan text using simple regex."""
    entries: list[dict] = []
    pattern = re.compile(r"(\d{2,4})\s*(?:cal|kcal|calories)", re.IGNORECASE)
    for line in plan_text.split("\n"):
        match = pattern.search(line)
        if match:
            entries.append({"line": line.strip(), "calories": int(match.group(1))})
    return entries


def total_calories(entries: list[dict]) -> int:
    return sum(e.get("calories", 0) for e in entries)


# ── Recipe Saving ─────────────────────────────────────────────────────────────

def load_saved_recipes(filepath: str = "saved_recipes.json") -> list[dict]:
    p = Path(filepath)
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return []


def save_recipe(name: str, content: str, diet: str, filepath: str = "saved_recipes.json") -> dict:
    recipes = load_saved_recipes(filepath)
    recipe = {
        "name": name,
        "diet": diet,
        "content": content,
        "saved_at": datetime.now().isoformat(),
    }
    recipes.append(recipe)
    Path(filepath).write_text(json.dumps(recipes, indent=2), encoding="utf-8")
    logger.info("Saved recipe: %s", name)
    return recipe
