"""
Symptom Checker Bot - CLI Module

Command-line interface for the symptom checker powered by Click and Rich.
"""

import sys
import os
import logging

# Path setup for common module
_common_path = os.path.join(os.path.dirname(__file__), '..', '..', '..')
sys.path.insert(0, os.path.abspath(_common_path))

import click
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.table import Table

from symptom_checker.core import (
    DISCLAIMER,
    SYSTEM_PROMPT,
    SYMPTOM_DATABASE,
    URGENCY_LABELS,
    assess_urgency,
    get_body_regions,
    check_symptoms,
    display_disclaimer,
    MedicalHistoryTracker,
    check_ollama_running,
)

logger = logging.getLogger("symptom_checker.cli")
console = Console()

# Session-level history tracker
_history = MedicalHistoryTracker()


@click.group()
def cli():
    """🏥 Symptom Checker Bot - AI-powered symptom analysis (EDUCATIONAL ONLY)."""
    pass


@cli.command()
@click.option("--symptoms", "-s", required=True, help="Describe your symptoms")
def check(symptoms: str):
    """Analyze symptoms with urgency scoring and LLM-powered insights."""
    display_disclaimer()

    # Urgency assessment
    level, label, advice = assess_urgency(symptoms)
    regions = get_body_regions(symptoms)

    console.print()
    console.print(Panel(
        f"[bold]Urgency Level:[/bold] {label}\n[bold]Advice:[/bold] {advice}",
        title="📊 Urgency Assessment",
        border_style="yellow" if level <= 2 else ("red" if level >= 4 else "orange1"),
    ))

    region_text = ", ".join(f"[cyan]{r}[/cyan]" for r in regions)
    console.print(f"\n🗺️  [bold]Affected Body Regions:[/bold] {region_text}\n")

    # LLM analysis
    if not check_ollama_running():
        console.print("[bold red]Error:[/bold red] Ollama is not running. "
                      "Please start Ollama first (`ollama serve`).")
        raise SystemExit(1)

    console.print("[bold]Analyzing symptoms...[/bold]\n")
    try:
        response = check_symptoms(symptoms)
        console.print(Panel(Markdown(response), title="🔍 Analysis", border_style="blue"))

        _history.add_entry(symptoms, level, regions, response)
    except Exception as exc:
        console.print(f"[bold red]Error during analysis:[/bold red] {exc}")
        raise SystemExit(1)

    console.print(Panel(
        "[bold red]Remember:[/bold red] This is for educational purposes ONLY. "
        "Always consult a qualified healthcare professional.",
        border_style="red",
    ))


@cli.command("chat")
def chat_mode():
    """Start an interactive symptom-checking chat session."""
    display_disclaimer()
    console.print("\n[bold cyan]Interactive Symptom Chat[/bold cyan]")
    console.print("Type your symptoms or questions. Type [bold]'quit'[/bold] or [bold]'exit'[/bold] to end.\n")

    if not check_ollama_running():
        console.print("[bold red]Error:[/bold red] Ollama is not running. "
                      "Please start Ollama first (`ollama serve`).")
        raise SystemExit(1)

    conversation_history: list[dict] = []

    while True:
        try:
            user_input = console.input("[bold green]You:[/bold green] ").strip()
        except (EOFError, KeyboardInterrupt):
            console.print("\n[yellow]Session ended.[/yellow]")
            break

        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit", "q"):
            console.print("[yellow]Session ended. Stay healthy![/yellow]")
            break

        # Show urgency
        level, label, advice = assess_urgency(user_input)
        regions = get_body_regions(user_input)

        if level >= 4:
            console.print(f"\n[bold red]{label}[/bold red]: {advice}\n")

        try:
            response = check_symptoms(user_input, conversation_history)
            console.print(Panel(Markdown(response), title="🩺 Response", border_style="blue"))

            conversation_history.append({"role": "user", "content": user_input})
            conversation_history.append({"role": "assistant", "content": response})

            _history.add_entry(user_input, level, regions, response)
        except Exception as exc:
            console.print(f"[bold red]Error:[/bold red] {exc}")

    # Show session summary
    summary = _history.get_summary()
    if summary["total_checks"] > 0:
        console.print(Panel(
            f"Total checks: {summary['total_checks']}\n"
            f"Max urgency: {summary['max_urgency']}\n"
            f"Regions affected: {', '.join(summary['regions_affected'])}",
            title="📋 Session Summary",
            border_style="cyan",
        ))


@cli.command()
def history():
    """Display symptom check history for this session."""
    entries = _history.get_history()
    if not entries:
        console.print("[yellow]No symptom checks recorded in this session.[/yellow]")
        return

    table = Table(title="📋 Symptom Check History")
    table.add_column("Time", style="cyan")
    table.add_column("Symptoms", style="white")
    table.add_column("Urgency", style="yellow")
    table.add_column("Regions", style="green")

    for entry in entries:
        urgency_label = URGENCY_LABELS.get(entry["urgency"], ("?", ""))[0]
        table.add_row(
            entry["timestamp"][:19],
            entry["symptoms"][:60] + ("..." if len(entry["symptoms"]) > 60 else ""),
            urgency_label,
            ", ".join(entry["regions"]),
        )

    console.print(table)


@cli.command()
def regions():
    """Display all tracked body regions and their symptoms."""
    console.print()
    for region, data in SYMPTOM_DATABASE.items():
        symptom_list = ", ".join(data["symptoms"])
        console.print(Panel(
            f"[bold]{data['description']}[/bold]\n\n"
            f"Symptoms: {symptom_list}",
            title=f"🗺️  {region.capitalize()}",
            border_style="cyan",
        ))
    console.print()


if __name__ == "__main__":
    cli()
