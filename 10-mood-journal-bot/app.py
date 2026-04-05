"""
Mood Journal Bot - Private mood tracking with AI insights.

Track daily moods and journal entries, then analyze patterns over time
using Gemma 4 via Ollama. All data stored locally in JSON.
"""

import sys
import os
import json
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import click
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from common.llm_client import chat, check_ollama_running

console = Console()

SYSTEM_PROMPT = """You are an empathetic and supportive mood journal analyst. Your role is to:
1. Help users reflect on their emotions and experiences
2. Identify mood patterns and trends over time
3. Provide supportive, non-judgmental responses
4. Suggest healthy coping strategies when appropriate
5. Celebrate positive moments and progress

Guidelines:
- Be warm, empathetic, and encouraging
- Never diagnose mental health conditions
- Recommend professional help if entries suggest serious distress
- Focus on patterns, not individual entries
- Respect privacy and emotional vulnerability"""

MOODS = {
    "1": ("😊", "Happy", "green"),
    "2": ("😌", "Calm", "cyan"),
    "3": ("😐", "Neutral", "white"),
    "4": ("😔", "Sad", "blue"),
    "5": ("😤", "Angry", "red"),
    "6": ("😰", "Anxious", "yellow"),
    "7": ("😫", "Stressed", "magenta"),
    "8": ("🥰", "Grateful", "green"),
    "9": ("😴", "Tired", "dim"),
    "10": ("🤗", "Excited", "bright_yellow"),
}

JOURNAL_FILE = os.path.join(os.path.dirname(__file__), "journal_entries.json")


def load_entries() -> list[dict]:
    """Load journal entries from the JSON file."""
    if not os.path.exists(JOURNAL_FILE):
        return []
    try:
        with open(JOURNAL_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def save_entries(entries: list[dict]) -> None:
    """Save journal entries to the JSON file."""
    with open(JOURNAL_FILE, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2, ensure_ascii=False)


def add_entry(mood_key: str, text: str, energy_level: int = 5) -> dict:
    """Create and save a new journal entry."""
    emoji, mood_name, _ = MOODS[mood_key]
    entry = {
        "id": len(load_entries()) + 1,
        "timestamp": datetime.now().isoformat(),
        "date": datetime.now().strftime("%Y-%m-%d"),
        "time": datetime.now().strftime("%H:%M"),
        "mood": mood_name,
        "mood_emoji": emoji,
        "mood_score": int(mood_key),
        "energy_level": energy_level,
        "text": text,
    }
    entries = load_entries()
    entries.append(entry)
    save_entries(entries)
    return entry


def get_recent_entries(days: int = 7) -> list[dict]:
    """Get entries from the last N days."""
    entries = load_entries()
    cutoff = datetime.now() - timedelta(days=days)
    return [
        e for e in entries
        if datetime.fromisoformat(e["timestamp"]) >= cutoff
    ]


def analyze_entries(entries: list[dict]) -> str:
    """Analyze mood patterns in journal entries using LLM."""
    if not entries:
        return "No entries to analyze. Start journaling to see insights!"

    summary_lines = []
    for e in entries:
        summary_lines.append(
            f"- {e['date']} {e['time']}: {e['mood_emoji']} {e['mood']} "
            f"(energy: {e['energy_level']}/10) — {e['text'][:100]}"
        )
    entries_text = "\n".join(summary_lines)

    messages = [
        {
            "role": "user",
            "content": (
                f"Analyze these mood journal entries and provide insights:\n\n"
                f"{entries_text}\n\n"
                "Please provide:\n"
                "1. Overall mood trend (improving, declining, stable)\n"
                "2. Most common moods and potential triggers\n"
                "3. Energy level patterns\n"
                "4. Positive observations\n"
                "5. Gentle suggestions for well-being\n"
                "Be warm, supportive, and encouraging."
            ),
        }
    ]
    return chat(messages, system_prompt=SYSTEM_PROMPT, max_tokens=2048)


def display_mood_menu():
    """Display the mood selection menu."""
    table = Table(title="How are you feeling?", border_style="cyan")
    table.add_column("#", style="bold", width=3)
    table.add_column("Mood", width=15)
    for key, (emoji, name, color) in MOODS.items():
        table.add_row(key, f"{emoji} [{color}]{name}[/{color}]")
    console.print(table)


def show_history(days: int = 7):
    """Display recent journal entries."""
    entries = get_recent_entries(days)
    if not entries:
        console.print(f"[yellow]No entries in the last {days} days.[/yellow]")
        return

    table = Table(title=f"Journal — Last {days} Days", border_style="cyan")
    table.add_column("Date", width=12)
    table.add_column("Time", width=6)
    table.add_column("Mood", width=15)
    table.add_column("Energy", width=8)
    table.add_column("Entry", max_width=40)

    for e in entries:
        _, _, color = MOODS.get(str(e.get("mood_score", 3)), ("", "", "white"))
        table.add_row(
            e["date"],
            e["time"],
            f"{e['mood_emoji']} [{color}]{e['mood']}[/{color}]",
            f"{e['energy_level']}/10",
            e["text"][:40] + ("..." if len(e["text"]) > 40 else ""),
        )
    console.print(table)


@click.group()
def cli():
    """Mood Journal Bot - Track your moods and get AI insights."""
    pass


@cli.command()
def journal():
    """Write a new journal entry."""
    console.print(
        Panel.fit(
            "[bold cyan]📔 Mood Journal[/bold cyan]\n"
            "Record how you're feeling today",
            border_style="cyan",
        )
    )

    display_mood_menu()
    mood_key = Prompt.ask(
        "\n[bold yellow]Select your mood[/bold yellow]",
        choices=list(MOODS.keys()),
        default="3",
    )

    energy = Prompt.ask(
        "[bold yellow]Energy level (1-10)[/bold yellow]",
        default="5",
    )
    try:
        energy_level = max(1, min(10, int(energy)))
    except ValueError:
        energy_level = 5

    text = Prompt.ask("[bold yellow]📝 What's on your mind?[/bold yellow]")

    if not text.strip():
        console.print("[red]Entry cannot be empty.[/red]")
        return

    entry = add_entry(mood_key, text, energy_level)
    emoji, mood_name, color = MOODS[mood_key]

    console.print()
    console.print(
        Panel(
            f"{emoji} [{color}]{mood_name}[/{color}] | Energy: {energy_level}/10\n\n"
            f"{text}",
            title=f"[bold green]✅ Entry Saved — {entry['date']} {entry['time']}[/bold green]",
            border_style="green",
        )
    )


@cli.command()
@click.option("--days", type=click.IntRange(1, 365), default=7, help="Number of days to analyze")
def analyze(days: int):
    """Analyze mood patterns and get AI insights."""
    console.print(
        Panel.fit(
            "[bold cyan]🔍 Mood Analysis[/bold cyan]\n"
            f"Analyzing entries from the last {days} days",
            border_style="cyan",
        )
    )

    if not check_ollama_running():
        console.print("[red]❌ Ollama is not running. Start it with: ollama serve[/red]")
        sys.exit(1)

    entries = get_recent_entries(days)

    if not entries:
        console.print(f"[yellow]No entries found in the last {days} days.[/yellow]")
        console.print("[dim]Use 'python app.py journal' to add entries first.[/dim]")
        return

    show_history(days)
    console.print()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        progress.add_task("Analyzing your mood patterns...", total=None)
        analysis = analyze_entries(entries)

    console.print()
    console.print(
        Panel(Markdown(analysis), title="[bold green]🧠 AI Insights[/bold green]", border_style="green")
    )


@cli.command()
@click.option("--days", type=click.IntRange(1, 365), default=7, help="Number of days to show")
def history(days: int):
    """View recent journal entries."""
    console.print(
        Panel.fit(
            "[bold cyan]📖 Journal History[/bold cyan]",
            border_style="cyan",
        )
    )
    show_history(days)


@cli.command()
def stats():
    """Show mood statistics."""
    entries = load_entries()
    if not entries:
        console.print("[yellow]No entries yet.[/yellow]")
        return

    console.print(
        Panel.fit("[bold cyan]📊 Mood Statistics[/bold cyan]", border_style="cyan")
    )

    total = len(entries)
    mood_counts: dict[str, int] = {}
    total_energy = 0

    for e in entries:
        mood = e.get("mood", "Unknown")
        mood_counts[mood] = mood_counts.get(mood, 0) + 1
        total_energy += e.get("energy_level", 5)

    table = Table(title=f"All-Time Stats ({total} entries)", border_style="cyan")
    table.add_column("Mood", width=20)
    table.add_column("Count", width=8)
    table.add_column("Percentage", width=12)

    for mood, count in sorted(mood_counts.items(), key=lambda x: x[1], reverse=True):
        pct = (count / total) * 100
        table.add_row(mood, str(count), f"{pct:.1f}%")

    console.print(table)
    console.print(f"\n[bold]Average Energy:[/bold] {total_energy / total:.1f}/10")
    console.print(f"[bold]Total Entries:[/bold] {total}")
    console.print(f"[bold]First Entry:[/bold] {entries[0].get('date', 'N/A')}")
    console.print(f"[bold]Latest Entry:[/bold] {entries[-1].get('date', 'N/A')}")


if __name__ == "__main__":
    cli()
