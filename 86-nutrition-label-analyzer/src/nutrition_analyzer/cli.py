"""
Nutrition Label Analyzer - CLI interface.

Provides click-based commands for food analysis, label reading,
food comparison, daily value lookups, meal tracking, allergen
checking, and dietary goal management.

⚠ EDUCATIONAL USE ONLY. Not medical or dietary advice.
"""

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .core import (
    DISCLAIMER,
    DV_REFERENCE,
    COMMON_ALLERGENS,
    PRESET_GOALS,
    MealTracker,
    analyze_food,
    analyze_label,
    compare_foods,
    read_file,
    calculate_daily_values,
    check_allergens,
    check_ollama_running,
)

console = Console()

# Module-level tracker so that the ``track`` command can accumulate meals
# within a single CLI session (or be reset).
_tracker = MealTracker()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def display_disclaimer() -> None:
    """Display the nutrition/medical disclaimer."""
    console.print()
    console.print(Panel(DISCLAIMER, title="⚕ Important Notice", border_style="red"))
    console.print()


def display_analysis(title: str, result: str, border_style: str = "green") -> None:
    """Display analysis results with rich formatting."""
    display_disclaimer()
    console.print(Panel(result, title=title, border_style=border_style, padding=(1, 2)))
    console.print()
    console.print(
        "[dim italic]Note: All values are AI-generated estimates. "
        "Consult a healthcare professional for dietary advice.[/dim italic]"
    )
    console.print()


# ---------------------------------------------------------------------------
# CLI Group
# ---------------------------------------------------------------------------

@click.group()
def cli():
    """Nutrition Label Analyzer - AI-powered nutrition insights.

    ⚠ EDUCATIONAL USE ONLY. Not medical or dietary advice.
    """
    pass


# ---------------------------------------------------------------------------
# Existing Commands
# ---------------------------------------------------------------------------

@cli.command()
@click.option("--food", required=True, help="Name of the food item to analyze.")
def analyze(food: str):
    """Analyze the nutrition of a food item."""
    if not check_ollama_running():
        console.print("[red]Error: Ollama is not running. Please start it first.[/red]")
        raise SystemExit(1)

    console.print(f"\n[cyan]🍽 Analyzing nutrition for:[/cyan] [bold]{food}[/bold]")

    with console.status("[cyan]Analyzing nutrition data...[/cyan]"):
        try:
            result = analyze_food(food)
        except Exception as e:
            console.print(f"[red]Error during analysis: {e}[/red]")
            raise SystemExit(1)

    display_analysis(f"🍽 Nutrition Analysis: {food}", result)


@cli.command()
@click.option("--file", "file_path", required=True, help="Path to nutrition label text file.")
def label(file_path: str):
    """Analyze a nutrition label from a text file."""
    if not check_ollama_running():
        console.print("[red]Error: Ollama is not running. Please start it first.[/red]")
        raise SystemExit(1)

    try:
        label_text = read_file(file_path)
    except FileNotFoundError as e:
        console.print(f"[red]Error: {e}[/red]")
        raise SystemExit(1)
    except Exception as e:
        console.print(f"[red]Error reading file: {e}[/red]")
        raise SystemExit(1)

    console.print(f"\n[cyan]📋 Analyzing nutrition label from:[/cyan] [bold]{file_path}[/bold]")

    with console.status("[cyan]Analyzing nutrition label...[/cyan]"):
        try:
            result = analyze_label(label_text)
        except Exception as e:
            console.print(f"[red]Error during analysis: {e}[/red]")
            raise SystemExit(1)

    display_analysis("📋 Nutrition Label Analysis", result, border_style="blue")


@cli.command()
@click.option("--foods", required=True, help="Comma-separated list of food items to compare.")
def compare(foods: str):
    """Compare nutrition across multiple food items."""
    if not check_ollama_running():
        console.print("[red]Error: Ollama is not running. Please start it first.[/red]")
        raise SystemExit(1)

    food_list = [f.strip() for f in foods.split(",") if f.strip()]

    if len(food_list) < 2:
        console.print("[red]Error: Please provide at least 2 food items to compare.[/red]")
        raise SystemExit(1)

    food_display = " vs ".join(food_list)
    console.print(f"\n[cyan]⚖ Comparing:[/cyan] [bold]{food_display}[/bold]")

    with console.status("[cyan]Comparing nutrition data...[/cyan]"):
        try:
            result = compare_foods(food_list)
        except Exception as e:
            console.print(f"[red]Error during comparison: {e}[/red]")
            raise SystemExit(1)

    display_analysis(f"⚖ Nutrition Comparison: {food_display}", result, border_style="magenta")


# ---------------------------------------------------------------------------
# New Commands
# ---------------------------------------------------------------------------

@cli.command("daily-values")
@click.option("--food", required=True, help="Nutrient values as key=value pairs, e.g. 'calories=550,total_fat=30,sodium=1000'.")
def daily_values(food: str):
    """Calculate %Daily Values for given nutrient amounts."""
    display_disclaimer()

    nutrients: dict[str, float] = {}
    for pair in food.split(","):
        pair = pair.strip()
        if "=" not in pair:
            continue
        key, val = pair.split("=", 1)
        try:
            nutrients[key.strip()] = float(val.strip())
        except ValueError:
            console.print(f"[yellow]Warning: skipping non-numeric value for '{key.strip()}'[/yellow]")

    if not nutrients:
        console.print("[red]Error: No valid nutrient key=value pairs provided.[/red]")
        raise SystemExit(1)

    dv = calculate_daily_values(nutrients)

    table = Table(title="📊 % Daily Values", border_style="cyan")
    table.add_column("Nutrient", style="bold")
    table.add_column("Amount", justify="right")
    table.add_column("% DV", justify="right")

    for nutrient, amount in nutrients.items():
        ref = DV_REFERENCE.get(nutrient)
        unit = ref["unit"] if ref else ""
        pct_str = f"{dv[nutrient]}%" if nutrient in dv else "N/A"
        table.add_row(nutrient, f"{amount} {unit}", pct_str)

    console.print(table)
    console.print()


@cli.command("track")
@click.option("--meal", default=None, help="Meal description with nutrients, e.g. 'Lunch: calories=600,protein=30,carbs=50,fat=25'.")
@click.option("--reset", is_flag=True, help="Reset the daily meal tracker.")
@click.option("--summary", is_flag=True, help="Show daily totals and remaining budget.")
def track(meal: str | None, reset: bool, summary: bool):
    """Track daily meals and nutrient intake."""
    display_disclaimer()

    if reset:
        _tracker.reset()
        console.print("[green]✔ Meal tracker has been reset.[/green]")
        return

    if meal:
        parts = meal.split(":", 1)
        meal_name = parts[0].strip() if len(parts) > 1 else "Meal"
        nutrient_str = parts[1].strip() if len(parts) > 1 else parts[0].strip()
        nutrients: dict[str, float] = {}
        for pair in nutrient_str.split(","):
            pair = pair.strip()
            if "=" not in pair:
                continue
            key, val = pair.split("=", 1)
            try:
                nutrients[key.strip()] = float(val.strip())
            except ValueError:
                pass
        if nutrients:
            _tracker.add_meal(meal_name, nutrients)
            console.print(f"[green]✔ Added meal: {meal_name}[/green]")
        else:
            console.print("[red]Error: No valid nutrient data in meal string.[/red]")
            raise SystemExit(1)

    if summary or meal:
        totals = _tracker.get_daily_totals()
        remaining = _tracker.get_remaining_budget()

        table = Table(title="📊 Daily Nutrition Summary", border_style="cyan")
        table.add_column("Metric", style="bold")
        table.add_column("Total", justify="right")
        table.add_column("Remaining", justify="right")

        for key in ["calories", "protein", "carbs", "fat"]:
            total_val = totals.get(key, 0)
            rem_key = key if key == "calories" else f"{key}_g"
            rem_val = remaining.get(rem_key, "N/A")
            table.add_row(key.capitalize(), str(round(total_val, 1)), str(rem_val))

        console.print(table)
        console.print()


@cli.command("allergen-check")
@click.option("--food", required=True, help="Food name or description to scan for allergens.")
@click.option("--allergens", default=None, help="Comma-separated allergen list (default: FDA Big 9).")
def allergen_check(food: str, allergens: str | None):
    """Check a food for common allergens."""
    display_disclaimer()

    allergen_list = None
    if allergens:
        allergen_list = [a.strip() for a in allergens.split(",") if a.strip()]

    found = check_allergens(food, allergen_list)

    if found:
        console.print(f"[bold red]⚠ Potential allergens detected in '{food}':[/bold red]")
        for a in found:
            console.print(f"  [red]• {a}[/red]")
    else:
        console.print(f"[green]✔ No common allergens detected in '{food}'.[/green]")
    console.print()


@cli.command("goals")
@click.option("--preset", default=None, help="Show a preset dietary goal (balanced, low_carb, high_protein, keto, weight_loss).")
@click.option("--show", is_flag=True, help="List all available preset goals.")
def goals(preset: str | None, show: bool):
    """View dietary goal presets and macro breakdowns."""
    display_disclaimer()

    if show or preset is None:
        table = Table(title="🎯 Dietary Goal Presets", border_style="cyan")
        table.add_column("Key", style="bold")
        table.add_column("Name")
        table.add_column("Calories", justify="right")
        table.add_column("Protein %", justify="right")
        table.add_column("Carb %", justify="right")
        table.add_column("Fat %", justify="right")

        for key, goal in PRESET_GOALS.items():
            table.add_row(
                key,
                goal.name,
                str(goal.daily_calories),
                f"{int(goal.protein_pct * 100)}%",
                f"{int(goal.carb_pct * 100)}%",
                f"{int(goal.fat_pct * 100)}%",
            )
        console.print(table)
        console.print()
        return

    goal = PRESET_GOALS.get(preset)
    if not goal:
        console.print(f"[red]Error: Unknown preset '{preset}'. Use --show to list presets.[/red]")
        raise SystemExit(1)

    cal = goal.daily_calories
    protein_g = round(cal * goal.protein_pct / 4, 1)
    carb_g = round(cal * goal.carb_pct / 4, 1)
    fat_g = round(cal * goal.fat_pct / 9, 1)

    table = Table(title=f"🎯 {goal.name} Goal", border_style="cyan")
    table.add_column("Macro", style="bold")
    table.add_column("% of Calories", justify="right")
    table.add_column("Daily Grams", justify="right")

    table.add_row("Protein", f"{int(goal.protein_pct * 100)}%", f"{protein_g}g")
    table.add_row("Carbohydrates", f"{int(goal.carb_pct * 100)}%", f"{carb_g}g")
    table.add_row("Fat", f"{int(goal.fat_pct * 100)}%", f"{fat_g}g")

    console.print(f"\n[bold]Daily Calories:[/bold] {cal} kcal\n")
    console.print(table)
    console.print()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    """Entry point for the nutrition-analyzer console script."""
    cli()


if __name__ == "__main__":
    main()
