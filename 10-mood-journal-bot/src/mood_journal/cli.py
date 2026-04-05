"""Click CLI interface for Mood Journal Bot."""

import sys
import logging

import click
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

from .core import (
    add_entry, get_recent_entries, analyze_entries, load_entries,
    generate_weekly_report, generate_monthly_report, get_gratitude_prompt,
    get_mood_stats, export_entries, check_ollama_running,
    MOODS, SYSTEM_PROMPT,
)
from .utils import setup_logging

logger = logging.getLogger(__name__)
console = Console()


@click.group()
@click.option("--log-level", default="WARNING", help="Logging level")
def cli(log_level: str):
    """📔 Mood Journal Bot - Track your moods and get AI insights."""
    setup_logging(log_level)


@cli.command()
def journal():
    """Write a new journal entry."""
    console.print(Panel.fit("[bold cyan]📔 Mood Journal[/bold cyan]\nRecord how you're feeling today",
                            border_style="cyan"))

    # Mood selection
    table = Table(title="How are you feeling?", border_style="cyan")
    table.add_column("#", style="bold", width=3)
    table.add_column("Mood", width=15)
    for key, (emoji, name, color) in MOODS.items():
        table.add_row(key, f"{emoji} [{color}]{name}[/{color}]")
    console.print(table)

    mood_key = Prompt.ask("\n[bold yellow]Select your mood[/bold yellow]",
                          choices=list(MOODS.keys()), default="3")

    energy = Prompt.ask("[bold yellow]Energy level (1-10)[/bold yellow]", default="5")
    try:
        energy_level = max(1, min(10, int(energy)))
    except ValueError:
        energy_level = 5

    text = Prompt.ask("[bold yellow]📝 What's on your mind?[/bold yellow]")
    if not text.strip():
        console.print("[red]Entry cannot be empty.[/red]")
        return

    gratitude = Prompt.ask("[bold yellow]🙏 What are you grateful for? (optional)[/bold yellow]", default="")

    entry = add_entry(mood_key, text, energy_level, gratitude)
    emoji, mood_name, color = MOODS[mood_key]

    console.print()
    gratitude_line = f"\n🙏 {gratitude}" if gratitude else ""
    console.print(Panel(
        f"{emoji} [{color}]{mood_name}[/{color}] | Energy: {energy_level}/10\n\n{text}{gratitude_line}",
        title=f"[bold green]✅ Entry Saved — {entry['date']} {entry['time']}[/bold green]",
        border_style="green",
    ))


@cli.command()
@click.option("--days", type=click.IntRange(1, 365), default=7, help="Number of days to analyze")
def analyze(days: int):
    """Analyze mood patterns and get AI insights."""
    console.print(Panel.fit(f"[bold cyan]🔍 Mood Analysis[/bold cyan]\nAnalyzing entries from the last {days} days",
                            border_style="cyan"))

    if not check_ollama_running():
        console.print("[red]❌ Ollama is not running. Start it with: ollama serve[/red]")
        sys.exit(1)

    entries = get_recent_entries(days)
    if not entries:
        console.print(f"[yellow]No entries found in the last {days} days.[/yellow]")
        return

    _show_history_table(entries, days)
    console.print()

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
        progress.add_task("Analyzing your mood patterns...", total=None)
        analysis = analyze_entries(entries)

    console.print()
    console.print(Panel(Markdown(analysis), title="[bold green]🧠 AI Insights[/bold green]", border_style="green"))


@cli.command()
@click.option("--days", type=click.IntRange(1, 365), default=7, help="Number of days to show")
def history(days: int):
    """View recent journal entries."""
    console.print(Panel.fit("[bold cyan]📖 Journal History[/bold cyan]", border_style="cyan"))
    entries = get_recent_entries(days)
    _show_history_table(entries, days)


@cli.command()
def stats():
    """Show mood statistics."""
    mood_stats = get_mood_stats()
    if mood_stats["total"] == 0:
        console.print("[yellow]No entries yet.[/yellow]")
        return

    console.print(Panel.fit("[bold cyan]📊 Mood Statistics[/bold cyan]", border_style="cyan"))

    table = Table(title=f"All-Time Stats ({mood_stats['total']} entries)", border_style="cyan")
    table.add_column("Mood", width=20)
    table.add_column("Count", width=8)
    table.add_column("Percentage", width=12)

    for mood, count in sorted(mood_stats["mood_counts"].items(), key=lambda x: x[1], reverse=True):
        pct = (count / mood_stats["total"]) * 100
        table.add_row(mood, str(count), f"{pct:.1f}%")

    console.print(table)
    console.print(f"\n[bold]Average Energy:[/bold] {mood_stats['avg_energy']}/10")
    console.print(f"[bold]Total Entries:[/bold] {mood_stats['total']}")
    console.print(f"[bold]First Entry:[/bold] {mood_stats['first_date']}")
    console.print(f"[bold]Latest Entry:[/bold] {mood_stats['last_date']}")


@cli.command()
def weekly_report():
    """Generate a weekly mood report."""
    entries = get_recent_entries(7)
    report = generate_weekly_report(entries)
    console.print(Panel(Markdown(report), title="[bold green]📊 Weekly Report[/bold green]", border_style="green"))


@cli.command()
def monthly_report():
    """Generate a monthly mood report."""
    report = generate_monthly_report()
    console.print(Panel(Markdown(report), title="[bold green]📊 Monthly Report[/bold green]", border_style="green"))


@cli.command()
def gratitude():
    """Get a gratitude journaling prompt."""
    if not check_ollama_running():
        console.print("[red]❌ Ollama is not running.[/red]")
        sys.exit(1)

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
        progress.add_task("Generating prompt...", total=None)
        prompt = get_gratitude_prompt()

    console.print(Panel(prompt, title="[bold green]🙏 Gratitude Prompt[/bold green]", border_style="green"))


@cli.command()
@click.option("--output", default="journal_export.csv", help="Output file path")
@click.option("--days", type=int, default=None, help="Limit to last N days")
def export(output: str, days: int | None):
    """Export journal entries to CSV."""
    count = export_entries(output, days)
    console.print(f"[green]✅ Exported {count} entries to {output}[/green]")


def _show_history_table(entries: list[dict], days: int) -> None:
    """Display entries in a table."""
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
            e["date"], e["time"],
            f"{e['mood_emoji']} [{color}]{e['mood']}[/{color}]",
            f"{e['energy_level']}/10",
            e["text"][:40] + ("..." if len(e["text"]) > 40 else ""),
        )
    console.print(table)


def main():
    """Entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
