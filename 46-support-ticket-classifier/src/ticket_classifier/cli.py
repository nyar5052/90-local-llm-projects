#!/usr/bin/env python3
"""
Support Ticket Classifier - CLI interface.

Provides Click-based commands for classifying tickets, viewing analytics,
and inspecting the priority queue.
"""

import sys

import click
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.progress import Progress
from rich.table import Table

from ticket_classifier.core import (
    build_priority_queue,
    check_ollama_running,
    classify_tickets_batch,
    compute_analytics,
    compute_sla_deadlines,
    find_text_column,
    load_config,
    load_tickets,
    route_to_team,
)

console = Console()

PRIORITY_COLORS = {"low": "green", "medium": "yellow", "high": "red", "critical": "bold red"}
PRIORITY_EMOJIS = {"low": "🟢", "medium": "🟡", "high": "🟠", "critical": "🔴"}


# ---------------------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------------------


def display_results(
    tickets: list[dict],
    classifications: list[dict],
    text_col: str,
) -> None:
    """Display classification results in a rich table."""
    table = Table(title="🎫 Ticket Classification Results", show_lines=True)
    table.add_column("#", style="dim", width=4)
    table.add_column("Ticket", max_width=40, overflow="fold")
    table.add_column("Category", style="cyan", width=14)
    table.add_column("Priority", justify="center", width=10)
    table.add_column("Confidence", justify="center", width=12)
    table.add_column("Team", style="magenta", width=18)
    table.add_column("Suggested Response", max_width=35, overflow="fold")

    config = load_config()
    routing_rules = config.get("team_routing", {})

    for i, (ticket, clf) in enumerate(zip(tickets, classifications), 1):
        priority = clf.get("priority", "medium").lower()
        color = PRIORITY_COLORS.get(priority, "white")
        emoji = PRIORITY_EMOJIS.get(priority, "⚪")
        confidence = clf.get("confidence", 0.5)
        team = route_to_team(clf, routing_rules)

        table.add_row(
            str(i),
            str(ticket.get(text_col, ""))[:80],
            clf.get("category", "N/A"),
            f"[{color}]{emoji} {priority.title()}[/{color}]",
            f"{confidence:.0%}",
            team,
            str(clf.get("suggested_response", "N/A"))[:60],
        )

    console.print(table)


def display_summary(classifications: list[dict], categories: list[str]) -> None:
    """Display a summary panel of classifications."""
    analytics = compute_analytics(classifications, categories)

    summary = f"**Total Tickets:** {analytics['total_tickets']}\n\n"
    summary += "**By Category:**\n"
    for cat, count in analytics["category_distribution"].items():
        summary += f"  • {cat}: {count}\n"
    summary += "\n**By Priority:**\n"
    for pri, count in analytics["priority_distribution"].items():
        emoji = PRIORITY_EMOJIS.get(pri, "⚪")
        summary += f"  {emoji} {pri.title()}: {count}\n"
    summary += f"\n**Average Confidence:** {analytics['avg_confidence']:.1%}\n"
    summary += f"**SLA Compliance:** {analytics['sla_compliance']:.1f}%\n"
    summary += f"**High/Critical Tickets:** {analytics['high_priority_count']}\n"

    console.print(Panel(Markdown(summary), title="📊 Classification Summary", border_style="blue"))


def display_priority_queue(queue: list[dict]) -> None:
    """Display the priority queue in a rich table."""
    table = Table(title="🚨 Priority Queue", show_lines=True)
    table.add_column("Pos", style="bold", width=4)
    table.add_column("Ticket", max_width=50, overflow="fold")
    table.add_column("Category", style="cyan", width=14)
    table.add_column("Priority", justify="center", width=10)
    table.add_column("Confidence", justify="center", width=12)
    table.add_column("Weight", justify="center", width=8)

    for item in queue:
        priority = item["priority"]
        color = PRIORITY_COLORS.get(priority, "white")
        emoji = PRIORITY_EMOJIS.get(priority, "⚪")

        table.add_row(
            str(item["position"]),
            item["ticket_text"],
            item["category"],
            f"[{color}]{emoji} {priority.title()}[/{color}]",
            f"{item['confidence']:.0%}",
            str(item["weight"]),
        )

    console.print(table)


# ---------------------------------------------------------------------------
# CLI commands
# ---------------------------------------------------------------------------


@click.group()
@click.option("--config", "-cfg", default="config.yaml", help="Path to config file.")
@click.pass_context
def main(ctx: click.Context, config: str) -> None:
    """🎫 Support Ticket Classifier - AI-powered ticket classification."""
    ctx.ensure_object(dict)
    ctx.obj["config"] = load_config(config)


@main.command()
@click.option("--file", "-f", required=True, help="Path to tickets CSV file.")
@click.option("--categories", "-c", default=None, help="Comma-separated categories (overrides config).")
@click.option("--column", "-col", default=None, help="Column name containing ticket text.")
@click.pass_context
def classify(ctx: click.Context, file: str, categories: str | None, column: str | None) -> None:
    """Classify support tickets from a CSV file."""
    config = ctx.obj["config"]

    if categories:
        category_list = [c.strip() for c in categories.split(",") if c.strip()]
    else:
        category_list = config.get("categories", ["general"])

    console.print(Panel("🎫 [bold blue]Support Ticket Classifier[/bold blue]", expand=False))

    if not check_ollama_running():
        console.print("[red]Error:[/red] Ollama is not running. Start it with: ollama serve")
        sys.exit(1)

    if not category_list:
        console.print("[red]Error:[/red] At least one category is required.")
        sys.exit(1)

    with console.status("[bold green]Loading tickets..."):
        tickets = load_tickets(file)

    text_col = column if column else find_text_column(tickets)
    console.print(f"[green]✓[/green] Loaded [bold]{len(tickets)}[/bold] tickets from [bold]{file}[/bold]")
    console.print(f"[bold]Categories:[/bold] {', '.join(category_list)}")
    console.print(f"[bold]Text column:[/bold] {text_col}\n")

    temperature = config.get("model", {}).get("temperature", 0.2)

    with Progress(console=console) as progress:
        task = progress.add_task("[green]Classifying tickets...", total=len(tickets))

        def on_progress(current: int, total: int) -> None:
            progress.update(task, completed=current)

        classifications = classify_tickets_batch(
            tickets, category_list, text_col,
            temperature=temperature, on_progress=on_progress,
        )

    console.print()
    display_results(tickets, classifications, text_col)
    console.print()
    display_summary(classifications, category_list)


@main.command()
@click.option("--file", "-f", required=True, help="Path to tickets CSV file.")
@click.option("--categories", "-c", default=None, help="Comma-separated categories.")
@click.option("--column", "-col", default=None, help="Column name containing ticket text.")
@click.pass_context
def analytics(ctx: click.Context, file: str, categories: str | None, column: str | None) -> None:
    """Show analytics summary for classified tickets."""
    config = ctx.obj["config"]
    category_list = (
        [c.strip() for c in categories.split(",") if c.strip()]
        if categories
        else config.get("categories", ["general"])
    )

    if not check_ollama_running():
        console.print("[red]Error:[/red] Ollama is not running.")
        sys.exit(1)

    tickets = load_tickets(file)
    text_col = column if column else find_text_column(tickets)
    classifications = classify_tickets_batch(tickets, category_list, text_col)
    display_summary(classifications, category_list)


@main.command(name="priority-queue")
@click.option("--file", "-f", required=True, help="Path to tickets CSV file.")
@click.option("--categories", "-c", default=None, help="Comma-separated categories.")
@click.option("--column", "-col", default=None, help="Column name containing ticket text.")
@click.pass_context
def priority_queue(ctx: click.Context, file: str, categories: str | None, column: str | None) -> None:
    """Show tickets sorted by priority (priority queue)."""
    config = ctx.obj["config"]
    category_list = (
        [c.strip() for c in categories.split(",") if c.strip()]
        if categories
        else config.get("categories", ["general"])
    )

    if not check_ollama_running():
        console.print("[red]Error:[/red] Ollama is not running.")
        sys.exit(1)

    tickets = load_tickets(file)
    text_col = column if column else find_text_column(tickets)
    classifications = classify_tickets_batch(tickets, category_list, text_col)

    queue = build_priority_queue(
        tickets, classifications, text_col,
        priority_weights=config.get("priority_weights"),
    )
    display_priority_queue(queue)

    # Show SLA info
    sla_info = compute_sla_deadlines(classifications, config.get("sla_hours"))
    console.print(Panel(
        f"[bold]SLA Deadlines Computed:[/bold] {len(sla_info)} tickets tracked",
        title="⏱️  SLA Tracking",
        border_style="yellow",
    ))


if __name__ == "__main__":
    main()
