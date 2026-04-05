#!/usr/bin/env python3
"""
Flashcard Creator — Creates study flashcards from topics or notes.
Exports to JSON format and supports interactive review mode.
"""

import sys
import os
import json
import random
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from common.llm_client import chat, check_ollama_running

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm

console = Console()

SYSTEM_PROMPT = """You are an expert educator creating study flashcards.
Generate flashcards in valid JSON format.

Return a JSON object with this structure:
{
  "topic": "Topic Name",
  "cards": [
    {
      "id": 1,
      "front": "Question or term on the front of the card",
      "back": "Answer or definition on the back",
      "hint": "Optional hint",
      "difficulty": "easy|medium|hard",
      "tags": ["tag1", "tag2"]
    }
  ]
}

Return ONLY the JSON, no other text."""


def create_flashcards(topic: str, count: int, difficulty: str) -> dict:
    """Generate flashcards using the LLM."""
    prompt = (
        f"Create exactly {count} study flashcards about '{topic}'.\n"
        f"Difficulty level: {difficulty}.\n"
        f"Include clear, concise fronts (questions/terms) and detailed backs (answers/definitions).\n"
        f"Add helpful hints and relevant tags."
    )

    response = chat(
        messages=[{"role": "user", "content": prompt}],
        system_prompt=SYSTEM_PROMPT,
        temperature=0.7,
        max_tokens=4096,
    )

    try:
        text = response.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1].rsplit("```", 1)[0]
        return json.loads(text)
    except json.JSONDecodeError:
        console.print("[red]Error: Could not parse flashcard response.[/red]")
        sys.exit(1)


def display_flashcards(cards_data: dict) -> None:
    """Display flashcards in a formatted table."""
    table = Table(title=f"Flashcards: {cards_data.get('topic', 'N/A')}", show_lines=True)
    table.add_column("#", style="bold", width=4)
    table.add_column("Front", style="cyan", ratio=2)
    table.add_column("Back", style="green", ratio=3)
    table.add_column("Difficulty", style="yellow", width=10)

    for card in cards_data.get("cards", []):
        table.add_row(
            str(card.get("id", "")),
            card.get("front", ""),
            card.get("back", ""),
            card.get("difficulty", ""),
        )

    console.print(table)


def review_flashcards(cards_data: dict, shuffle: bool = True) -> None:
    """Interactive flashcard review session."""
    cards = cards_data.get("cards", [])
    if not cards:
        console.print("[red]No flashcards to review.[/red]")
        return

    if shuffle:
        random.shuffle(cards)

    correct = 0
    total = len(cards)

    console.print(Panel(f"[bold green]Review Mode[/bold green]\n"
                        f"Topic: {cards_data.get('topic', 'N/A')} | {total} cards\n"
                        f"Press Enter to reveal the answer, then rate yourself."))

    for i, card in enumerate(cards, 1):
        console.print(f"\n[bold cyan]Card {i}/{total}[/bold cyan]")
        console.print(Panel(card.get("front", ""), title="Front", border_style="cyan"))

        if card.get("hint"):
            show_hint = Confirm.ask("[dim]Show hint?[/dim]", default=False)
            if show_hint:
                console.print(f"[yellow]Hint: {card['hint']}[/yellow]")

        console.input("[dim]Press Enter to reveal answer...[/dim]")
        console.print(Panel(card.get("back", ""), title="Back", border_style="green"))

        knew_it = Confirm.ask("Did you know it?", default=True)
        if knew_it:
            correct += 1
            console.print("[green]✓ Great![/green]")
        else:
            console.print("[yellow]Keep studying this one![/yellow]")

    pct = (correct / total * 100) if total > 0 else 0
    color = "green" if pct >= 80 else "yellow" if pct >= 60 else "red"
    console.print(Panel(f"[bold {color}]Score: {correct}/{total} ({pct:.0f}%)[/bold {color}]",
                        title="Review Results"))


def load_flashcards(filepath: str) -> dict:
    """Load flashcards from a JSON file."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        console.print(f"[red]Error: File '{filepath}' not found.[/red]")
        sys.exit(1)
    except json.JSONDecodeError:
        console.print(f"[red]Error: Invalid JSON in '{filepath}'.[/red]")
        sys.exit(1)


@click.group()
def cli():
    """Flashcard Creator — Generate and review study flashcards."""
    pass


@cli.command()
@click.option("--topic", "-t", required=True, help="Topic for flashcards")
@click.option("--count", "-c", default=10, type=int, help="Number of flashcards (default: 10)")
@click.option("--difficulty", "-d", type=click.Choice(["easy", "medium", "hard"]),
              default="medium", help="Difficulty level")
@click.option("--output", "-o", type=click.Path(), default=None,
              help="Output JSON file (default: flashcards_<topic>.json)")
def create(topic, count, difficulty, output):
    """Create flashcards from a topic."""
    console.print(Panel("[bold blue]🗂️ Flashcard Creator[/bold blue]",
                        subtitle="Powered by Local LLM"))

    if not check_ollama_running():
        console.print("[red]Error: Ollama is not running. Start with: ollama serve[/red]")
        sys.exit(1)

    console.print(f"[cyan]Creating {count} flashcards about '{topic}'...[/cyan]")

    with console.status("[bold green]Generating flashcards..."):
        cards_data = create_flashcards(topic, count, difficulty)

    display_flashcards(cards_data)

    if output is None:
        safe_topic = topic.lower().replace(" ", "_")[:30]
        output = f"flashcards_{safe_topic}.json"

    with open(output, "w", encoding="utf-8") as f:
        json.dump(cards_data, f, indent=2, ensure_ascii=False)

    console.print(f"\n[green]✓ Flashcards saved to {output}[/green]")


@cli.command()
@click.option("--file", "-f", "filepath", required=True, type=click.Path(exists=True),
              help="Path to flashcards JSON file")
@click.option("--shuffle/--no-shuffle", default=True, help="Shuffle cards (default: on)")
def review(filepath, shuffle):
    """Review flashcards from a JSON file."""
    console.print(Panel("[bold blue]🗂️ Flashcard Review[/bold blue]"))
    cards_data = load_flashcards(filepath)
    review_flashcards(cards_data, shuffle=shuffle)


if __name__ == "__main__":
    cli()
