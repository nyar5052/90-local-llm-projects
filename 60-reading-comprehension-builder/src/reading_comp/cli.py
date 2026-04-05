"""CLI interface for Reading Comprehension Builder."""

import json
import logging
import sys

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt

from .core import (
    generate_comprehension,
    score_exercise,
    get_answer_key,
    check_service,
    ReadingExercise,
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


def display_exercise(ex: ReadingExercise, show_answers: bool = False) -> None:
    console.print(Panel(
        f"[bold]{ex.title}[/bold]\n"
        f"Topic: {ex.topic} | Level: {ex.reading_level} | Words: ~{ex.word_count}",
        title="📚 Reading Comprehension",
        border_style="blue",
    ))

    console.print(Panel(ex.passage, title="📖 Passage", border_style="cyan", padding=(1, 2)))

    if ex.vocabulary_words:
        console.print("\n[bold yellow]📝 Key Vocabulary:[/bold yellow]")
        for v in ex.vocabulary_words:
            console.print(f"  [cyan]{v.word}[/cyan]: {v.definition}")

    console.print("\n[bold green]❓ Comprehension Questions:[/bold green]\n")
    for q in ex.questions:
        console.print(f"[bold yellow]Q{q.number}[/bold yellow] [{q.type}] [dim]({q.difficulty})[/dim]")
        console.print(f"  {q.question}")

        if q.options:
            for opt in q.options:
                console.print(f"    {opt}")

        if show_answers:
            console.print(f"  [green]Answer: {q.answer}[/green]")
            if q.explanation:
                console.print(f"  [dim]{q.explanation}[/dim]")
            if q.annotation:
                console.print(f"  [dim italic]Passage ref: {q.annotation}[/dim italic]")
        console.print()

    if show_answers and ex.summary:
        console.print(Panel(ex.summary, title="📋 Summary", border_style="green"))


def display_score(result: dict) -> None:
    pct = result["percentage"]
    color = "green" if pct >= 70 else "yellow" if pct >= 50 else "red"
    console.print(Panel(
        f"[bold {color}]Score: {result['score']}/{result['total']} ({pct:.0f}%)[/bold {color}]\n"
        f"Level: {result.get('level', 'N/A')}\n"
        f"{result.get('feedback', '')}",
        title="📊 Results",
        border_style=color,
    ))

    for d in result.get("details", []):
        icon = "✓" if d["correct"] else "✗"
        clr = "green" if d["correct"] else "red"
        console.print(f"  [{clr}]{icon}[/{clr}] Q{d['number']}: "
                      f"Your answer: {d['user_answer']} | Correct: {d['correct_answer']}")
        if not d["correct"]:
            console.print(f"    [dim]{d['explanation']}[/dim]")


def interactive_exercise(ex: ReadingExercise) -> None:
    """Run the exercise interactively with scoring."""
    console.print(Panel(ex.passage, title="📖 Read the Passage", border_style="cyan", padding=(1, 2)))

    if ex.vocabulary_words:
        console.print("\n[bold yellow]📝 Key Vocabulary:[/bold yellow]")
        for v in ex.vocabulary_words:
            console.print(f"  [cyan]{v.word}[/cyan]: {v.definition}")

    console.input("\n[dim]Press Enter when ready to answer questions...[/dim]")

    user_answers = {}
    for q in ex.questions:
        console.print(f"\n[bold yellow]Question {q.number}/{len(ex.questions)}[/bold yellow]")
        console.print(f"  {q.question}")
        if q.options:
            for opt in q.options:
                console.print(f"    {opt}")
        answer = Prompt.ask("  Your answer (A/B/C/D)").strip().upper()
        user_answers[q.number] = answer

    result = score_exercise(ex, user_answers)
    display_score(result)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


@click.group()
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
def cli(verbose):
    """📚 Reading Comprehension Builder — Create and take reading exercises."""
    _setup_logging(verbose)


@cli.command()
@click.option("--topic", "-t", required=True, help="Topic for the reading passage")
@click.option("--level", "-l", default="high school", help="Reading level")
@click.option("--questions", "-q", "num_questions", default=5, type=int, help="Number of questions")
@click.option("--length", "passage_length", type=click.Choice(["short", "medium", "long"]),
              default="medium", help="Passage length")
@click.option("--interactive", "-i", is_flag=True, help="Take the exercise interactively")
@click.option("--show-answers", "-a", is_flag=True, help="Show answers immediately")
@click.option("--output", "-o", type=click.Path(), help="Save exercise to JSON file")
def generate(topic, level, num_questions, passage_length, interactive, show_answers, output):
    """Generate a reading comprehension exercise."""
    console.print(Panel("[bold blue]📚 Reading Comprehension Builder[/bold blue]",
                        subtitle="Powered by Local LLM"))

    if not check_service():
        console.print("[red]Error: Ollama is not running. Start with: ollama serve[/red]")
        sys.exit(1)

    console.print(f"[cyan]Creating exercise about '{topic}' for {level} level...[/cyan]")

    with console.status("[bold green]Building exercise..."):
        ex = generate_comprehension(topic, level, num_questions, passage_length)

    if output:
        with open(output, "w", encoding="utf-8") as f:
            json.dump(ex.to_dict(), f, indent=2, ensure_ascii=False)
        console.print(f"[green]Exercise saved to {output}[/green]")

    if interactive:
        interactive_exercise(ex)
    else:
        display_exercise(ex, show_answers=show_answers)


@cli.command("answer-key")
@click.option("--file", "-f", "filepath", required=True, type=click.Path(exists=True),
              help="Path to exercise JSON file")
def answer_key(filepath):
    """Display the answer key for a saved exercise."""
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    from .core import _exercise_from_dict
    ex = _exercise_from_dict(data)
    key = get_answer_key(ex)

    console.print(Panel("[bold blue]📋 Answer Key[/bold blue]"))
    table = Table(title="Answer Key", show_lines=True)
    table.add_column("#", style="bold", width=4)
    table.add_column("Type", style="cyan", width=12)
    table.add_column("Question")
    table.add_column("Answer", style="green", width=8)
    table.add_column("Explanation", style="dim")

    for item in key:
        table.add_row(
            str(item["number"]),
            item["type"],
            item["question"],
            item["answer"],
            item["explanation"],
        )
    console.print(table)


def main():
    cli()


if __name__ == "__main__":
    main()
