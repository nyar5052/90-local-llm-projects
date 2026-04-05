#!/usr/bin/env python3
"""Habit Tracker Analyzer - Tracks habits and provides AI analysis of patterns."""

import sys
import os
import json
from datetime import datetime, timedelta
from collections import defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from common.llm_client import chat, generate, check_ollama_running

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown

console = Console()
HABITS_FILE = os.path.join(os.path.dirname(__file__), "habits.json")


def load_habits() -> dict:
    """Load habits data from JSON file."""
    if os.path.exists(HABITS_FILE):
        try:
            with open(HABITS_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {"habits": {}, "logs": []}
    return {"habits": {}, "logs": []}


def save_habits(data: dict) -> None:
    """Save habits data to JSON file."""
    with open(HABITS_FILE, 'w') as f:
        json.dump(data, f, indent=2)


def log_habit(habit_name: str, done: bool, notes: str = "") -> dict:
    """Log a habit completion for today."""
    data = load_habits()
    habit_key = habit_name.lower().replace(" ", "_")

    if habit_key not in data["habits"]:
        data["habits"][habit_key] = {
            "name": habit_name,
            "created": datetime.now().isoformat(),
            "target": "daily",
        }

    log_entry = {
        "habit": habit_key,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "time": datetime.now().strftime("%H:%M"),
        "done": done,
        "notes": notes,
    }

    data["logs"].append(log_entry)
    save_habits(data)
    return log_entry


def compute_streaks(data: dict) -> dict:
    """Compute current and best streaks for each habit."""
    streaks = {}
    for habit_key, habit_info in data["habits"].items():
        logs = sorted(
            [l for l in data["logs"] if l["habit"] == habit_key and l["done"]],
            key=lambda x: x["date"],
        )

        if not logs:
            streaks[habit_key] = {"current": 0, "best": 0, "total": 0}
            continue

        dates = sorted(set(l["date"] for l in logs))
        total = len(dates)

        # Current streak
        current = 0
        today = datetime.now().strftime("%Y-%m-%d")
        check_date = today
        for _ in range(len(dates)):
            if check_date in dates:
                current += 1
                prev = datetime.strptime(check_date, "%Y-%m-%d") - timedelta(days=1)
                check_date = prev.strftime("%Y-%m-%d")
            else:
                break

        # Best streak
        best = 1
        run = 1
        for i in range(1, len(dates)):
            d1 = datetime.strptime(dates[i - 1], "%Y-%m-%d")
            d2 = datetime.strptime(dates[i], "%Y-%m-%d")
            if (d2 - d1).days == 1:
                run += 1
                best = max(best, run)
            else:
                run = 1

        streaks[habit_key] = {"current": current, "best": best, "total": total}

    return streaks


def get_completion_rate(data: dict, days: int = 30) -> dict:
    """Compute completion rates for each habit over a period."""
    cutoff = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    rates = {}

    for habit_key in data["habits"]:
        recent_logs = [l for l in data["logs"] if l["habit"] == habit_key and l["date"] >= cutoff]
        done_count = sum(1 for l in recent_logs if l["done"])
        total_days = min(days, (datetime.now() - datetime.strptime(
            data["habits"][habit_key].get("created", datetime.now().isoformat())[:10], "%Y-%m-%d"
        )).days + 1)
        rates[habit_key] = {
            "done": done_count,
            "total_days": total_days,
            "rate": (done_count / total_days * 100) if total_days > 0 else 0,
        }

    return rates


def analyze_habits(data: dict, period: str) -> str:
    """Use AI to analyze habit patterns."""
    streaks = compute_streaks(data)
    days = {"week": 7, "month": 30, "year": 365}.get(period, 30)
    rates = get_completion_rate(data, days)

    summary = {
        "habits": {k: v["name"] for k, v in data["habits"].items()},
        "streaks": streaks,
        "completion_rates": rates,
        "period": period,
        "total_logs": len(data["logs"]),
    }

    prompt = f"""Analyze these habit tracking patterns:

{json.dumps(summary, indent=2)}

Provide:
1. **Overall Assessment**: How well are habits being maintained?
2. **Streak Analysis**: Which habits have strong/weak streaks
3. **Completion Patterns**: Best and worst performing habits
4. **Improvement Suggestions**: Specific, actionable tips for each habit
5. **Habit Stacking**: Suggest how to link habits together for better consistency
6. **Motivational Insight**: An encouraging observation

Be specific with numbers and percentages. Format in markdown."""

    return generate(
        prompt=prompt,
        system_prompt="You are a behavioral science expert and habit coach. Provide data-driven, supportive habit analysis.",
        temperature=0.6,
    )


def display_habits(data: dict) -> None:
    """Display habit status in a formatted table."""
    streaks = compute_streaks(data)
    rates = get_completion_rate(data, 30)

    table = Table(title="🎯 Habit Tracker", show_lines=True)
    table.add_column("Habit", style="white", min_width=15)
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
            f"🔥 {streak.get('current', 0)} days",
            f"⭐ {streak.get('best', 0)} days",
            f"{rate_pct:.0f}% {bar}",
            str(streak.get("total", 0)),
        )

    console.print(table)


@click.group()
def cli():
    """Habit Tracker Analyzer - Track habits and get AI-powered insights."""
    pass


@cli.command()
@click.option('--habit', '-h', required=True, help='Habit name')
@click.option('--done/--skip', default=True, help='Mark as done or skipped')
@click.option('--notes', '-n', default='', help='Optional notes')
def log(habit, done, notes):
    """Log a habit completion."""
    console.print(Panel("[bold blue]🎯 Habit Tracker[/bold blue]", border_style="blue"))
    entry = log_habit(habit, done, notes)
    status = "[green]✅ Done[/green]" if done else "[yellow]⏭️ Skipped[/yellow]"
    console.print(f"{status}: {habit} ({entry['date']})")
    if notes:
        console.print(f"[dim]Notes: {notes}[/dim]")


@cli.command()
@click.option('--period', '-p', default='month',
              type=click.Choice(['week', 'month', 'year']),
              help='Analysis period')
def analyze(period):
    """Get AI analysis of your habit patterns."""
    console.print(Panel(
        "[bold blue]🎯 Habit Tracker[/bold blue]\n"
        f"[dim]Analyzing {period}ly patterns...[/dim]",
        border_style="blue",
    ))

    if not check_ollama_running():
        console.print("[red]Error:[/red] Ollama is not running. Start it with: [bold]ollama serve[/bold]")
        sys.exit(1)

    data = load_habits()
    if not data["habits"]:
        console.print("[yellow]No habits tracked yet. Start with: python app.py log --habit 'exercise'[/yellow]")
        return

    display_habits(data)

    with console.status("[bold green]Analyzing your habits..."):
        result = analyze_habits(data, period)
    console.print(Panel(Markdown(result), title="📊 Habit Analysis", border_style="green"))


@cli.command()
def status():
    """View current habit streaks and status."""
    console.print(Panel("[bold blue]🎯 Habit Tracker[/bold blue]", border_style="blue"))
    data = load_habits()

    if not data["habits"]:
        console.print("[yellow]No habits tracked yet.[/yellow]")
        return

    display_habits(data)


if __name__ == '__main__':
    cli()
