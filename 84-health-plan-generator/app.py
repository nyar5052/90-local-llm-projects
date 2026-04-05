"""
Health Plan Generator - Generates personalized wellness plans based on goals.

Creates structured plans covering diet, exercise, sleep, and stress management
using a local LLM via Ollama.

⚠️  DISCLAIMER: This tool is for INFORMATIONAL and EDUCATIONAL PURPOSES ONLY.
It does NOT provide medical advice, diagnosis, or treatment. Always consult a
qualified healthcare professional before starting any new health, diet, or
exercise program.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from common.llm_client import generate, check_ollama_running

import click
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt, IntPrompt

console = Console()

DISCLAIMER = (
    "⚠️  DISCLAIMER: This tool is for INFORMATIONAL and EDUCATIONAL PURPOSES ONLY. "
    "It does NOT provide medical advice, diagnosis, or treatment. The plans generated "
    "are general wellness suggestions and are NOT a substitute for professional medical "
    "guidance. Always consult a qualified healthcare professional before starting any "
    "new health, diet, or exercise program."
)

SYSTEM_PROMPT = """You are a wellness plan assistant. Your role is to generate structured,
general wellness plans based on a user's stated goals and preferences.

For each plan, provide the following sections in Markdown format:

1. **Overview**: A brief summary of the plan and its goals.
2. **Diet Suggestions**: General nutrition guidance aligned with the goal.
3. **Exercise Plan**: Activity recommendations appropriate for the stated lifestyle level.
4. **Sleep Recommendations**: Tips and habits for better sleep.
5. **Stress Management**: Techniques for managing stress.
6. **Sample Weekly Schedule**: A day-by-day outline for one week (use a Markdown table).

CRITICAL RULES:
- You are NOT a doctor. Always include a reminder that this is general wellness information only.
- Never diagnose conditions or prescribe medications.
- Recommend consulting a healthcare professional before starting any new program.
- Tailor the intensity and specifics to the stated lifestyle level and age if provided.
- If the duration is specified, structure the plan for that timeframe."""


def _build_prompt(goal: str, age: int | None, lifestyle: str | None, duration: str | None) -> str:
    """Build the prompt for generating a wellness plan."""
    parts = [f"Create a wellness plan for the following goal: {goal}"]

    if age is not None:
        parts.append(f"Age: {age}")
    if lifestyle:
        parts.append(f"Current lifestyle/activity level: {lifestyle}")
    if duration:
        duration_map = {
            "1week": "1 week",
            "1month": "1 month",
            "3months": "3 months",
        }
        parts.append(f"Plan duration: {duration_map.get(duration, duration)}")

    parts.append("\nFormat the plan in clear Markdown with the required sections.")
    return "\n".join(parts)


def _display_disclaimer() -> None:
    """Display the medical disclaimer prominently."""
    console.print()
    console.print(Panel(
        DISCLAIMER,
        title="[bold red]Health Disclaimer[/bold red]",
        border_style="red",
        padding=(1, 2),
    ))
    console.print()


def generate_plan(goal: str, age: int | None = None,
                  lifestyle: str | None = None, duration: str | None = None) -> str:
    """Generate a wellness plan using the LLM.

    Args:
        goal: The health/wellness goal.
        age: Optional age of the user.
        lifestyle: Optional activity level (sedentary, moderate, active).
        duration: Optional plan duration (1week, 1month, 3months).

    Returns:
        The LLM-generated wellness plan as a string.
    """
    prompt = _build_prompt(goal, age, lifestyle, duration)
    response = generate(
        prompt=prompt,
        system_prompt=SYSTEM_PROMPT,
        temperature=0.4,
        max_tokens=3000,
    )
    return response


def _display_plan(goal: str, plan: str) -> None:
    """Render a wellness plan with rich formatting."""
    console.print(Panel(
        Markdown(plan),
        title=f"[bold green]Wellness Plan: {goal}[/bold green]",
        border_style="green",
        padding=(1, 2),
    ))


@click.group()
def cli():
    """Health Plan Generator - Create personalized wellness plans.

    ⚠️  FOR INFORMATIONAL PURPOSES ONLY - NOT MEDICAL ADVICE.
    """
    pass


@cli.command("generate")
@click.option('--goal', required=True, help='Your wellness goal (e.g., "better sleep", "lose weight").')
@click.option('--age', type=int, default=None, help='Your age (optional, helps tailor the plan).')
@click.option(
    '--lifestyle',
    type=click.Choice(['sedentary', 'moderate', 'active'], case_sensitive=False),
    default=None,
    help='Your current activity level (optional).',
)
@click.option(
    '--duration',
    type=click.Choice(['1week', '1month', '3months'], case_sensitive=False),
    default=None,
    help='Desired plan duration (optional).',
)
def generate_cmd(goal: str, age: int | None, lifestyle: str | None, duration: str | None):
    """Generate a wellness plan for a specific goal."""
    _display_disclaimer()

    if not check_ollama_running():
        console.print("[bold red]Error:[/bold red] Ollama is not running. Please start Ollama first.")
        raise SystemExit(1)

    details = [f"Goal: {goal}"]
    if age:
        details.append(f"Age: {age}")
    if lifestyle:
        details.append(f"Lifestyle: {lifestyle}")
    if duration:
        details.append(f"Duration: {duration}")
    console.print("[bold]Generating plan with:[/bold] " + " | ".join(details) + "\n")

    try:
        with console.status("[bold green]Creating your wellness plan...[/bold green]"):
            plan = generate_plan(goal, age, lifestyle, duration)
        _display_plan(goal, plan)
    except Exception as e:
        console.print(f"[bold red]Error generating plan:[/bold red] {e}")
        raise SystemExit(1)

    _display_disclaimer()


@cli.command()
def interactive():
    """Guided questionnaire to create a personalized wellness plan."""
    _display_disclaimer()

    if not check_ollama_running():
        console.print("[bold red]Error:[/bold red] Ollama is not running. Please start Ollama first.")
        raise SystemExit(1)

    console.print(Panel(
        "[bold]Welcome to the Health Plan Generator![/bold]\n\n"
        "Answer a few questions and we'll create a personalized wellness plan for you.",
        title="[bold cyan]Interactive Mode[/bold cyan]",
        border_style="cyan",
    ))
    console.print()

    # Gather information through prompts
    goal = Prompt.ask(
        "[bold]What is your wellness goal?[/bold]",
        default="general wellness",
    )

    age_str = Prompt.ask(
        "[bold]What is your age?[/bold] [dim](press Enter to skip)[/dim]",
        default="",
    )
    age = int(age_str) if age_str.strip().isdigit() else None

    lifestyle = Prompt.ask(
        "[bold]What is your current activity level?[/bold]",
        choices=["sedentary", "moderate", "active"],
        default="moderate",
    )

    duration = Prompt.ask(
        "[bold]How long should the plan be?[/bold]",
        choices=["1week", "1month", "3months"],
        default="1month",
    )

    console.print()
    console.print("[bold]Summary:[/bold]")
    console.print(f"  Goal:      {goal}")
    if age:
        console.print(f"  Age:       {age}")
    console.print(f"  Lifestyle: {lifestyle}")
    console.print(f"  Duration:  {duration}")
    console.print()

    try:
        with console.status("[bold green]Creating your wellness plan...[/bold green]"):
            plan = generate_plan(goal, age, lifestyle, duration)
        _display_plan(goal, plan)
    except Exception as e:
        console.print(f"[bold red]Error generating plan:[/bold red] {e}")
        raise SystemExit(1)

    _display_disclaimer()


if __name__ == '__main__':
    cli()
