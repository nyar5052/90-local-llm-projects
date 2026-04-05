#!/usr/bin/env python3
"""Time Management Coach - Analyzes time usage and provides productivity tips."""

import sys
import os
import csv
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


def load_timelog(file_path: str) -> list[dict]:
    """Load time log from a CSV file."""
    if not os.path.exists(file_path):
        console.print(f"[red]Error:[/red] File '{file_path}' not found.")
        sys.exit(1)
    try:
        entries = []
        with open(file_path, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                entries.append(row)
        return entries
    except Exception as e:
        console.print(f"[red]Error reading CSV:[/red] {e}")
        sys.exit(1)


def compute_time_breakdown(entries: list[dict]) -> dict:
    """Compute time spent by category/activity."""
    breakdown = defaultdict(float)
    for entry in entries:
        category = entry.get("category", entry.get("Category", "Uncategorized"))
        duration_str = entry.get("duration", entry.get("Duration", entry.get("hours", "0")))
        try:
            duration = float(str(duration_str).replace("h", "").replace("hr", "").strip())
        except ValueError:
            duration = 0.0
        breakdown[category] += duration

    return dict(sorted(breakdown.items(), key=lambda x: x[1], reverse=True))


def compute_daily_totals(entries: list[dict]) -> dict:
    """Compute total hours per day."""
    daily = defaultdict(float)
    for entry in entries:
        date = entry.get("date", entry.get("Date", "unknown"))
        duration_str = entry.get("duration", entry.get("Duration", entry.get("hours", "0")))
        try:
            duration = float(str(duration_str).replace("h", "").replace("hr", "").strip())
        except ValueError:
            duration = 0.0
        daily[date] += duration

    return dict(sorted(daily.items()))


def display_breakdown(breakdown: dict, total_hours: float) -> None:
    """Display time breakdown in a formatted table."""
    table = Table(title="⏱️ Time Breakdown", show_lines=True)
    table.add_column("Category", style="cyan", min_width=18)
    table.add_column("Hours", style="green", justify="right", min_width=8)
    table.add_column("Percentage", style="yellow", justify="right", min_width=12)
    table.add_column("Visual", style="blue", min_width=22)

    for category, hours in breakdown.items():
        pct = (hours / total_hours * 100) if total_hours > 0 else 0
        bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
        table.add_row(category, f"{hours:.1f}h", f"{pct:.1f}%", bar)

    table.add_row(
        "[bold]TOTAL[/bold]", f"[bold]{total_hours:.1f}h[/bold]", "100%", "",
        style="bold",
    )
    console.print(table)


def analyze_time_usage(entries: list[dict], breakdown: dict, daily: dict) -> str:
    """Use AI to analyze time usage patterns."""
    summary = {
        "category_breakdown": breakdown,
        "daily_totals": daily,
        "total_entries": len(entries),
        "total_hours": sum(breakdown.values()),
        "avg_daily_hours": sum(daily.values()) / max(len(daily), 1),
    }

    prompt = f"""Analyze this time usage data:

{json.dumps(summary, indent=2)}

Provide:
1. **Time Usage Assessment**: How efficiently is time being spent?
2. **Productivity Score**: Rate 1-10 with reasoning
3. **Time Wasters**: Identify areas consuming disproportionate time
4. **Deep Work Analysis**: How much time is spent on focused, high-value work?
5. **Optimization Suggestions**: Specific, actionable time management tips
6. **Ideal Schedule**: Suggest an optimized daily schedule
7. **Work-Life Balance**: Assessment and recommendations

Be specific with numbers. Format in markdown."""

    return generate(
        prompt=prompt,
        system_prompt="You are an expert time management coach and productivity consultant. Provide data-driven, actionable advice.",
        temperature=0.6,
    )


def get_tips(goal: str) -> str:
    """Get AI time management tips for a specific goal."""
    prompt = f"""Provide expert time management tips for this goal: "{goal}"

Include:
1. **Understanding the Goal**: What achieving this requires
2. **Time Blocking Strategy**: How to block time for this goal
3. **Top 5 Techniques**: Specific methods (Pomodoro, time boxing, etc.)
4. **Common Pitfalls**: Mistakes to avoid
5. **Daily Routine Suggestion**: Ideal daily schedule for this goal
6. **Tools & Resources**: Helpful tools and techniques
7. **Progress Metrics**: How to measure improvement

Be practical and actionable. Format in markdown."""

    return generate(
        prompt=prompt,
        system_prompt="You are a world-class time management coach. Provide practical, evidence-based productivity advice.",
        temperature=0.7,
    )


def generate_pomodoro_plan(tasks: str, available_hours: float = 8.0) -> str:
    """Generate a Pomodoro-based plan for the day."""
    prompt = f"""Create a Pomodoro-based daily plan for these tasks:

Tasks: {tasks}
Available Hours: {available_hours}

For each task:
1. Estimate number of Pomodoro sessions (25 min each)
2. Assign priority (High/Medium/Low)
3. Suggest optimal time of day
4. Include 5-min short breaks and 15-min long breaks

Format as a clear schedule in markdown."""

    return generate(
        prompt=prompt,
        system_prompt="You are a Pomodoro technique expert.",
        temperature=0.5,
    )


@click.group()
def cli():
    """Time Management Coach - AI-powered productivity analysis and tips."""
    pass


@cli.command()
@click.option('--log', '-l', 'log_file', required=True, type=click.Path(), help='Path to time log CSV')
@click.option('--analyze', '-a', is_flag=True, help='Get AI analysis')
def review(log_file, analyze):
    """Review and analyze time usage from a log file."""
    console.print(Panel(
        "[bold blue]⏱️ Time Management Coach[/bold blue]\n"
        "[dim]Analyzing your time usage...[/dim]",
        border_style="blue",
    ))

    entries = load_timelog(log_file)
    breakdown = compute_time_breakdown(entries)
    daily = compute_daily_totals(entries)
    total_hours = sum(breakdown.values())

    display_breakdown(breakdown, total_hours)

    # Daily summary
    if daily:
        console.print(f"\n[dim]Days tracked: {len(daily)} | "
                      f"Avg daily: {total_hours/max(len(daily),1):.1f}h | "
                      f"Total: {total_hours:.1f}h[/dim]\n")

    if analyze:
        if not check_ollama_running():
            console.print("[red]Error:[/red] Ollama is not running.")
            sys.exit(1)

        with console.status("[bold green]Analyzing your time usage..."):
            result = analyze_time_usage(entries, breakdown, daily)
        console.print(Panel(Markdown(result), title="📊 Time Analysis", border_style="green"))


@cli.command()
@click.option('--goal', '-g', required=True, help='Productivity goal')
def tips(goal):
    """Get AI time management tips for a specific goal."""
    console.print(Panel(
        "[bold blue]⏱️ Time Management Coach[/bold blue]\n"
        f"[dim]Goal: {goal}[/dim]",
        border_style="blue",
    ))

    if not check_ollama_running():
        console.print("[red]Error:[/red] Ollama is not running. Start it with: [bold]ollama serve[/bold]")
        sys.exit(1)

    with console.status("[bold green]Preparing your coaching session..."):
        result = get_tips(goal)
    console.print(Panel(Markdown(result), title="💡 Time Management Tips", border_style="cyan"))


@cli.command()
@click.option('--tasks', '-t', required=True, help='Comma-separated task list')
@click.option('--hours', '-h', default=8.0, help='Available hours')
def pomodoro(tasks, hours):
    """Generate a Pomodoro-based daily plan."""
    console.print(Panel("[bold blue]⏱️ Time Management Coach[/bold blue]", border_style="blue"))

    if not check_ollama_running():
        console.print("[red]Error:[/red] Ollama is not running.")
        sys.exit(1)

    with console.status("[bold green]Creating your Pomodoro plan..."):
        result = generate_pomodoro_plan(tasks, hours)
    console.print(Panel(Markdown(result), title="🍅 Pomodoro Plan", border_style="red"))


if __name__ == '__main__':
    cli()
