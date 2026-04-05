"""CLI interface for Vocabulary Builder."""

import json
import logging
import sys

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt

from .core import (
    generate_vocabulary,
    load_vocab_file,
    run_quiz,
    check_service,
    VocabularySet,
    WordEntry,
)

console = Console()
logger = logging.getLogger(__name__)


def _setup_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


# ---------------------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------------------


def display_vocabulary(vs: VocabularySet) -> None:
    console.print(Panel(
        f"[bold]{vs.topic}[/bold]\nLevel: {vs.level} | Words: {len(vs.words)}",
        title="📖 Vocabulary Builder",
        border_style="blue",
    ))

    for w in vs.words:
        console.print(f"\n[bold cyan]{w.word}[/bold cyan] [dim]({w.part_of_speech})[/dim]")
        console.print(f"  [white]{w.definition}[/white]")
        if w.example_sentence:
            console.print(f'  [italic green]Example: "{w.example_sentence}"[/italic green]')
        if w.etymology:
            console.print(f"  [yellow]Etymology: {w.etymology}[/yellow]")
        if w.synonyms:
            console.print(f"  [dim]Synonyms: {', '.join(w.synonyms)}[/dim]")
        if w.antonyms:
            console.print(f"  [dim]Antonyms: {', '.join(w.antonyms)}[/dim]")
        if w.word_family:
            console.print(f"  [dim]Word Family: {', '.join(w.word_family)}[/dim]")
        if w.context_sentences:
            console.print("  [dim]Context Sentences:[/dim]")
            for s in w.context_sentences:
                console.print(f'    • "{s}"')
        if w.mnemonic:
            console.print(f"  [magenta]💡 Mnemonic: {w.mnemonic}[/magenta]")


def run_interactive_quiz(words: list) -> None:
    """Run an interactive vocabulary quiz in the terminal."""
    import random
    random.shuffle(words)

    score = 0
    total = len(words)

    console.print(Panel(
        f"[bold green]Vocabulary Quiz[/bold green]\n{total} words\nType the word that matches the definition.",
        border_style="green",
    ))

    for i, w in enumerate(words, 1):
        console.print(f"\n[bold yellow]Question {i}/{total}[/bold yellow]")
        console.print(f"  Definition: {w.definition}")
        if w.part_of_speech:
            console.print(f"  [dim]Part of speech: {w.part_of_speech}[/dim]")

        answer = Prompt.ask("  Your answer").strip().lower()

        if answer == w.word.lower():
            console.print("[green]✓ Correct![/green]")
            score += 1
        else:
            console.print(f"[red]✗ The word is: {w.word}[/red]")
            if w.mnemonic:
                console.print(f"  [magenta]Mnemonic: {w.mnemonic}[/magenta]")

    pct = (score / total * 100) if total > 0 else 0
    color = "green" if pct >= 80 else "yellow" if pct >= 60 else "red"
    console.print(Panel(f"[bold {color}]Score: {score}/{total} ({pct:.0f}%)[/bold {color}]",
                        title="Quiz Results"))


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


@click.group()
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
def cli(verbose):
    """📖 Vocabulary Builder — Learn and quiz vocabulary words."""
    _setup_logging(verbose)


@cli.command()
@click.option("--topic", "-t", required=True, help="Vocabulary topic")
@click.option("--count", "-c", default=10, type=int, help="Number of words")
@click.option("--level", "-l", default="", help="Target level (e.g., advanced, GRE)")
@click.option("--output", "-o", type=click.Path(), default=None, help="Output JSON file")
def learn(topic, count, level, output):
    """Generate vocabulary list from a topic."""
    console.print(Panel("[bold blue]📖 Vocabulary Builder[/bold blue]",
                        subtitle="Powered by Local LLM"))

    if not check_service():
        console.print("[red]Error: Ollama is not running. Start with: ollama serve[/red]")
        sys.exit(1)

    console.print(f"[cyan]Generating {count} words for '{topic}'...[/cyan]")

    with console.status("[bold green]Building vocabulary..."):
        vs = generate_vocabulary(topic, count, level)

    display_vocabulary(vs)

    if output is None:
        safe_topic = topic.lower().replace(" ", "_")[:30]
        output = f"vocab_{safe_topic}.json"

    with open(output, "w", encoding="utf-8") as f:
        json.dump(vs.to_dict(), f, indent=2, ensure_ascii=False)
    console.print(f"\n[green]✓ Vocabulary saved to {output}[/green]")


@cli.command()
@click.option("--file", "-f", "filepath", required=True, type=click.Path(exists=True),
              help="Path to vocabulary JSON file")
def quiz(filepath):
    """Quiz yourself on vocabulary from a file."""
    console.print(Panel("[bold blue]📖 Vocabulary Quiz[/bold blue]"))
    vs = load_vocab_file(filepath)
    run_interactive_quiz(vs.words)


def main():
    cli()


if __name__ == "__main__":
    main()
