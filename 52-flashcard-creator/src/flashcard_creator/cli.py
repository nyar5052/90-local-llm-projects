#!/usr/bin/env python3
"""
Flashcard Creator — CLI interface built with Click.

Provides commands: create, review, decks, import-deck, export-deck, stats.
"""

import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
from common.llm_client import check_ollama_running  # noqa: E402

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

try:
    from flashcard_creator.core import (
        ConfigManager, DeckManager, SpacedRepetition, ReviewSession,
        create_flashcards, dict_to_flashcards, setup_logging, Deck,
    )
except ModuleNotFoundError:
    from src.flashcard_creator.core import (
        ConfigManager, DeckManager, SpacedRepetition, ReviewSession,
        create_flashcards, dict_to_flashcards, setup_logging, Deck,
    )

console = Console()


def _ensure_ollama() -> None:
    if not check_ollama_running():
        console.print("[red]Error: Ollama is not running. Start with: ollama serve[/red]")
        sys.exit(1)


@click.group()
@click.pass_context
def cli(ctx: click.Context) -> None:
    """🗂️ Flashcard Creator — Generate and review study flashcards."""
    ctx.ensure_object(dict)
    cfg = ConfigManager()
    setup_logging(cfg)
    ctx.obj["config"] = cfg
    decks_dir = cfg.get("storage", "decks_dir", "./decks")
    ctx.obj["deck_manager"] = DeckManager(decks_dir)


# ---- create ----------------------------------------------------------------

@cli.command()
@click.option("--topic", "-t", required=True, help="Topic for flashcards")
@click.option("--count", "-c", default=None, type=int, help="Number of flashcards")
@click.option("--difficulty", "-d", type=click.Choice(["easy", "medium", "hard"]),
              default=None, help="Difficulty level")
@click.option("--deck-name", "-n", default=None, help="Save to named deck")
@click.option("--output", "-o", type=click.Path(), default=None,
              help="Output JSON file path")
@click.pass_context
def create(ctx, topic, count, difficulty, deck_name, output):
    """Create flashcards from a topic using the LLM."""
    cfg: ConfigManager = ctx.obj["config"]
    dm: DeckManager = ctx.obj["deck_manager"]

    if count is None:
        count = cfg.get("flashcards", "default_count", 10)
    if difficulty is None:
        difficulty = cfg.get("flashcards", "default_difficulty", "medium")

    console.print(Panel("[bold blue]🗂️ Flashcard Creator[/bold blue]",
                        subtitle="Powered by Local LLM"))

    _ensure_ollama()
    console.print(f"[cyan]Creating {count} flashcards about '{topic}'...[/cyan]")

    with console.status("[bold green]Generating flashcards..."):
        cards_data = create_flashcards(topic, count, difficulty, config=cfg)

    # Display table
    _display_table(cards_data)

    # Persist to deck if requested
    if deck_name:
        deck = dm.get_deck(deck_name) or dm.create_deck(deck_name, description=f"Flashcards about {topic}")
        for fc in dict_to_flashcards(cards_data):
            deck.cards.append(fc)
        dm._save(deck)
        console.print(f"[green]✓ Added {count} cards to deck '{deck_name}'[/green]")

    # Save raw JSON
    if output is None:
        safe = topic.lower().replace(" ", "_")[:30]
        output = f"flashcards_{safe}.json"
    with open(output, "w", encoding="utf-8") as f:
        json.dump(cards_data, f, indent=2, ensure_ascii=False)
    console.print(f"[green]✓ Flashcards saved to {output}[/green]")


# ---- review ----------------------------------------------------------------

@cli.command()
@click.option("--deck", "-d", "deck_name", required=True, help="Deck name to review")
@click.option("--due-only", is_flag=True, default=False, help="Only review due cards")
@click.option("--shuffle/--no-shuffle", default=True, help="Shuffle cards")
@click.pass_context
def review(ctx, deck_name, due_only, shuffle):
    """Interactive flashcard review session."""
    dm: DeckManager = ctx.obj["deck_manager"]
    deck = dm.get_deck(deck_name)
    if deck is None:
        console.print(f"[red]Deck '{deck_name}' not found.[/red]")
        sys.exit(1)

    session = ReviewSession(deck, shuffle=shuffle, due_only=due_only)
    if not session.cards:
        console.print("[yellow]No cards due for review.[/yellow]")
        return

    sr = SpacedRepetition(ctx.obj["config"])
    total = len(session.cards)
    console.print(Panel(f"[bold green]Review Mode[/bold green]\n"
                        f"Deck: {deck.name} | {total} card(s)"))

    from rich.prompt import Confirm
    for i, card in enumerate(session.cards, 1):
        console.print(f"\n[bold cyan]Card {i}/{total}[/bold cyan]")
        console.print(Panel(card.front, title="Front", border_style="cyan"))
        if card.hint:
            if Confirm.ask("[dim]Show hint?[/dim]", default=False):
                console.print(f"[yellow]Hint: {card.hint}[/yellow]")
        console.input("[dim]Press Enter to reveal answer...[/dim]")
        console.print(Panel(card.back, title="Back", border_style="green"))

        quality = click.prompt("Rate quality (0-5)", type=click.IntRange(0, 5), default=3)
        session.record(quality)
        sr.calculate_next_review(card, quality)

    dm._save(deck)
    stats = session.finish()
    color = "green" if stats.score_pct >= 80 else "yellow" if stats.score_pct >= 60 else "red"
    console.print(Panel(
        f"[bold {color}]Score: {stats.correct}/{stats.cards_reviewed} ({stats.score_pct:.0f}%)[/bold {color}]\n"
        f"Avg quality: {stats.avg_quality:.1f} | Time: {stats.time_elapsed_s:.0f}s",
        title="Review Results",
    ))


# ---- decks -----------------------------------------------------------------

@cli.command()
@click.pass_context
def decks(ctx):
    """List all saved decks."""
    dm: DeckManager = ctx.obj["deck_manager"]
    all_decks = dm.list_decks()
    if not all_decks:
        console.print("[yellow]No decks found.[/yellow]")
        return
    table = Table(title="Saved Decks", show_lines=True)
    table.add_column("Name", style="cyan")
    table.add_column("Cards", style="green", justify="right")
    table.add_column("Tags", style="yellow")
    table.add_column("Created", style="dim")
    for d in all_decks:
        table.add_row(d.name, str(len(d.cards)), ", ".join(d.tags), d.created_at[:10])
    console.print(table)


# ---- import-deck -----------------------------------------------------------

@cli.command("import-deck")
@click.option("--file", "-f", "filepath", required=True, type=click.Path(exists=True),
              help="File to import")
@click.option("--format", "-F", "fmt", type=click.Choice(["json", "csv"]),
              default="json", help="File format")
@click.pass_context
def import_deck(ctx, filepath, fmt):
    """Import a deck from a file."""
    dm: DeckManager = ctx.obj["deck_manager"]
    deck = dm.import_deck(filepath, fmt=fmt)
    dm._save(deck)
    console.print(f"[green]✓ Imported deck '{deck.name}' with {len(deck.cards)} card(s)[/green]")


# ---- export-deck -----------------------------------------------------------

@cli.command("export-deck")
@click.option("--deck", "-d", "deck_name", required=True, help="Deck name to export")
@click.option("--format", "-F", "fmt", type=click.Choice(["json", "csv"]),
              default="json", help="Output format")
@click.option("--output", "-o", type=click.Path(), default=None, help="Output file path")
@click.pass_context
def export_deck(ctx, deck_name, fmt, output):
    """Export a deck to a file."""
    dm: DeckManager = ctx.obj["deck_manager"]
    deck = dm.get_deck(deck_name)
    if deck is None:
        console.print(f"[red]Deck '{deck_name}' not found.[/red]")
        sys.exit(1)
    if output is None:
        safe = deck_name.lower().replace(" ", "_")[:30]
        output = f"{safe}.{fmt}"
    dm.export_deck(deck, output, fmt=fmt)
    console.print(f"[green]✓ Exported deck '{deck_name}' to {output}[/green]")


# ---- stats -----------------------------------------------------------------

@cli.command()
@click.option("--deck", "-d", "deck_name", required=True, help="Deck name")
@click.pass_context
def stats(ctx, deck_name):
    """Show review statistics for a deck."""
    dm: DeckManager = ctx.obj["deck_manager"]
    deck = dm.get_deck(deck_name)
    if deck is None:
        console.print(f"[red]Deck '{deck_name}' not found.[/red]")
        sys.exit(1)
    st = dm.get_stats(deck)
    table = Table(title=f"Stats: {deck_name}", show_lines=True)
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green", justify="right")
    table.add_row("Total cards", str(st.total_cards))
    table.add_row("Cards reviewed", str(st.cards_reviewed))
    table.add_row("Due for review", str(st.due_cards))
    for diff, cnt in sorted(st.cards_by_difficulty.items()):
        table.add_row(f"  {diff}", str(cnt))
    console.print(table)


# ---- helpers ---------------------------------------------------------------

def _display_table(cards_data: dict) -> None:
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


if __name__ == "__main__":
    cli()
