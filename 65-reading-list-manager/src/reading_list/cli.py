#!/usr/bin/env python3
"""Reading List Manager - Click CLI interface."""

import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from common.llm_client import check_ollama_running  # noqa: E402

import click  # noqa: E402
from rich.console import Console  # noqa: E402
from rich.panel import Panel  # noqa: E402
from rich.markdown import Markdown  # noqa: E402

from reading_list.core import (  # noqa: E402
    load_books,
    add_book,
    update_progress,
    rate_book,
    get_genre_stats,
    get_summary,
    get_recommendations,
    analyze_reading_habits,
    display_books,
    set_reading_goal,
    check_goal_progress,
    STATUS_EMOJI,
)

console = Console()

VALID_STATUSES = list(STATUS_EMOJI.keys())


def _banner():
    console.print(Panel("[bold blue]📚 Reading List Manager[/bold blue]", border_style="blue"))


def _check_llm():
    if not check_ollama_running():
        console.print("[red]Error:[/red] Ollama is not running. Start it with: [bold]ollama serve[/bold]")
        sys.exit(1)


# ---------------------------------------------------------------------------
# CLI group
# ---------------------------------------------------------------------------


@click.group()
def cli():
    """📚 Reading List Manager - AI-powered book management and recommendations."""
    pass


# ---------------------------------------------------------------------------
# Original commands
# ---------------------------------------------------------------------------


@cli.command()
@click.option('--title', '-t', required=True, help='Book title')
@click.option('--author', '-a', required=True, help='Book author')
@click.option('--genre', '-g', default='', help='Book genre')
@click.option('--status', '-s', default='to-read', type=click.Choice(VALID_STATUSES), help='Reading status')
@click.option('--rating', '-r', default=0, type=int, help='Rating 1-5')
@click.option('--pages', '-p', default=0, type=int, help='Total pages')
def add(title, author, genre, status, rating, pages):
    """Add a book to your reading list."""
    _banner()
    book = add_book(title, author, genre, status, rating, pages=pages)
    console.print(f"[green]✅ Added:[/green] \"{book['title']}\" by {book['author']}")
    if genre:
        console.print(f"[dim]Genre: {genre} | Status: {status}[/dim]")


@cli.command()
@click.option('--genre', '-g', default='', help='Preferred genre for recommendations')
def recommend(genre):
    """Get AI book recommendations."""
    _banner()
    _check_llm()
    data = load_books()
    with console.status("[bold green]Finding perfect books for you..."):
        result = get_recommendations(genre, data["books"])
    console.print(Panel(Markdown(result), title="📖 Recommended Books", border_style="green"))


@cli.command(name='summary')
@click.option('--title', '-t', required=True, help='Book title')
@click.option('--author', '-a', required=True, help='Book author')
def book_summary(title, author):
    """Get an AI-generated book summary."""
    _banner()
    _check_llm()
    with console.status(f"[bold green]Summarizing '{title}'..."):
        result = get_summary(title, author)
    console.print(Panel(Markdown(result), title=f"📖 {title}", border_style="cyan"))


@cli.command(name='list')
@click.option('--status', '-s', default=None, type=click.Choice(VALID_STATUSES), help='Filter by status')
def list_books(status):
    """List all books in your reading list."""
    _banner()
    data = load_books()
    books = data["books"]
    if status:
        books = [b for b in books if b.get("status") == status]
    if not books:
        console.print("[yellow]No books found. Add some with: reading-list add -t '...' -a '...'[/yellow]")
        return
    display_books(books)
    console.print(f"\n[dim]Total books: {len(books)}[/dim]")


@cli.command()
def analyze():
    """Analyze your reading habits with AI."""
    _banner()
    _check_llm()
    data = load_books()
    if not data["books"]:
        console.print("[yellow]No books to analyze. Add some first![/yellow]")
        return
    with console.status("[bold green]Analyzing reading habits..."):
        result = analyze_reading_habits(data["books"])
    console.print(Panel(Markdown(result), title="📊 Reading Analysis", border_style="magenta"))


# ---------------------------------------------------------------------------
# New commands
# ---------------------------------------------------------------------------


@cli.command()
@click.option('--book-id', '-b', required=True, type=int, help='Book ID')
@click.option('--pages', '-p', required=True, type=int, help='Pages read so far')
def progress(book_id, pages):
    """Update reading progress for a book."""
    _banner()
    book = update_progress(book_id, pages)
    if book is None:
        console.print(f"[red]Book with ID {book_id} not found.[/red]")
        return
    emoji = STATUS_EMOJI.get(book["status"], "📋")
    console.print(
        f"[green]📖 Progress updated:[/green] \"{book['title']}\" — "
        f"{book['pages_read']}/{book.get('pages', '?')} pages ({book['progress_percent']:.0f}%) {emoji}"
    )


@cli.command()
@click.option('--book-id', '-b', required=True, type=int, help='Book ID')
@click.option('--rating', '-r', required=True, type=int, help='Rating 1-5')
@click.option('--review', default='', help='Optional review text')
def rate(book_id, rating, review):
    """Rate a book and optionally leave a review."""
    _banner()
    try:
        book = rate_book(book_id, rating, review)
    except ValueError as e:
        console.print(f"[red]{e}[/red]")
        return
    if book is None:
        console.print(f"[red]Book with ID {book_id} not found.[/red]")
        return
    stars = "⭐" * rating
    console.print(f"[green]Rated:[/green] \"{book['title']}\" — {stars}")
    if review:
        console.print(f"[dim]Review: {review}[/dim]")


@cli.command()
def stats():
    """Show genre statistics for your library."""
    _banner()
    data = load_books()
    if not data["books"]:
        console.print("[yellow]No books to analyze.[/yellow]")
        return
    genre_stats = get_genre_stats(data["books"])
    from rich.table import Table

    table = Table(title="📊 Genre Statistics", show_lines=True)
    table.add_column("Genre", style="blue")
    table.add_column("Books", style="cyan", justify="right")
    table.add_column("Avg Rating", style="magenta", justify="right")

    for genre, info in sorted(genre_stats.items()):
        avg = f"{info['avg_rating']:.1f} ⭐" if info["avg_rating"] else "-"
        table.add_row(genre, str(info["count"]), avg)

    console.print(table)


@cli.command()
@click.option('--year', '-y', default=None, type=int, help='Goal year (default: current)')
@click.option('--target', '-t', default=None, type=int, help='Number of books to read')
def goal(year, target):
    """Set or check your yearly reading goal."""
    _banner()
    year = year or datetime.now().year

    if target is not None:
        set_reading_goal(year, target)
        console.print(f"[green]🎯 Goal set:[/green] Read {target} books in {year}")
        return

    data = load_books()
    progress_info = check_goal_progress(year, data["books"])
    pct = progress_info["percent"]
    bar_filled = int(pct / 5)
    bar = "█" * bar_filled + "░" * (20 - bar_filled)

    console.print(f"\n[bold]🎯 Reading Goal {year}[/bold]")
    console.print(f"  Progress: [{bar}] {pct:.1f}%")
    console.print(f"  Completed: {progress_info['completed']} / {progress_info['target']}")
    console.print(f"  Remaining: {progress_info['remaining']} books")
    if progress_info["days_left"] > 0:
        console.print(f"  Days left: {progress_info['days_left']}")
        console.print(f"  Pace needed: ~{progress_info['books_per_month_needed']:.1f} books/month")


if __name__ == '__main__':
    cli()
