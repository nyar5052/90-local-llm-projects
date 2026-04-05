#!/usr/bin/env python3
"""Smart Calendar Assistant - Schedule optimization and meeting suggestions using AI."""

import sys
import os
import json
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from common.llm_client import chat, generate, check_ollama_running

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown

console = Console()


def load_schedule(file_path: str) -> list[dict]:
    """Load calendar schedule from a JSON file."""
    if not os.path.exists(file_path):
        console.print(f"[red]Error:[/red] File '{file_path}' not found.")
        sys.exit(1)
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        if isinstance(data, dict) and "events" in data:
            return data["events"]
        if isinstance(data, list):
            return data
        console.print("[red]Error:[/red] Invalid schedule format. Expected a list of events or {\"events\": [...]}.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        console.print(f"[red]Error:[/red] Invalid JSON: {e}")
        sys.exit(1)


def display_schedule(events: list[dict]) -> None:
    """Display the current schedule in a rich table."""
    table = Table(title="📅 Current Schedule", show_lines=True)
    table.add_column("Date", style="cyan", min_width=12)
    table.add_column("Time", style="green", min_width=12)
    table.add_column("Event", style="white", min_width=20)
    table.add_column("Duration", style="yellow", min_width=10)
    table.add_column("Priority", style="magenta", min_width=8)

    for event in events:
        table.add_row(
            event.get("date", "N/A"),
            event.get("time", "N/A"),
            event.get("title", "Untitled"),
            event.get("duration", "N/A"),
            event.get("priority", "normal"),
        )

    console.print(table)


def optimize_schedule(events: list[dict]) -> str:
    """Use AI to optimize the schedule and suggest improvements."""
    schedule_text = json.dumps(events, indent=2)
    prompt = f"""Analyze the following calendar schedule and provide optimization suggestions:

{schedule_text}

Please provide:
1. **Schedule Analysis**: Overview of current schedule density and balance
2. **Optimization Suggestions**: How to rearrange meetings for better productivity
3. **Best Meeting Times**: Suggest optimal slots for new meetings
4. **Break Recommendations**: Suggest breaks to avoid burnout
5. **Conflict Detection**: Identify any overlapping or too-close events

Format your response in clear markdown with headers and bullet points."""

    return generate(
        prompt=prompt,
        system_prompt="You are an expert calendar and productivity assistant. Provide actionable, specific scheduling advice.",
        temperature=0.6,
    )


def suggest_meeting_time(events: list[dict], meeting_duration: str, attendees: str) -> str:
    """Suggest the best time for a new meeting."""
    schedule_text = json.dumps(events, indent=2)
    prompt = f"""Given this existing schedule:

{schedule_text}

I need to schedule a meeting with:
- Duration: {meeting_duration}
- Attendees: {attendees}

Please suggest the 3 best time slots for this meeting, considering:
1. Gaps in the existing schedule
2. Avoiding early morning and late evening
3. Leaving buffer time between meetings
4. Optimal productivity hours (9-11 AM, 2-4 PM)

Format each suggestion with the date, time, and reasoning."""

    return generate(
        prompt=prompt,
        system_prompt="You are a smart calendar assistant that finds optimal meeting times.",
        temperature=0.5,
    )


def analyze_workload(events: list[dict]) -> str:
    """Analyze the workload distribution across the schedule."""
    schedule_text = json.dumps(events, indent=2)
    prompt = f"""Analyze the workload in this schedule:

{schedule_text}

Provide:
1. **Daily Load**: Hours booked per day
2. **Work-Life Balance Score**: Rate 1-10
3. **Busiest Day**: Which day has the most commitments
4. **Free Time Analysis**: Available slots for deep work
5. **Recommendations**: How to improve balance

Use markdown formatting."""

    return generate(
        prompt=prompt,
        system_prompt="You are a workload analysis expert focused on productivity and well-being.",
        temperature=0.6,
    )


@click.command()
@click.option('--schedule', '-s', type=click.Path(), help='Path to calendar JSON file')
@click.option('--optimize', '-o', is_flag=True, help='Optimize the schedule')
@click.option('--suggest', is_flag=True, help='Suggest a meeting time')
@click.option('--duration', '-d', default='60 minutes', help='Meeting duration for suggestions')
@click.option('--attendees', '-a', default='team', help='Meeting attendees')
@click.option('--workload', '-w', is_flag=True, help='Analyze workload distribution')
@click.option('--view', '-v', is_flag=True, help='View current schedule')
def main(schedule, optimize, suggest, duration, attendees, workload, view):
    """Smart Calendar Assistant - AI-powered schedule optimization."""
    console.print(Panel(
        "[bold blue]📅 Smart Calendar Assistant[/bold blue]\n"
        "[dim]AI-powered schedule optimization and meeting suggestions[/dim]",
        border_style="blue",
    ))

    if not check_ollama_running():
        console.print("[red]Error:[/red] Ollama is not running. Start it with: [bold]ollama serve[/bold]")
        sys.exit(1)

    if not schedule:
        console.print("[yellow]Please provide a schedule file with --schedule[/yellow]")
        console.print("\nUsage examples:")
        console.print("  python app.py --schedule calendar.json --optimize")
        console.print("  python app.py --schedule calendar.json --suggest --duration '30 minutes'")
        console.print("  python app.py --schedule calendar.json --workload")
        return

    events = load_schedule(schedule)

    if view or (not optimize and not suggest and not workload):
        display_schedule(events)

    if optimize:
        with console.status("[bold green]Optimizing your schedule..."):
            result = optimize_schedule(events)
        console.print(Panel(Markdown(result), title="✨ Schedule Optimization", border_style="green"))

    if suggest:
        with console.status("[bold green]Finding the best meeting time..."):
            result = suggest_meeting_time(events, duration, attendees)
        console.print(Panel(Markdown(result), title="🕐 Suggested Meeting Times", border_style="cyan"))

    if workload:
        with console.status("[bold green]Analyzing workload..."):
            result = analyze_workload(events)
        console.print(Panel(Markdown(result), title="📊 Workload Analysis", border_style="magenta"))


if __name__ == '__main__':
    main()
