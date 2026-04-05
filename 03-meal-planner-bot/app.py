"""
Meal Planner Bot - Generate personalized weekly meal plans with recipes.

Takes dietary preferences, allergies, and number of days to generate
complete meal plans with detailed recipes using Gemma 4 via Ollama.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import click
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from rich.progress import Progress, SpinnerColumn, TextColumn
from common.llm_client import chat, check_ollama_running

console = Console()

SYSTEM_PROMPT = """You are an expert nutritionist and meal planning assistant. Your role is to:
1. Create balanced, nutritious meal plans tailored to dietary preferences
2. Account for allergies and dietary restrictions
3. Provide complete recipes with ingredients and step-by-step instructions
4. Include estimated prep/cook times and calorie counts
5. Suggest ingredient substitutions when appropriate

Format your meal plans clearly with:
- Day headers
- Breakfast, Lunch, Dinner, and optional Snacks
- Brief recipe descriptions with key ingredients"""

DIETS = [
    "omnivore", "vegetarian", "vegan", "keto", "paleo",
    "mediterranean", "gluten-free", "dairy-free", "pescatarian", "low-carb",
]


def generate_meal_plan(
    diet: str,
    days: int,
    allergies: str | None = None,
    calories: int | None = None,
) -> str:
    """Generate a meal plan based on preferences."""
    prompt_parts = [
        f"Create a {days}-day meal plan for a {diet} diet.",
        "Include Breakfast, Lunch, Dinner, and one Snack for each day.",
    ]
    if allergies:
        prompt_parts.append(f"IMPORTANT: Avoid these allergens/ingredients: {allergies}")
    if calories:
        prompt_parts.append(f"Target approximately {calories} calories per day.")
    prompt_parts.append(
        "For each meal, provide: name, key ingredients, and estimated calories."
    )

    messages = [{"role": "user", "content": " ".join(prompt_parts)}]
    return chat(messages, system_prompt=SYSTEM_PROMPT, max_tokens=4096)


def get_recipe_details(meal_name: str, diet: str) -> str:
    """Get a detailed recipe for a specific meal."""
    messages = [
        {
            "role": "user",
            "content": (
                f"Give me a detailed recipe for: {meal_name}\n"
                f"Diet: {diet}\n"
                "Include: ingredients list, step-by-step instructions, prep time, "
                "cook time, servings, and nutritional info."
            ),
        }
    ]
    return chat(messages, system_prompt=SYSTEM_PROMPT, max_tokens=2048)


@click.command()
@click.option("--diet", type=click.Choice(DIETS, case_sensitive=False), default="omnivore", help="Dietary preference")
@click.option("--days", type=click.IntRange(1, 14), default=7, help="Number of days (1-14)")
@click.option("--allergies", type=str, default=None, help="Comma-separated list of allergies")
@click.option("--calories", type=int, default=None, help="Target daily calories")
def main(diet: str, days: int, allergies: str | None, calories: int | None):
    """Meal Planner Bot - Generate personalized meal plans with recipes."""
    console.print(
        Panel.fit(
            "[bold cyan]🍽️ Meal Planner Bot[/bold cyan]\n"
            "Personalized meal plans powered by AI",
            border_style="cyan",
        )
    )

    if not check_ollama_running():
        console.print("[red]❌ Ollama is not running. Start it with: ollama serve[/red]")
        sys.exit(1)

    console.print(f"[bold]Diet:[/bold] {diet.capitalize()}")
    console.print(f"[bold]Days:[/bold] {days}")
    if allergies:
        console.print(f"[bold]Allergies:[/bold] {allergies}")
    if calories:
        console.print(f"[bold]Target Calories:[/bold] {calories}/day")
    console.print()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        progress.add_task(f"Generating {days}-day {diet} meal plan...", total=None)
        meal_plan = generate_meal_plan(diet, days, allergies, calories)

    console.print(
        Panel(Markdown(meal_plan), title="[bold green]📋 Your Meal Plan[/bold green]", border_style="green")
    )

    # Interactive recipe detail loop
    console.print("\n[dim]Want a detailed recipe? Type a meal name, or 'quit' to exit.[/dim]\n")

    while True:
        try:
            meal = Prompt.ask("[bold yellow]🍳 Get recipe for[/bold yellow]")
        except (KeyboardInterrupt, EOFError):
            break

        if meal.lower().strip() in ("quit", "exit", "q"):
            break

        if not meal.strip():
            continue

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            progress.add_task("Getting recipe details...", total=None)
            recipe = get_recipe_details(meal, diet)

        console.print()
        console.print(
            Panel(Markdown(recipe), title=f"[bold green]📖 Recipe: {meal}[/bold green]", border_style="green")
        )
        console.print()

    console.print("[bold cyan]🍽️ Enjoy your meals! Goodbye![/bold cyan]")


if __name__ == "__main__":
    main()
