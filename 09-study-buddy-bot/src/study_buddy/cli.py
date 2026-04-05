"""Click CLI interface for Study Buddy Bot."""

import sys
import time
import logging

import click
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.live import Live

from .core import (
    generate_quiz, explain_concept, create_study_plan, generate_flashcards,
    ask_question, record_study_session, get_study_stats,
    load_saved_flashcards, check_ollama_running,
    MODES, SYSTEM_PROMPT,
)
from .utils import setup_logging

logger = logging.getLogger(__name__)
console = Console()


@click.group()
@click.option("--log-level", default="WARNING", help="Logging level")
def cli(log_level: str):
    """📚 Study Buddy Bot - Your AI exam preparation assistant."""
    setup_logging(log_level)


@cli.command()
@click.option("--subject", required=True, help="Subject (e.g., Biology, Math)")
@click.option("--topic", required=True, help="Specific topic to study")
@click.option("--mode", type=click.Choice(list(MODES.keys()), case_sensitive=False), default=None)
def study(subject: str, topic: str, mode: str | None):
    """Start a study session with a specific mode."""
    console.print(Panel.fit("[bold cyan]📚 Study Buddy Bot[/bold cyan]\nYour AI exam preparation assistant",
                            border_style="cyan"))

    if not check_ollama_running():
        console.print("[red]❌ Ollama is not running. Start it with: ollama serve[/red]")
        sys.exit(1)

    console.print(f"[bold]Subject:[/bold] {subject}")
    console.print(f"[bold]Topic:[/bold] {topic}")
    console.print()

    if not mode:
        console.print("[bold]Available modes:[/bold]")
        for key, desc in MODES.items():
            console.print(f"  [cyan]{key}[/cyan] — {desc}")
        console.print()
        mode = Prompt.ask("[bold yellow]Choose mode[/bold yellow]",
                          choices=list(MODES.keys()), default="explain")

    start_time = time.time()

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
        if mode == "quiz":
            progress.add_task("Generating quiz...", total=None)
            result = generate_quiz(subject, topic)
        elif mode == "explain":
            progress.add_task("Preparing explanation...", total=None)
            result = explain_concept(subject, topic)
        elif mode == "plan":
            progress.add_task("Creating study plan...", total=None)
            result = create_study_plan(subject, topic)
        elif mode == "summarize":
            progress.add_task("Summarizing...", total=None)
            result = explain_concept(subject, topic, depth="summary")
        elif mode == "flashcards":
            progress.add_task("Creating flashcards...", total=None)
            result = generate_flashcards(subject, topic)
        else:
            result = "Unknown mode."

    console.print()
    console.print(Panel(Markdown(result),
                        title=f"[bold green]📚 {MODES.get(mode, mode).split()[0]} — {topic}[/bold green]",
                        border_style="green"))

    # Interactive Q&A
    console.print("\n[dim]Ask follow-up questions, or type 'quit' to exit.[/dim]\n")
    history: list[dict] = [
        {"role": "user", "content": f"I'm studying {topic} in {subject}"},
        {"role": "assistant", "content": result},
    ]

    while True:
        try:
            question = Prompt.ask("[bold yellow]📝 Your question[/bold yellow]")
        except (KeyboardInterrupt, EOFError):
            break

        if question.lower().strip() in ("quit", "exit", "q", ""):
            break

        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
            progress.add_task("Thinking...", total=None)
            response = ask_question(subject, topic, question, history)

        history.append({"role": "user", "content": question})
        history.append({"role": "assistant", "content": response})

        console.print()
        console.print(Panel(Markdown(response), title="[bold green]📚 Study Buddy[/bold green]", border_style="green"))

    duration = int((time.time() - start_time) / 60)
    if duration > 0:
        record_study_session(subject, topic, mode, duration)

    console.print("[bold cyan]📚 Good luck with your studies! Goodbye![/bold cyan]")


@cli.command()
@click.option("--minutes", type=int, default=25, help="Timer duration (Pomodoro default: 25)")
def timer(minutes: int):
    """Start a study session timer (Pomodoro technique)."""
    console.print(Panel.fit(f"[bold cyan]⏱️ Study Timer — {minutes} minutes[/bold cyan]", border_style="cyan"))
    console.print("[dim]Press Ctrl+C to stop early[/dim]\n")

    try:
        for remaining in range(minutes * 60, 0, -1):
            mins, secs = divmod(remaining, 60)
            console.print(f"\r⏱️  [bold]{mins:02d}:{secs:02d}[/bold] remaining", end="")
            time.sleep(1)
        console.print("\n\n[bold green]🎉 Time's up! Great study session![/bold green]")
        console.print("[dim]Take a 5-minute break before your next session.[/dim]")
    except KeyboardInterrupt:
        elapsed = minutes - (remaining // 60)
        console.print(f"\n\n[yellow]Timer stopped. You studied for ~{elapsed} minutes.[/yellow]")


@cli.command()
def stats():
    """Show study statistics."""
    stats = get_study_stats()
    console.print(Panel.fit("[bold cyan]📊 Study Statistics[/bold cyan]", border_style="cyan"))
    console.print(f"[bold]Total Sessions:[/bold] {stats['total_sessions']}")
    console.print(f"[bold]Total Study Time:[/bold] {stats['total_hours']} hours")

    subjects = stats.get("subjects", {})
    if subjects:
        table = Table(title="Subject Breakdown", border_style="cyan")
        table.add_column("Subject", width=20)
        table.add_column("Sessions", width=10)
        table.add_column("Time (min)", width=12)
        table.add_column("Topics", max_width=30)
        for subj, data in subjects.items():
            table.add_row(subj.capitalize(), str(data["session_count"]),
                          str(data["total_minutes"]), ", ".join(data.get("topics", [])[:3]))
        console.print(table)


@cli.command()
def flashcard_list():
    """List saved flashcard sets."""
    flashcards = load_saved_flashcards()
    if not flashcards:
        console.print("[yellow]No saved flashcard sets.[/yellow]")
        return
    table = Table(title="Saved Flashcard Sets", border_style="cyan")
    table.add_column("Subject", width=15)
    table.add_column("Topic", width=20)
    table.add_column("Cards", width=8)
    table.add_column("Created", width=12)
    for key, data in flashcards.items():
        table.add_row(data["subject"], data["topic"],
                      str(len(data.get("cards", []))), data["created_date"][:10])
    console.print(table)


def main():
    """Entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
