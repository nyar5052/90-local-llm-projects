#!/usr/bin/env python3
"""Reading List Manager - Manages reading list with AI book summaries and recommendations."""

import sys
import os
import json
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from common.llm_client import chat, generate, check_ollama_running

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown

console = Console()
BOOKS_FILE = os.path.join(os.path.dirname(__file__), "reading_list.json")


def load_books() -> dict:
    """Load reading list from JSON file."""
    if os.path.exists(BOOKS_FILE):
        try:
            with open(BOOKS_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {"books": []}
    return {"books": []}


def save_books(data: dict) -> None:
    """Save reading list to JSON file."""
    with open(BOOKS_FILE, 'w') as f:
        json.dump(data, f, indent=2)


def add_book(title: str, author: str, genre: str = "", status: str = "to-read", rating: int = 0, notes: str = "") -> dict:
    """Add a book to the reading list."""
    data = load_books()
    book = {
        "id": len(data["books"]) + 1,
        "title": title,
        "author": author,
        "genre": genre,
        "status": status,
        "rating": rating,
        "notes": notes,
        "added": datetime.now().isoformat(),
    }
    data["books"].append(book)
    save_books(data)
    return book


def get_summary(title: str, author: str) -> str:
    """Get an AI-generated book summary."""
    prompt = f"""Provide a comprehensive summary of the book "{title}" by {author}.

Include:
1. **Overview**: Brief synopsis (2-3 sentences)
2. **Key Themes**: Main themes explored
3. **Key Takeaways**: Most important lessons or insights
4. **Who Should Read It**: Target audience
5. **Similar Books**: 3 similar book recommendations

Format in markdown."""

    return generate(
        prompt=prompt,
        system_prompt="You are a well-read literary assistant who provides insightful book summaries.",
        temperature=0.6,
    )


def get_recommendations(genre: str = "", books: list[dict] = None) -> str:
    """Get AI book recommendations based on reading history."""
    books_text = ""
    if books:
        books_text = "\n".join(
            f"- \"{b['title']}\" by {b['author']} (Genre: {b.get('genre', 'N/A')}, Rating: {b.get('rating', 'N/A')}/5)"
            for b in books
        )

    prompt = f"""Based on this reading history:
{books_text or 'No reading history available.'}

{f'Genre preference: {genre}' if genre else ''}

Recommend 5 books with:
1. **Title and Author**: Full book details
2. **Why This Book**: Why it matches the reader's taste
3. **Genre**: Book category
4. **Difficulty Level**: Easy/Medium/Advanced read
5. **Key Insight**: What makes this book special

Format as a numbered list in markdown."""

    return generate(
        prompt=prompt,
        system_prompt="You are an expert book recommender who understands reader preferences and can suggest perfect next reads.",
        temperature=0.7,
    )


def analyze_reading_habits(books: list[dict]) -> str:
    """Analyze reading habits and patterns."""
    books_text = json.dumps(books, indent=2)
    prompt = f"""Analyze these reading habits:

{books_text}

Provide:
1. **Reading Profile**: What kind of reader is this person?
2. **Genre Distribution**: Favorite genres and balance
3. **Rating Patterns**: What they tend to rate highly
4. **Reading Pace**: Observations about reading speed
5. **Suggestions**: How to diversify or deepen reading

Format in markdown."""

    return generate(
        prompt=prompt,
        system_prompt="You are a reading habit analyst.",
        temperature=0.5,
    )


def display_books(books: list[dict]) -> None:
    """Display reading list in a formatted table."""
    table = Table(title="📚 Reading List", show_lines=True)
    table.add_column("ID", style="cyan", width=5)
    table.add_column("Title", style="white", min_width=20)
    table.add_column("Author", style="green", min_width=15)
    table.add_column("Genre", style="blue", min_width=12)
    table.add_column("Status", style="yellow", min_width=10)
    table.add_column("Rating", style="magenta", width=8)

    status_emoji = {"to-read": "📋", "reading": "📖", "completed": "✅", "dropped": "❌"}

    for book in books:
        status = book.get("status", "to-read")
        emoji = status_emoji.get(status, "📋")
        rating = "⭐" * book.get("rating", 0) if book.get("rating") else "-"
        table.add_row(
            str(book["id"]),
            book["title"],
            book["author"],
            book.get("genre", "-"),
            f"{emoji} {status}",
            rating,
        )

    console.print(table)


@click.group()
def cli():
    """Reading List Manager - AI-powered book management and recommendations."""
    pass


@cli.command()
@click.option('--title', '-t', required=True, help='Book title')
@click.option('--author', '-a', required=True, help='Book author')
@click.option('--genre', '-g', default='', help='Book genre')
@click.option('--status', '-s', default='to-read',
              type=click.Choice(['to-read', 'reading', 'completed', 'dropped']),
              help='Reading status')
@click.option('--rating', '-r', default=0, type=int, help='Rating 1-5')
def add(title, author, genre, status, rating):
    """Add a book to your reading list."""
    console.print(Panel("[bold blue]📚 Reading List Manager[/bold blue]", border_style="blue"))
    book = add_book(title, author, genre, status, rating)
    console.print(f"[green]✅ Added:[/green] \"{book['title']}\" by {book['author']}")
    if genre:
        console.print(f"[dim]Genre: {genre} | Status: {status}[/dim]")


@cli.command()
@click.option('--genre', '-g', default='', help='Preferred genre for recommendations')
def recommend(genre):
    """Get AI book recommendations."""
    console.print(Panel("[bold blue]📚 Reading List Manager[/bold blue]\n[dim]Getting recommendations...[/dim]", border_style="blue"))

    if not check_ollama_running():
        console.print("[red]Error:[/red] Ollama is not running. Start it with: [bold]ollama serve[/bold]")
        sys.exit(1)

    data = load_books()
    with console.status("[bold green]Finding perfect books for you..."):
        result = get_recommendations(genre, data["books"])
    console.print(Panel(Markdown(result), title="📖 Recommended Books", border_style="green"))


@cli.command(name='summary')
@click.option('--title', '-t', required=True, help='Book title')
@click.option('--author', '-a', required=True, help='Book author')
def book_summary(title, author):
    """Get an AI-generated book summary."""
    console.print(Panel("[bold blue]📚 Reading List Manager[/bold blue]", border_style="blue"))

    if not check_ollama_running():
        console.print("[red]Error:[/red] Ollama is not running. Start it with: [bold]ollama serve[/bold]")
        sys.exit(1)

    with console.status(f"[bold green]Summarizing '{title}'..."):
        result = get_summary(title, author)
    console.print(Panel(Markdown(result), title=f"📖 {title}", border_style="cyan"))


@cli.command(name='list')
@click.option('--status', '-s', default=None,
              type=click.Choice(['to-read', 'reading', 'completed', 'dropped']),
              help='Filter by status')
def list_books(status):
    """List all books in your reading list."""
    console.print(Panel("[bold blue]📚 Reading List Manager[/bold blue]", border_style="blue"))
    data = load_books()
    books = data["books"]

    if status:
        books = [b for b in books if b.get("status") == status]

    if not books:
        console.print("[yellow]No books found. Add some with: python app.py add --title '...' --author '...'[/yellow]")
        return

    display_books(books)
    console.print(f"\n[dim]Total books: {len(books)}[/dim]")


@cli.command()
def analyze():
    """Analyze your reading habits."""
    console.print(Panel("[bold blue]📚 Reading List Manager[/bold blue]", border_style="blue"))

    if not check_ollama_running():
        console.print("[red]Error:[/red] Ollama is not running.")
        sys.exit(1)

    data = load_books()
    if not data["books"]:
        console.print("[yellow]No books to analyze. Add some first![/yellow]")
        return

    with console.status("[bold green]Analyzing reading habits..."):
        result = analyze_reading_habits(data["books"])
    console.print(Panel(Markdown(result), title="📊 Reading Analysis", border_style="magenta"))


if __name__ == '__main__':
    cli()
