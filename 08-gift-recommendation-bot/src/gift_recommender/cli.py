"""Click CLI interface for Gift Recommendation Bot."""

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
    generate_recommendations, get_gift_details, compare_prices,
    add_to_wishlist, get_wishlist, mark_purchased,
    add_occasion, get_upcoming_occasions, check_ollama_running,
    OCCASIONS, RELATIONSHIPS,
)
from .utils import setup_logging

logger = logging.getLogger(__name__)
console = Console()


@click.group()
@click.option("--log-level", default="WARNING", help="Logging level")
def cli(log_level: str):
    """🎁 Gift Recommendation Bot - Find the perfect gift with AI."""
    setup_logging(log_level)


@cli.command()
@click.option("--occasion", type=click.Choice(OCCASIONS, case_sensitive=False), required=True, help="Gift occasion")
@click.option("--relationship", type=click.Choice(RELATIONSHIPS, case_sensitive=False), default="friend")
@click.option("--budget", type=click.IntRange(5, 10000), default=50, help="Budget in dollars")
@click.option("--interests", type=str, default=None, help="Recipient interests")
@click.option("--age", type=str, default=None, help="Recipient's age")
def recommend(occasion: str, relationship: str, budget: int, interests: str | None, age: str | None):
    """Get personalized gift recommendations."""
    console.print(Panel.fit("[bold cyan]🎁 Gift Recommendation Bot[/bold cyan]\nFind the perfect gift with AI",
                            border_style="cyan"))

    if not check_ollama_running():
        console.print("[red]❌ Ollama is not running. Start it with: ollama serve[/red]")
        sys.exit(1)

    table = Table(title="Gift Search Parameters", border_style="cyan")
    table.add_column("Parameter", style="bold")
    table.add_column("Value")
    table.add_row("Occasion", occasion.replace("-", " ").title())
    table.add_row("Recipient", relationship.capitalize())
    table.add_row("Budget", f"${budget}")
    if interests:
        table.add_row("Interests", interests)
    if age:
        table.add_row("Age", age)
    console.print(table)
    console.print()

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
        progress.add_task("Finding perfect gifts...", total=None)
        recommendations = generate_recommendations(occasion, relationship, budget, interests, age)

    console.print(Panel(Markdown(recommendations), title="[bold green]🎁 Gift Recommendations[/bold green]",
                        border_style="green"))

    console.print("\n[dim]Commands: type gift name for details, '/compare <gift>' for prices, or 'quit'[/dim]\n")

    while True:
        try:
            user_input = Prompt.ask("[bold yellow]🔍 More about[/bold yellow]")
        except (KeyboardInterrupt, EOFError):
            break

        if user_input.lower().strip() in ("quit", "exit", "q"):
            break
        if not user_input.strip():
            continue

        if user_input.startswith("/compare "):
            gift = user_input[9:].strip()
            with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
                progress.add_task("Comparing prices...", total=None)
                result = compare_prices(gift)
            console.print(Panel(Markdown(result), title=f"[bold green]💰 Price Comparison: {gift}[/bold green]",
                                border_style="green"))
        else:
            with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
                progress.add_task("Getting details...", total=None)
                details = get_gift_details(user_input, budget)
            console.print(Panel(Markdown(details), title=f"[bold green]🎁 {user_input}[/bold green]",
                                border_style="green"))
        console.print()

    console.print("[bold cyan]🎁 Happy gifting! Goodbye![/bold cyan]")


@cli.command()
@click.option("--person", required=True, help="Person's name")
@click.option("--gift", required=True, help="Gift item")
@click.option("--price", default="", help="Estimated price")
@click.option("--occasion", default="", help="Occasion")
def wishlist_add(person: str, gift: str, price: str, occasion: str):
    """Add an item to someone's wishlist."""
    item = add_to_wishlist(person, gift, price, occasion)
    console.print(f"[green]✅ Added to {person}'s wishlist: {gift}[/green]")


@cli.command()
@click.option("--person", required=True, help="Person's name")
def wishlist_show(person: str):
    """Show a person's wishlist."""
    items = get_wishlist(person)
    if not items:
        console.print(f"[yellow]No wishlist items for {person}.[/yellow]")
        return
    table = Table(title=f"{person}'s Wishlist", border_style="cyan")
    table.add_column("#", width=4)
    table.add_column("Gift", width=25)
    table.add_column("Price", width=10)
    table.add_column("Status", width=12)
    for item in items:
        status = "✅ Purchased" if item.get("purchased") else "⬜ Pending"
        table.add_row(str(item["id"]), item["gift"], item.get("price", ""), status)
    console.print(table)


@cli.command()
@click.option("--person", required=True, help="Person's name")
@click.option("--occasion", required=True, help="Occasion type")
@click.option("--date", required=True, help="Date (YYYY-MM-DD)")
def calendar_add(person: str, occasion: str, date: str):
    """Add an occasion to the calendar."""
    entry = add_occasion(person, occasion, date)
    console.print(f"[green]✅ Added: {person}'s {occasion} on {date}[/green]")


@cli.command()
@click.option("--days", type=int, default=30, help="Days to look ahead")
def calendar_show(days: int):
    """Show upcoming occasions."""
    upcoming = get_upcoming_occasions(days)
    if not upcoming:
        console.print(f"[yellow]No occasions in the next {days} days.[/yellow]")
        return
    table = Table(title=f"Upcoming Occasions (next {days} days)", border_style="cyan")
    table.add_column("Person", width=15)
    table.add_column("Occasion", width=15)
    table.add_column("Date", width=12)
    table.add_column("Days Until", width=10)
    for o in upcoming:
        table.add_row(o["person"], o["occasion"], o["date"], str(o.get("days_until", "?")))
    console.print(table)


def main():
    """Entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
