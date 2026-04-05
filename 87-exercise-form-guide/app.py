"""
Exercise Form Guide - AI-powered exercise form instructions and routines.

Provides detailed exercise form guidance including target muscles, step-by-step
instructions, common mistakes, breathing cues, progressions, and safety tips.

⚠️  DISCLAIMER: This tool is for educational purposes only and is NOT medical advice.
Always consult a qualified fitness professional or physician before starting any
exercise program. Improper form can lead to injury.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from common.llm_client import generate, check_ollama_running

import click
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.text import Text

console = Console()

DISCLAIMER = (
    "[bold red]⚠️  DISCLAIMER:[/bold red] This tool provides AI-generated exercise "
    "guidance for [bold]educational purposes only[/bold]. It is [bold]NOT medical advice[/bold]. "
    "Always consult a qualified fitness professional or physician before starting any exercise "
    "program. Improper form can lead to serious injury."
)

VALID_LEVELS = ["beginner", "intermediate", "advanced"]
VALID_MUSCLE_GROUPS = ["legs", "chest", "back", "shoulders", "arms", "core", "full body"]
VALID_GOALS = ["strength", "hypertrophy", "endurance", "flexibility"]

SYSTEM_PROMPT = """You are an expert exercise science coach and certified personal trainer.
When providing exercise guidance, always include:

1. **Exercise Description**: Brief overview of the exercise and its benefits.
2. **Target Muscles**: Primary and secondary muscles worked.
3. **Step-by-Step Form Instructions**: Numbered steps with precise cues.
4. **Common Mistakes**: What people typically do wrong and how to fix it.
5. **Breathing Cues**: When to inhale and exhale during the movement.
6. **Progressions & Regressions**: Easier and harder variations.
7. **Safety Tips**: Important safety considerations and contraindications.

Format your response in clean Markdown with clear section headers.
Be specific, actionable, and prioritize safety above all else.

IMPORTANT: Always include a reminder that users should consult a healthcare provider
or certified trainer before attempting new exercises."""


def display_disclaimer():
    """Display the fitness/medical disclaimer."""
    console.print()
    console.print(Panel(DISCLAIMER, title="Health & Safety Notice", border_style="red"))
    console.print()


def display_result(title: str, content: str):
    """Display LLM result with rich formatting."""
    display_disclaimer()
    console.print(Panel(Markdown(content), title=title, border_style="green", padding=(1, 2)))
    console.print()
    console.print(
        "[dim italic]Remember: Always prioritize proper form over heavier weights. "
        "When in doubt, seek professional guidance.[/dim italic]"
    )
    console.print()


@click.group()
def cli():
    """🏋️ Exercise Form Guide - AI-powered exercise instruction and routines.

    Get detailed form instructions, discover exercises by muscle group,
    and generate workout routines tailored to your level and goals.

    ⚠️  Not medical advice. Consult a professional before exercising.
    """
    pass


@cli.command()
@click.option(
    "--exercise", required=True, help="Name of the exercise (e.g., 'deadlift', 'bench press')."
)
@click.option(
    "--level",
    type=click.Choice(VALID_LEVELS, case_sensitive=False),
    default="beginner",
    help="Experience level for tailored guidance.",
)
def guide(exercise: str, level: str):
    """Get detailed form instructions for a specific exercise."""
    try:
        if not check_ollama_running():
            console.print("[bold red]Error:[/bold red] Ollama is not running. Please start it first.")
            raise SystemExit(1)

        console.print(f"[bold blue]🔍 Generating form guide for:[/bold blue] {exercise} ({level} level)")
        console.print("[dim]Consulting AI coach...[/dim]")

        prompt = (
            f"Provide a comprehensive exercise form guide for '{exercise}' "
            f"tailored to a {level}-level trainee.\n\n"
            f"Include all sections: description, target muscles, step-by-step form, "
            f"common mistakes, breathing cues, progressions/regressions, and safety tips.\n\n"
            f"Adjust complexity and cues for the {level} level."
        )

        response = generate(prompt=prompt, system_prompt=SYSTEM_PROMPT)
        display_result(f"Exercise Form Guide: {exercise.title()} ({level.title()})", response)

    except SystemExit:
        raise
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise SystemExit(1)


@cli.command("list")
@click.option(
    "--muscle-group",
    required=True,
    type=click.Choice(VALID_MUSCLE_GROUPS, case_sensitive=False),
    help="Muscle group to list exercises for.",
)
def list_exercises(muscle_group: str):
    """List exercises for a specific muscle group."""
    try:
        if not check_ollama_running():
            console.print("[bold red]Error:[/bold red] Ollama is not running. Please start it first.")
            raise SystemExit(1)

        console.print(f"[bold blue]🔍 Listing exercises for:[/bold blue] {muscle_group}")
        console.print("[dim]Consulting AI coach...[/dim]")

        prompt = (
            f"List 10-15 exercises that target the '{muscle_group}' muscle group.\n\n"
            f"For each exercise, provide:\n"
            f"- Exercise name\n"
            f"- Difficulty level (beginner/intermediate/advanced)\n"
            f"- Equipment needed (if any)\n"
            f"- Brief one-line description\n\n"
            f"Organize from easiest to most advanced. Format as a clean Markdown list."
        )

        response = generate(prompt=prompt, system_prompt=SYSTEM_PROMPT)
        display_result(f"Exercises for: {muscle_group.title()}", response)

    except SystemExit:
        raise
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise SystemExit(1)


@cli.command()
@click.option(
    "--goal",
    required=True,
    type=click.Choice(VALID_GOALS, case_sensitive=False),
    help="Training goal for the routine.",
)
@click.option(
    "--level",
    type=click.Choice(VALID_LEVELS, case_sensitive=False),
    default="beginner",
    help="Experience level.",
)
def routine(goal: str, level: str):
    """Generate a workout routine based on goal and level."""
    try:
        if not check_ollama_running():
            console.print("[bold red]Error:[/bold red] Ollama is not running. Please start it first.")
            raise SystemExit(1)

        console.print(f"[bold blue]🏋️ Generating routine:[/bold blue] {goal} ({level} level)")
        console.print("[dim]Consulting AI coach...[/dim]")

        prompt = (
            f"Create a weekly workout routine for a {level}-level trainee "
            f"with a primary goal of {goal}.\n\n"
            f"Include:\n"
            f"- Weekly schedule (which days, which muscle groups)\n"
            f"- Exercises for each day with sets, reps, and rest periods\n"
            f"- Warm-up and cool-down recommendations\n"
            f"- Progression strategy over 4-6 weeks\n"
            f"- Recovery and nutrition tips\n\n"
            f"Format as clean Markdown with clear day-by-day structure.\n"
            f"Adjust volume and intensity appropriately for the {level} level."
        )

        response = generate(prompt=prompt, system_prompt=SYSTEM_PROMPT)
        display_result(f"Workout Routine: {goal.title()} ({level.title()})", response)

    except SystemExit:
        raise
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise SystemExit(1)


if __name__ == "__main__":
    cli()
