"""
Health Plan Generator - CLI interface.

⚠️  DISCLAIMER: This tool is for INFORMATIONAL and EDUCATIONAL PURPOSES ONLY.
It does NOT provide medical advice, diagnosis, or treatment. Always consult a
qualified healthcare professional before starting any new health, diet, or
exercise program.
"""

import json
import os
import sys

import click
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import IntPrompt, Prompt
from rich.table import Table

from health_planner.core import (
    DISCLAIMER,
    WEEKLY_CHECKIN_QUESTIONS,
    ProgressTracker,
    check_ollama_running,
    generate_adaptive_recommendation,
    generate_plan,
    get_milestones_for_goal,
)

console = Console()

# Persist progress between CLI invocations
_PROGRESS_FILE = os.path.join(
    os.path.dirname(__file__), "..", "..", ".health_progress.json"
)


def _load_tracker() -> ProgressTracker:
    """Load progress tracker from disk."""
    try:
        with open(_PROGRESS_FILE, "r", encoding="utf-8") as fh:
            return ProgressTracker.from_dict(json.load(fh))
    except (FileNotFoundError, json.JSONDecodeError):
        return ProgressTracker()


def _save_tracker(tracker: ProgressTracker) -> None:
    """Save progress tracker to disk."""
    with open(_PROGRESS_FILE, "w", encoding="utf-8") as fh:
        json.dump(tracker.to_dict(), fh, indent=2)


def _display_disclaimer() -> None:
    """Display the medical disclaimer prominently."""
    console.print()
    console.print(
        Panel(
            DISCLAIMER,
            title="[bold red]Health Disclaimer[/bold red]",
            border_style="red",
            padding=(1, 2),
        )
    )
    console.print()


def _display_plan(goal: str, plan: str) -> None:
    """Render a wellness plan with rich formatting."""
    console.print(
        Panel(
            Markdown(plan),
            title=f"[bold green]Wellness Plan: {goal}[/bold green]",
            border_style="green",
            padding=(1, 2),
        )
    )


def _display_milestones(goal: str) -> None:
    """Display milestones for a given goal as a rich table."""
    milestones = get_milestones_for_goal(goal)
    table = Table(
        title=f"🎯 Milestones for: {goal}",
        show_header=True,
        header_style="bold cyan",
    )
    table.add_column("Week", justify="center", style="bold")
    table.add_column("Milestone", style="white")
    table.add_column("💡 Tip", style="dim")

    for m in milestones:
        table.add_row(str(m["week"]), m["milestone"], m["tip"])

    console.print()
    console.print(table)
    console.print()


# ---------------------------------------------------------------------------
# CLI Group
# ---------------------------------------------------------------------------


@click.group()
def cli():
    """🏋️ Health Plan Generator - Create personalized wellness plans.

    ⚠️  FOR INFORMATIONAL PURPOSES ONLY - NOT MEDICAL ADVICE.
    Always consult a healthcare professional before starting any new program.
    """
    pass


# ---------------------------------------------------------------------------
# Generate Command
# ---------------------------------------------------------------------------


@cli.command("generate")
@click.option(
    "--goal",
    required=True,
    help='Your wellness goal (e.g., "better sleep", "lose weight").',
)
@click.option(
    "--age",
    type=int,
    default=None,
    help="Your age (optional, helps tailor the plan).",
)
@click.option(
    "--lifestyle",
    type=click.Choice(["sedentary", "moderate", "active"], case_sensitive=False),
    default=None,
    help="Your current activity level (optional).",
)
@click.option(
    "--duration",
    type=click.Choice(["1week", "1month", "3months"], case_sensitive=False),
    default=None,
    help="Desired plan duration (optional).",
)
def generate_cmd(
    goal: str, age: int | None, lifestyle: str | None, duration: str | None
):
    """Generate a wellness plan for a specific goal."""
    _display_disclaimer()

    if not check_ollama_running():
        console.print(
            "[bold red]Error:[/bold red] Ollama is not running. Please start Ollama first."
        )
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

    # Show milestones alongside the plan
    _display_milestones(goal)

    # Initialize tracker for the new plan
    tracker = _load_tracker()
    tracker.start_plan(goal)
    _save_tracker(tracker)

    _display_disclaimer()


# ---------------------------------------------------------------------------
# Interactive Command
# ---------------------------------------------------------------------------


@cli.command()
def interactive():
    """Guided questionnaire to create a personalized wellness plan."""
    _display_disclaimer()

    if not check_ollama_running():
        console.print(
            "[bold red]Error:[/bold red] Ollama is not running. Please start Ollama first."
        )
        raise SystemExit(1)

    console.print(
        Panel(
            "[bold]Welcome to the Health Plan Generator![/bold]\n\n"
            "Answer a few questions and we'll create a personalized wellness plan for you.",
            title="[bold cyan]Interactive Mode[/bold cyan]",
            border_style="cyan",
        )
    )
    console.print()

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

    _display_milestones(goal)

    tracker = _load_tracker()
    tracker.start_plan(goal)
    _save_tracker(tracker)

    _display_disclaimer()


# ---------------------------------------------------------------------------
# Milestones Command
# ---------------------------------------------------------------------------


@cli.command()
@click.option(
    "--goal",
    required=True,
    help='The goal to show milestones for (e.g., "lose weight").',
)
def milestones(goal: str):
    """Show week-by-week milestones for a health goal."""
    _display_disclaimer()
    _display_milestones(goal)
    _display_disclaimer()


# ---------------------------------------------------------------------------
# Check-in Command
# ---------------------------------------------------------------------------


@cli.command()
def checkin():
    """Complete a weekly progress check-in."""
    _display_disclaimer()

    tracker = _load_tracker()
    if not tracker.goal:
        console.print(
            "[bold yellow]No active plan found.[/bold yellow] "
            "Generate a plan first with [bold]generate[/bold] or [bold]interactive[/bold]."
        )
        return

    console.print(
        Panel(
            f"[bold]Weekly Check-in — Week {tracker.current_week}[/bold]\n"
            f"Goal: {tracker.goal}\n"
            f"Started: {tracker.start_date}",
            title="[bold cyan]📋 Weekly Check-in[/bold cyan]",
            border_style="cyan",
        )
    )
    console.print()

    # Show current milestone
    milestone = tracker.get_current_milestone()
    if milestone:
        console.print(
            Panel(
                f"[bold]Week {milestone['week']} Milestone:[/bold] {milestone['milestone']}\n"
                f"💡 [dim]{milestone['tip']}[/dim]",
                border_style="yellow",
            )
        )
        console.print()

    responses: dict = {}

    energy = Prompt.ask(WEEKLY_CHECKIN_QUESTIONS[0], default="5")
    responses["energy"] = int(energy) if energy.isdigit() else 5

    responses["meal_plan"] = Prompt.ask(
        WEEKLY_CHECKIN_QUESTIONS[1],
        choices=["mostly", "partially", "not really"],
        default="partially",
    )

    exercise_days = Prompt.ask(WEEKLY_CHECKIN_QUESTIONS[2], default="3")
    responses["exercise_days"] = int(exercise_days) if exercise_days.isdigit() else 3

    sleep = Prompt.ask(WEEKLY_CHECKIN_QUESTIONS[3], default="5")
    responses["sleep"] = int(sleep) if sleep.isdigit() else 5

    responses["challenge"] = Prompt.ask(WEEKLY_CHECKIN_QUESTIONS[4], default="")
    responses["win"] = Prompt.ask(WEEKLY_CHECKIN_QUESTIONS[5], default="")

    stress = Prompt.ask(WEEKLY_CHECKIN_QUESTIONS[6], default="5")
    responses["stress"] = int(stress) if stress.isdigit() else 5

    responses["symptoms"] = Prompt.ask(WEEKLY_CHECKIN_QUESTIONS[7], default="None")
    responses["adjustments"] = Prompt.ask(WEEKLY_CHECKIN_QUESTIONS[8], default="")

    entry = tracker.add_checkin(responses)
    _save_tracker(tracker)

    console.print()
    console.print(
        Panel(
            f"[bold green]✅ Check-in for Week {entry['week']} saved![/bold green]",
            border_style="green",
        )
    )

    # Show adaptive recommendations
    recs = generate_adaptive_recommendation(tracker)
    console.print()
    console.print(
        Panel(
            recs,
            title="[bold cyan]📊 Recommendations[/bold cyan]",
            border_style="cyan",
        )
    )

    _display_disclaimer()


# ---------------------------------------------------------------------------
# Progress Command
# ---------------------------------------------------------------------------


@cli.command()
def progress():
    """Show progress summary and recommendations."""
    _display_disclaimer()

    tracker = _load_tracker()
    if not tracker.goal:
        console.print(
            "[bold yellow]No active plan found.[/bold yellow] "
            "Generate a plan first with [bold]generate[/bold] or [bold]interactive[/bold]."
        )
        return

    summary = tracker.get_progress_summary()

    table = Table(
        title="📈 Progress Summary",
        show_header=True,
        header_style="bold cyan",
    )
    table.add_column("Metric", style="bold")
    table.add_column("Value", justify="center")

    table.add_row("Goal", str(summary.get("goal", "N/A")))
    table.add_row("Start Date", str(summary.get("start_date", "N/A")))
    table.add_row("Weeks Completed", str(summary.get("weeks_completed", 0)))
    table.add_row("Current Week", str(summary.get("current_week", 1)))
    table.add_row(
        "Avg Energy",
        f"{summary['avg_energy']:.1f}/10" if summary.get("avg_energy") is not None else "N/A",
    )
    table.add_row(
        "Avg Sleep",
        f"{summary['avg_sleep']:.1f}/10" if summary.get("avg_sleep") is not None else "N/A",
    )
    table.add_row("Total Check-ins", str(summary.get("total_checkins", 0)))

    console.print()
    console.print(table)

    # Recommendations
    recs = generate_adaptive_recommendation(tracker)
    console.print()
    console.print(
        Panel(
            recs,
            title="[bold cyan]🔄 Adaptive Recommendations[/bold cyan]",
            border_style="cyan",
        )
    )

    # Show milestones
    _display_milestones(tracker.goal)

    _display_disclaimer()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    cli()
