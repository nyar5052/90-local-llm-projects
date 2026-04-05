#!/usr/bin/env python3
"""CLI interface for Smart Calendar Assistant."""

import sys
import os
import logging

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from common.llm_client import check_ollama_running

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown

from calendar_assistant.core import (
    load_schedule,
    display_schedule,
    optimize_schedule,
    suggest_meeting_time,
    analyze_workload,
    detect_conflicts,
    score_priority,
    generate_daily_agenda,
    load_config,
)

logger = logging.getLogger(__name__)
console = Console()


def _setup_logging(level: str = "INFO") -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )


def _load_events(schedule: str | None) -> list[dict]:
    if schedule:
        return load_schedule(schedule)
    console.print("[yellow]No schedule file provided. Use --schedule / -s to load events.[/yellow]")
    return []


# ---------------------------------------------------------------------------
# CLI group
# ---------------------------------------------------------------------------

@click.group(invoke_without_command=True)
@click.option("--schedule", "-s", type=click.Path(exists=False), help="Path to schedule JSON file.")
@click.option("--log-level", "-l", default="INFO", help="Logging level.")
@click.pass_context
def main(ctx: click.Context, schedule: str | None, log_level: str) -> None:
    """📅 Smart Calendar Assistant – AI-powered schedule optimization."""
    _setup_logging(log_level)
    ctx.ensure_object(dict)
    ctx.obj["schedule"] = schedule
    if ctx.invoked_subcommand is None:
        console.print(Panel("📅 [bold cyan]Smart Calendar Assistant[/bold cyan]\nUse --help to see available commands.", expand=False))


# --- view ---------------------------------------------------------------

@main.command()
@click.pass_context
def view(ctx: click.Context) -> None:
    """View the current schedule."""
    events = _load_events(ctx.obj.get("schedule"))
    if not events:
        return
    table = Table(title="📅 Schedule", show_lines=True)
    table.add_column("#", style="dim", width=4)
    table.add_column("Title", style="bold")
    table.add_column("Start")
    table.add_column("End")
    table.add_column("Priority", justify="center")
    for i, ev in enumerate(events, 1):
        table.add_row(
            str(i),
            ev.get("title", "Untitled"),
            ev.get("start", ""),
            ev.get("end", ""),
            ev.get("priority", "medium").upper(),
        )
    console.print(table)


# --- optimize -----------------------------------------------------------

@main.command()
@click.pass_context
def optimize(ctx: click.Context) -> None:
    """Optimize the schedule using AI."""
    if not check_ollama_running():
        console.print("[red]Ollama is not running. Please start it first.[/red]")
        return
    events = _load_events(ctx.obj.get("schedule"))
    if not events:
        return
    console.print("[cyan]Optimizing schedule…[/cyan]")
    result = optimize_schedule(events)
    console.print(Panel(Markdown(result), title="✨ Optimized Schedule", border_style="green"))


# --- suggest ------------------------------------------------------------

@main.command()
@click.option("--duration", "-d", default=30, help="Meeting duration in minutes.")
@click.option("--attendees", "-a", default=None, help="Comma-separated attendees.")
@click.pass_context
def suggest(ctx: click.Context, duration: int, attendees: str | None) -> None:
    """Suggest the best time for a new meeting."""
    if not check_ollama_running():
        console.print("[red]Ollama is not running. Please start it first.[/red]")
        return
    events = _load_events(ctx.obj.get("schedule"))
    if not events:
        return
    console.print(f"[cyan]Finding best slot for a {duration}-min meeting…[/cyan]")
    result = suggest_meeting_time(events, duration, attendees)
    console.print(Panel(Markdown(result), title="💡 Meeting Suggestion", border_style="blue"))


# --- workload -----------------------------------------------------------

@main.command()
@click.pass_context
def workload(ctx: click.Context) -> None:
    """Analyze workload distribution."""
    if not check_ollama_running():
        console.print("[red]Ollama is not running. Please start it first.[/red]")
        return
    events = _load_events(ctx.obj.get("schedule"))
    if not events:
        return
    console.print("[cyan]Analyzing workload…[/cyan]")
    result = analyze_workload(events)
    console.print(Panel(Markdown(result), title="📊 Workload Analysis", border_style="magenta"))


# --- conflicts ----------------------------------------------------------

@main.command()
@click.option("--timezone", "-tz", default=None, help="IANA timezone (e.g. America/New_York).")
@click.pass_context
def conflicts(ctx: click.Context, timezone: str | None) -> None:
    """Detect scheduling conflicts."""
    events = _load_events(ctx.obj.get("schedule"))
    if not events:
        return
    pairs = detect_conflicts(events, timezone)
    if not pairs:
        console.print("[green]No conflicts detected! ✅[/green]")
        return
    table = Table(title="⚠️  Scheduling Conflicts", show_lines=True)
    table.add_column("Event A", style="bold red")
    table.add_column("Event B", style="bold red")
    for a, b in pairs:
        table.add_row(
            f"{a.get('title', '?')} ({a.get('start', '')} – {a.get('end', '')})",
            f"{b.get('title', '?')} ({b.get('start', '')} – {b.get('end', '')})",
        )
    console.print(table)


# --- agenda -------------------------------------------------------------

@main.command()
@click.option("--date", "-D", default=None, help="Date in YYYY-MM-DD format (default: today).")
@click.option("--timezone", "-tz", default=None, help="IANA timezone.")
@click.pass_context
def agenda(ctx: click.Context, date: str | None, timezone: str | None) -> None:
    """Generate a daily agenda."""
    events = _load_events(ctx.obj.get("schedule"))
    if not events:
        return
    items = generate_daily_agenda(events, date, timezone)
    if not items:
        console.print("[yellow]No events found for the requested date.[/yellow]")
        return
    table = Table(title=f"📋 Agenda for {date or 'Today'}", show_lines=True)
    table.add_column("Time", style="cyan")
    table.add_column("Title", style="bold")
    table.add_column("Priority", justify="center")
    table.add_column("Score", justify="center")
    for ev in items:
        table.add_row(
            f"{ev.get('start', '')} – {ev.get('end', '')}",
            ev.get("title", "Untitled"),
            ev.get("priority", "medium").upper(),
            str(ev.get("priority_score", "")),
        )
    console.print(table)


# --- priority -----------------------------------------------------------

@main.command()
@click.pass_context
def priority(ctx: click.Context) -> None:
    """Show events ranked by priority score."""
    events = _load_events(ctx.obj.get("schedule"))
    if not events:
        return
    scored = sorted(events, key=lambda e: score_priority(e), reverse=True)
    table = Table(title="🏆 Events by Priority", show_lines=True)
    table.add_column("Rank", style="dim", width=5)
    table.add_column("Title", style="bold")
    table.add_column("Priority", justify="center")
    table.add_column("Score", justify="center", style="cyan")
    for i, ev in enumerate(scored, 1):
        table.add_row(
            str(i),
            ev.get("title", "Untitled"),
            ev.get("priority", "medium").upper(),
            str(score_priority(ev)),
        )
    console.print(table)


if __name__ == "__main__":
    main()
