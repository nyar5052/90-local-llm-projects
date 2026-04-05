"""Click CLI interface for Language Learning Bot."""

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
    get_response, get_lesson, get_pronunciation_tips, generate_lesson_plan,
    get_vocabulary_quiz, add_vocabulary_word, load_vocabulary,
    record_session, get_progress_summary, check_ollama_running,
    LANGUAGES, LEVELS,
)
from .utils import setup_logging

logger = logging.getLogger(__name__)
console = Console()


@click.group()
@click.option("--log-level", default="WARNING", help="Logging level")
def cli(log_level: str):
    """🌍 Language Learning Bot - Practice conversations in your target language."""
    setup_logging(log_level)


@cli.command()
@click.option("--language", type=click.Choice(LANGUAGES, case_sensitive=False), required=True, help="Target language")
@click.option("--level", type=click.Choice(LEVELS, case_sensitive=False), default="beginner", help="Proficiency level")
def chat_cmd(language: str, level: str):
    """Start an interactive conversation practice session."""
    console.print(
        Panel.fit(
            "[bold cyan]🌍 Language Learning Bot[/bold cyan]\n"
            f"Practice {language.capitalize()} at {level} level",
            border_style="cyan",
        )
    )

    if not check_ollama_running():
        console.print("[red]❌ Ollama is not running. Start it with: ollama serve[/red]")
        sys.exit(1)

    console.print(f"[bold]Language:[/bold] {language.capitalize()}")
    console.print(f"[bold]Level:[/bold] {level.capitalize()}")
    console.print()
    console.print(
        Panel(
            "[bold]Commands:[/bold]\n"
            "  [cyan]/lesson <topic>[/cyan] — Get a mini lesson\n"
            "  [cyan]/translate <text>[/cyan] — Translate to/from target language\n"
            "  [cyan]/vocab[/cyan] — Get useful vocabulary\n"
            "  [cyan]/pronounce <word>[/cyan] — Get pronunciation tips\n"
            "  [cyan]/add <word> = <translation>[/cyan] — Add to vocabulary tracker\n"
            "  [cyan]/my-vocab[/cyan] — Show saved vocabulary\n"
            "  [cyan]/progress[/cyan] — Show learning progress\n"
            "  [cyan]quit[/cyan] — Exit\n\n"
            "[dim]Or just type in English or the target language to practice![/dim]",
            title="[bold]How to Use[/bold]",
            border_style="yellow",
        )
    )

    history: list[dict] = []

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
        progress.add_task("Preparing your tutor...", total=None)
        greeting = get_response(
            f"Greet me in {language} and start a simple conversation appropriate for a {level} student.",
            [], language, level,
        )

    history.append({
        "role": "user",
        "content": f"Greet me in {language} and start a simple conversation appropriate for a {level} student.",
    })
    history.append({"role": "assistant", "content": greeting})

    console.print()
    console.print(Panel(Markdown(greeting), title=f"[bold green]🎓 {language.capitalize()} Tutor[/bold green]", border_style="green"))

    turn_count = 0
    while True:
        try:
            user_input = Prompt.ask("\n[bold yellow]You[/bold yellow]")
        except (KeyboardInterrupt, EOFError):
            break

        if user_input.lower().strip() in ("quit", "exit", "q"):
            break
        if not user_input.strip():
            continue

        # Handle special commands
        if user_input.startswith("/lesson "):
            topic = user_input[8:].strip()
            with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
                progress.add_task(f"Preparing lesson on {topic}...", total=None)
                response = get_lesson(topic, language, level)
            console.print()
            console.print(Panel(Markdown(response), title=f"[bold green]📚 Lesson: {topic}[/bold green]", border_style="green"))
            continue

        if user_input.startswith("/translate "):
            text = user_input[11:].strip()
            user_input = f"Translate this: '{text}'"

        if user_input.strip() == "/vocab":
            user_input = f"Give me 10 useful {language} vocabulary words for a {level} student with translations and example sentences."

        if user_input.startswith("/pronounce "):
            word = user_input[11:].strip()
            with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
                progress.add_task(f"Getting pronunciation tips...", total=None)
                response = get_pronunciation_tips(word, language)
            console.print()
            console.print(Panel(Markdown(response), title=f"[bold green]🗣️ Pronunciation: {word}[/bold green]", border_style="green"))
            continue

        if user_input.startswith("/add "):
            parts = user_input[5:].split("=", 1)
            if len(parts) == 2:
                word, translation = parts[0].strip(), parts[1].strip()
                add_vocabulary_word(language, word, translation)
                console.print(f"[green]✅ Added: {word} = {translation}[/green]")
            else:
                console.print("[red]Usage: /add <word> = <translation>[/red]")
            continue

        if user_input.strip() == "/my-vocab":
            vocab = load_vocabulary(language)
            if not vocab:
                console.print("[yellow]No vocabulary saved yet.[/yellow]")
            else:
                table = Table(title=f"{language.capitalize()} Vocabulary", border_style="cyan")
                table.add_column("#", width=4)
                table.add_column("Word", width=20)
                table.add_column("Translation", width=20)
                table.add_column("Added", width=12)
                for v in vocab[-20:]:
                    table.add_row(str(v["id"]), v["word"], v["translation"], v["added_date"][:10])
                console.print(table)
            continue

        if user_input.strip() == "/progress":
            summary = get_progress_summary(language)
            console.print(Panel(summary, title="[bold green]📊 Progress[/bold green]", border_style="green"))
            continue

        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
            progress.add_task("Thinking...", total=None)
            response = get_response(user_input, history, language, level)

        history.append({"role": "user", "content": user_input})
        history.append({"role": "assistant", "content": response})
        turn_count += 1

        console.print()
        console.print(Panel(Markdown(response), title="[bold green]🎓 Tutor[/bold green]", border_style="green"))

    if turn_count > 0:
        record_session(language, level, turn_count * 2, "conversation")

    console.print(f"\n[bold cyan]🌍 Great practice! Keep learning {language.capitalize()}! Goodbye![/bold cyan]")


@cli.command()
@click.option("--language", type=click.Choice(LANGUAGES, case_sensitive=False), required=True)
@click.option("--level", type=click.Choice(LEVELS, case_sensitive=False), default="beginner")
@click.option("--weeks", type=int, default=4, help="Plan duration in weeks")
def lesson_plan(language: str, level: str, weeks: int):
    """Generate a structured lesson plan."""
    if not check_ollama_running():
        console.print("[red]❌ Ollama is not running.[/red]")
        sys.exit(1)

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
        progress.add_task("Creating lesson plan...", total=None)
        plan = generate_lesson_plan(language, level, weeks)

    console.print(Panel(Markdown(plan), title=f"[bold green]📋 {language.capitalize()} Lesson Plan[/bold green]", border_style="green"))


@cli.command()
@click.option("--language", type=click.Choice(LANGUAGES, case_sensitive=False), required=True)
@click.option("--count", type=int, default=5, help="Number of questions")
def quiz(language: str, count: int):
    """Take a vocabulary quiz from saved words."""
    if not check_ollama_running():
        console.print("[red]❌ Ollama is not running.[/red]")
        sys.exit(1)

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
        progress.add_task("Generating quiz...", total=None)
        quiz_content = get_vocabulary_quiz(language, count)

    console.print(Panel(Markdown(quiz_content), title="[bold green]📝 Vocabulary Quiz[/bold green]", border_style="green"))


@cli.command()
@click.option("--language", type=click.Choice(LANGUAGES, case_sensitive=False), required=True)
def progress_cmd(language: str):
    """Show learning progress."""
    summary = get_progress_summary(language)
    console.print(Panel(summary, title="[bold green]📊 Progress[/bold green]", border_style="green"))


def main():
    """Entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
