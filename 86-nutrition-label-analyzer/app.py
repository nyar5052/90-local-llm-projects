"""
Nutrition Label Analyzer - Analyzes food nutrition and provides health insights.

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

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from common.llm_client import generate, check_ollama_running

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

console = Console()

DISCLAIMER = (
    "[bold red]⚠ DISCLAIMER:[/bold red] This tool is for [bold]EDUCATIONAL purposes ONLY[/bold]. "
    "Nutrition data and health insights are [bold]AI-generated estimates[/bold] and may be "
    "inaccurate. This is [bold]NOT[/bold] medical or dietary advice. Always consult a qualified "
    "healthcare professional or registered dietitian before making dietary changes."
)

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


def display_disclaimer() -> None:
    """Display the nutrition/medical disclaimer."""
    console.print()
    console.print(Panel(DISCLAIMER, title="⚕ Important Notice", border_style="red"))
    console.print()


def analyze_food(food: str) -> str:
    """Analyze nutrition for a single food item.

    Args:
        food: Name of the food item to analyze.

    Returns:
        LLM-generated nutritional analysis.
    """
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
    prompt = f"Compare the nutrition of these foods: {food_list}"

    return generate(
        prompt=prompt,
        system_prompt=COMPARE_SYSTEM_PROMPT,
        temperature=0.3,
        max_tokens=3072,
    )


def display_analysis(title: str, result: str, border_style: str = "green") -> None:
    """Display analysis results with rich formatting.

    Args:
        title: Panel title.
        result: Analysis text to display.
        border_style: Rich border color.
    """
    display_disclaimer()
    console.print(Panel(result, title=title, border_style=border_style, padding=(1, 2)))
    console.print()
    console.print(
        "[dim italic]Note: All values are AI-generated estimates. "
        "Consult a healthcare professional for dietary advice.[/dim italic]"
    )
    console.print()


def read_file(file_path: str) -> str:
    """Read text content from a file."""
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


# --- CLI ---

@click.group()
def cli():
    """Nutrition Label Analyzer - AI-powered nutrition insights.

    ⚠ EDUCATIONAL USE ONLY. Not medical or dietary advice.
    """
    pass


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
@click.option(
    "--foods", required=True,
    help="Comma-separated list of food items to compare."
)
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


if __name__ == "__main__":
    cli()
