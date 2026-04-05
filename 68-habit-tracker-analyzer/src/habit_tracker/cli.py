#!/usr/bin/env python3
"""Habit Tracker Analyzer - CLI interface."""

import sys
import os

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown
from rich.progress import BarColumn, Progress, TextColumn

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from common.llm_client import check_ollama_running

from .core import (
    load_config,
    load_habits,
    log_habit,
    add_habit,
    delete_habit,
    compute_streaks,
    get_completion_rate,
    check_achievements,
    compute_correlations,
    analyze_habits,
    generate_weekly_report,
    generate_monthly_report,
    ACHIEVEMENTS,
)

console = Console()


def _habits_file(config: dict) -> str:
    return config.get("habits_file", "habits.json")


# ---------------------------------------------------------------------------
# CLI Group
# ---------------------------------------------------------------------------

@click.group()
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output.")
@click.option("--config", "-c", "config_path", default="config.yaml",
              help="Path to config YAML.")
@click.pass_context
def cli(ctx, verbose, config_path):
    """🎯 Habit Tracker Analyzer - Track habits and get AI-powered insights."""
    ctx.ensure_object(dict)
    ctx.obj["config"] = load_config(config_path)
    ctx.obj["verbose"] = verbose


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

@cli.command()
@click.option("--habit", "-h", required=True, help="Habit name")
@click.option("--done/--skip", default=True, help="Mark as done or skipped")
@click.option("--notes", "-n", default="", help="Optional notes")
@click.pass_context
def log(ctx, habit, done, notes):
    """Log a habit completion."""
    config = ctx.obj["config"]
    console.print(Panel("[bold blue]🎯 Habit Tracker[/bold blue]", border_style="blue"))
    entry = log_habit(habit, done, notes, habits_file=_habits_file(config))
    status = "[green]✅ Done[/green]" if done else "[yellow]⏭️ Skipped[/yellow]"
    console.print(f"{status}: {habit} ({entry['date']})")
    if notes:
        console.print(f"[dim]Notes: {notes}[/dim]")

    # Show new achievements
    if config.get("achievements", {}).get("notifications"):
        data = load_habits(_habits_file(config))
        earned = check_achievements(data)
        if earned:
            console.print()
            for ach in earned:
                console.print(f"  {ach['icon']}  [bold]{ach['name']}[/bold] - {ach['description']}")


@cli.command()
@click.option("--name", "-n", required=True, help="Habit name")
@click.option("--category", "-c", default="general", help="Habit category")
@click.option("--target", "-t", default="daily",
              type=click.Choice(["daily", "weekly"]), help="Frequency target")
@click.pass_context
def add(ctx, name, category, target):
    """Add a new habit to track."""
    config = ctx.obj["config"]
    habit = add_habit(name, category, target, habits_file=_habits_file(config))
    console.print(
        Panel(
            f"[green]✅ Added habit:[/green] [bold]{habit['name']}[/bold]\n"
            f"  Category: {habit['category']}  |  Target: {habit['target']}",
            border_style="green",
        )
    )


@cli.command()
@click.option("--habit", "-h", required=True, help="Habit key to delete")
@click.pass_context
def delete(ctx, habit):
    """Delete a habit and its logs."""
    config = ctx.obj["config"]
    if delete_habit(habit, habits_file=_habits_file(config)):
        console.print(f"[red]🗑️  Deleted habit:[/red] {habit}")
    else:
        console.print(f"[yellow]Habit '{habit}' not found.[/yellow]")


@cli.command()
@click.pass_context
def status(ctx):
    """View current habit streaks and status."""
    config = ctx.obj["config"]
    console.print(Panel("[bold blue]🎯 Habit Tracker[/bold blue]", border_style="blue"))
    data = load_habits(_habits_file(config))

    if not data["habits"]:
        console.print("[yellow]No habits tracked yet.[/yellow]")
        return

    _display_habits(data)


@cli.command()
@click.option("--period", "-p", default="month",
              type=click.Choice(["week", "month", "year"]),
              help="Analysis period")
@click.pass_context
def analyze(ctx, period):
    """Get AI analysis of your habit patterns."""
    config = ctx.obj["config"]
    console.print(
        Panel(
            "[bold blue]🎯 Habit Tracker[/bold blue]\n"
            f"[dim]Analyzing {period}ly patterns...[/dim]",
            border_style="blue",
        )
    )

    if not check_ollama_running():
        console.print(
            "[red]Error:[/red] Ollama is not running. "
            "Start it with: [bold]ollama serve[/bold]"
        )
        sys.exit(1)

    data = load_habits(_habits_file(config))
    if not data["habits"]:
        console.print("[yellow]No habits tracked yet. Use 'habit-tracker add' first.[/yellow]")
        return

    _display_habits(data)

    with console.status("[bold green]Analyzing your habits..."):
        result = analyze_habits(data, period, config)
    console.print(Panel(Markdown(result), title="📊 Habit Analysis", border_style="green"))


@cli.command()
@click.pass_context
def achievements(ctx):
    """View your achievements and progress."""
    config = ctx.obj["config"]
    data = load_habits(_habits_file(config))

    if not data["habits"]:
        console.print("[yellow]No habits tracked yet.[/yellow]")
        return

    earned = check_achievements(data)
    earned_ids = {a["id"] for a in earned}

    console.print(Panel("[bold]🏅 Achievements[/bold]", border_style="gold1"))
    console.print()

    for ach_id, ach in ACHIEVEMENTS.items():
        if ach_id in earned_ids:
            console.print(f"  {ach['icon']}  [bold green]{ach['name']}[/bold green] - {ach['description']}  ✅")
        else:
            console.print(f"  🔒  [dim]{ach['name']} - {ach['description']}[/dim]")

    console.print()
    console.print(f"  [bold]{len(earned_ids)}/{len(ACHIEVEMENTS)}[/bold] achievements unlocked")


@cli.command()
@click.option("--type", "-t", "report_type", default="weekly",
              type=click.Choice(["weekly", "monthly"]),
              help="Report type")
@click.pass_context
def report(ctx, report_type):
    """Generate a habit report."""
    config = ctx.obj["config"]
    data = load_habits(_habits_file(config))

    if not data["habits"]:
        console.print("[yellow]No habits tracked yet.[/yellow]")
        return

    if report_type == "weekly":
        text = generate_weekly_report(data, config)
    else:
        text = generate_monthly_report(data, config)

    console.print(Panel(Markdown(text), title=f"📊 {report_type.title()} Report", border_style="blue"))


# ---------------------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------------------

def _display_habits(data: dict) -> None:
    """Display habit status in a formatted Rich table."""
    streaks = compute_streaks(data)
    rates = get_completion_rate(data, 30)

    table = Table(title="🎯 Habit Tracker", show_lines=True)
    table.add_column("Habit", style="white", min_width=15)
    table.add_column("Category", style="magenta", justify="center", min_width=10)
    table.add_column("Current Streak", style="green", justify="center", min_width=14)
    table.add_column("Best Streak", style="cyan", justify="center", min_width=11)
    table.add_column("30-Day Rate", style="yellow", justify="center", min_width=11)
    table.add_column("Total", style="dim", justify="center", width=8)

    for habit_key, habit_info in data["habits"].items():
        streak = streaks.get(habit_key, {})
        rate = rates.get(habit_key, {})
        rate_pct = rate.get("rate", 0)
        bar = "🟩" * int(rate_pct / 10) + "⬜" * (10 - int(rate_pct / 10))

        table.add_row(
            habit_info["name"],
            habit_info.get("category", "general"),
            f"🔥 {streak.get('current', 0)} days",
            f"⭐ {streak.get('best', 0)} days",
            f"{rate_pct:.0f}% {bar}",
            str(streak.get("total", 0)),
        )

    console.print(table)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    cli(obj={})


if __name__ == "__main__":
    main()
