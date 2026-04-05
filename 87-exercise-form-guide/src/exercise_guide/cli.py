"""
Exercise Form Guide - CLI interface.

Provides click-based CLI commands for exercise guidance, muscle info,
warm-up/cool-down routines, and progression paths.

⚠️  DISCLAIMER: This tool is for educational purposes only and is NOT medical advice.
"""

import click
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.table import Table

from exercise_guide.core import (
    DISCLAIMER,
    SYSTEM_PROMPT,
    VALID_LEVELS,
    VALID_MUSCLE_GROUPS,
    VALID_GOALS,
    MUSCLE_GROUP_DATABASE,
    PROGRESSION_PATHS,
    check_ollama_running,
    generate_guide,
    list_exercises as core_list_exercises,
    generate_routine,
    get_warmup_routine,
    get_cooldown_routine,
    get_exercise_variations,
    get_muscle_info,
)

console = Console()

RICH_DISCLAIMER = (
    "[bold red]⚠️  DISCLAIMER:[/bold red] This tool provides AI-generated exercise "
    "guidance for [bold]educational purposes only[/bold]. It is [bold]NOT medical advice[/bold]. "
    "Always consult a qualified fitness professional or physician before starting any exercise "
    "program. Improper form can lead to serious injury."
)


def display_disclaimer():
    """Display the fitness/medical disclaimer."""
    console.print()
    console.print(Panel(RICH_DISCLAIMER, title="Health & Safety Notice", border_style="red"))
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


# ---------------------------------------------------------------------------
# CLI Group
# ---------------------------------------------------------------------------


@click.group()
def cli():
    """🏋️ Exercise Form Guide - AI-powered exercise instruction and routines.

    Get detailed form instructions, discover exercises by muscle group,
    and generate workout routines tailored to your level and goals.

    ⚠️  Not medical advice. Consult a professional before exercising.
    """
    pass


# ---------------------------------------------------------------------------
# Existing Commands
# ---------------------------------------------------------------------------


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

        response = generate_guide(exercise, level)
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
def list_cmd(muscle_group: str):
    """List exercises for a specific muscle group."""
    try:
        if not check_ollama_running():
            console.print("[bold red]Error:[/bold red] Ollama is not running. Please start it first.")
            raise SystemExit(1)

        console.print(f"[bold blue]🔍 Listing exercises for:[/bold blue] {muscle_group}")
        console.print("[dim]Consulting AI coach...[/dim]")

        response = core_list_exercises(muscle_group)
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

        response = generate_routine(goal, level)
        display_result(f"Workout Routine: {goal.title()} ({level.title()})", response)

    except SystemExit:
        raise
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise SystemExit(1)


# ---------------------------------------------------------------------------
# New Commands
# ---------------------------------------------------------------------------


@cli.command()
@click.option(
    "--muscle-group",
    required=True,
    type=click.Choice(VALID_MUSCLE_GROUPS, case_sensitive=False),
    help="Muscle group to get warm-up routine for.",
)
def warmup(muscle_group: str):
    """Show a warm-up routine for a muscle group."""
    display_disclaimer()
    exercises = get_warmup_routine(muscle_group)
    if not exercises:
        console.print(f"[bold red]No warm-up routine found for '{muscle_group}'.[/bold red]")
        raise SystemExit(1)

    table = Table(title=f"🔥 Warm-up Routine: {muscle_group.title()}", border_style="yellow")
    table.add_column("Exercise", style="bold cyan")
    table.add_column("Duration", style="green")
    table.add_column("Description")

    for ex in exercises:
        table.add_row(ex["name"], ex["duration"], ex["description"])

    console.print(table)
    console.print()


@cli.command()
@click.option(
    "--muscle-group",
    required=True,
    type=click.Choice(VALID_MUSCLE_GROUPS, case_sensitive=False),
    help="Muscle group to get cool-down stretches for.",
)
def cooldown(muscle_group: str):
    """Show cool-down stretches for a muscle group."""
    display_disclaimer()
    stretches = get_cooldown_routine(muscle_group)
    if not stretches:
        console.print(f"[bold red]No cool-down routine found for '{muscle_group}'.[/bold red]")
        raise SystemExit(1)

    table = Table(title=f"🧘 Cool-down Stretches: {muscle_group.title()}", border_style="blue")
    table.add_column("Stretch", style="bold cyan")
    table.add_column("Duration", style="green")
    table.add_column("Description")

    for s in stretches:
        table.add_row(s["name"], s["duration"], s["description"])

    console.print(table)
    console.print()


@cli.command()
@click.option(
    "--exercise",
    required=True,
    type=click.Choice(list(PROGRESSION_PATHS.keys()), case_sensitive=False),
    help="Exercise to show progression path for.",
)
def progression(exercise: str):
    """Show the progression path for an exercise."""
    display_disclaimer()
    variations = get_exercise_variations(exercise)
    if not variations:
        console.print(f"[bold red]No progression path found for '{exercise}'.[/bold red]")
        raise SystemExit(1)

    console.print()
    console.print(Panel(
        f"[bold]📈 Progression Path: {exercise.title()}[/bold]",
        border_style="magenta",
    ))
    console.print()

    for i, step in enumerate(variations, 1):
        level_label = "Beginner" if i <= 2 else ("Intermediate" if i <= 4 else "Advanced")
        color = "green" if i <= 2 else ("yellow" if i <= 4 else "red")
        console.print(f"  [{color}]Step {i}:[/{color}] {step}  [dim]({level_label})[/dim]")

    console.print()


@cli.command()
@click.option(
    "--group",
    required=True,
    type=click.Choice(VALID_MUSCLE_GROUPS, case_sensitive=False),
    help="Muscle group to show info for.",
)
def muscles(group: str):
    """Show detailed information about a muscle group."""
    display_disclaimer()
    info = get_muscle_info(group)
    if not info:
        console.print(f"[bold red]No info found for muscle group '{group}'.[/bold red]")
        raise SystemExit(1)

    console.print()
    console.print(Panel(
        f"[bold]💪 Muscle Group: {group.title()}[/bold]\n\n{info['description']}",
        border_style="cyan",
    ))

    console.print()
    console.print("[bold]Muscles:[/bold]")
    for m in info["muscles"]:
        console.print(f"  • {m}")

    console.print()
    console.print("[bold]Common Exercises:[/bold]")
    for ex in info["common_exercises"]:
        console.print(f"  • {ex}")
    console.print()


# ---------------------------------------------------------------------------
# Entry Point
# ---------------------------------------------------------------------------


def main():
    """Entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
