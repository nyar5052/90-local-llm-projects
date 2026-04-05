"""Click CLI interface for Meal Planner Bot."""

import sys
import logging

import click
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from rich.progress import Progress, SpinnerColumn, TextColumn

from .config import load_config, setup_logging
from .core import (
    check_ollama_running,
    generate_meal_plan,
    get_recipe_details,
    generate_shopping_list,
    DIETS,
)
from .utils import save_recipe, save_shopping_list, parse_calories_from_plan, total_calories

logger = logging.getLogger(__name__)
console = Console()


@click.command()
@click.option("--diet", type=click.Choice(DIETS, case_sensitive=False), default="omnivore", help="Dietary preference")
@click.option("--days", type=click.IntRange(1, 14), default=7, help="Number of days (1-14)")
@click.option("--allergies", type=str, default=None, help="Comma-separated list of allergies")
@click.option("--calories", type=int, default=None, help="Target daily calories")
@click.option("--config", "config_path", default=None, type=click.Path(), help="Path to config.yaml")
def main(diet: str, days: int, allergies: str | None, calories: int | None, config_path: str | None):
    """Meal Planner Bot - Generate personalized meal plans with recipes."""
    cfg = load_config(config_path)
    setup_logging(cfg)
    model_cfg = cfg.get("model", {})
    storage_cfg = cfg.get("storage", {})

    console.print(Panel.fit("[bold cyan]🍽️ Meal Planner Bot[/bold cyan]\nPersonalized meal plans powered by AI", border_style="cyan"))

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

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as prog:
        prog.add_task(f"Generating {days}-day {diet} meal plan...", total=None)
        meal_plan = generate_meal_plan(diet, days, allergies, calories, model=model_cfg.get("name", "gemma4"), temperature=model_cfg.get("temperature", 0.7))

    console.print(Panel(Markdown(meal_plan), title="[bold green]📋 Your Meal Plan[/bold green]", border_style="green"))

    # Calorie summary
    cal_entries = parse_calories_from_plan(meal_plan)
    if cal_entries:
        console.print(f"\n[bold]🔥 Total estimated calories found: {total_calories(cal_entries)}[/bold]")

    console.print("\n[dim]Commands: meal name → recipe | 'shop' → shopping list | 'save <name>' → save recipe | 'quit'[/dim]\n")

    while True:
        try:
            cmd = Prompt.ask("[bold yellow]🍳 Command[/bold yellow]")
        except (KeyboardInterrupt, EOFError):
            break

        stripped = cmd.lower().strip()
        if stripped in ("quit", "exit", "q"):
            break
        if stripped == "shop":
            with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as prog:
                prog.add_task("Generating shopping list...", total=None)
                shopping = generate_shopping_list(meal_plan, model=model_cfg.get("name", "gemma4"))
            console.print(Panel(Markdown(shopping), title="[bold green]🛒 Shopping List[/bold green]", border_style="green"))
            save_shopping_list(shopping, storage_cfg.get("shopping_list_file", "shopping_list.json"))
            continue
        if not cmd.strip():
            continue

        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as prog:
            prog.add_task("Getting recipe details...", total=None)
            recipe = get_recipe_details(cmd, diet, model=model_cfg.get("name", "gemma4"))

        console.print()
        console.print(Panel(Markdown(recipe), title=f"[bold green]📖 Recipe: {cmd}[/bold green]", border_style="green"))
        save_recipe(cmd, recipe, diet, storage_cfg.get("recipes_file", "saved_recipes.json"))
        console.print()

    console.print("[bold cyan]🍽️ Enjoy your meals! Goodbye![/bold cyan]")


if __name__ == "__main__":
    main()
