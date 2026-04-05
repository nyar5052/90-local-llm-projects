#!/usr/bin/env python3
"""
Support Ticket Classifier - Classify support tickets by category and priority.

Reads support tickets from CSV, classifies them by category and priority,
and suggests initial responses using a local Gemma 4 LLM.
"""

import sys
import os
import csv
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown
from rich.progress import Progress

from common.llm_client import chat, check_ollama_running

console = Console()


def load_tickets(file_path: str) -> list[dict]:
    """Load support tickets from a CSV file."""
    if not os.path.exists(file_path):
        console.print(f"[red]Error:[/red] File '{file_path}' not found.")
        sys.exit(1)
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        if not rows:
            console.print("[red]Error:[/red] CSV file is empty.")
            sys.exit(1)
        return rows
    except Exception as e:
        console.print(f"[red]Error reading CSV:[/red] {e}")
        sys.exit(1)


def find_text_column(data: list[dict]) -> str:
    """Identify the column most likely containing ticket descriptions."""
    candidates = ["description", "subject", "message", "text", "content", "body", "issue", "summary"]
    for col in data[0].keys():
        if col.lower() in candidates:
            return col
    # Fallback: use the column with the longest average text
    best_col = max(data[0].keys(), key=lambda c: sum(len(str(row.get(c, ""))) for row in data[:5]))
    return best_col


def classify_ticket(ticket_text: str, categories: list[str]) -> dict:
    """Classify a single support ticket."""
    categories_text = ", ".join(categories)

    system_prompt = (
        "You are a support ticket classifier. Classify the ticket into one of the "
        f"provided categories and assign a priority level. Categories: {categories_text}\n"
        "Respond ONLY with valid JSON:\n"
        '{"category": "one of the categories", "priority": "low|medium|high|critical", '
        '"confidence": 0.0-1.0, "suggested_response": "brief initial response to customer"}'
    )

    messages = [{"role": "user", "content": f"Classify this support ticket:\n\n{ticket_text}"}]
    response = chat(messages, system_prompt=system_prompt, temperature=0.2)

    try:
        start = response.find("{")
        end = response.rfind("}") + 1
        if start >= 0 and end > start:
            result = json.loads(response[start:end])
            if result.get("category", "").lower() not in [c.lower() for c in categories]:
                result["category"] = categories[0]
            return result
    except (json.JSONDecodeError, ValueError):
        pass

    return {
        "category": categories[0],
        "priority": "medium",
        "confidence": 0.5,
        "suggested_response": "We have received your ticket and will respond shortly.",
    }


def display_results(tickets: list[dict], classifications: list[dict], text_col: str) -> None:
    """Display classification results in a table."""
    table = Table(title="🎫 Ticket Classification Results", show_lines=True)
    table.add_column("#", style="dim", width=4)
    table.add_column("Ticket", max_width=40, overflow="fold")
    table.add_column("Category", style="cyan", width=14)
    table.add_column("Priority", justify="center", width=10)
    table.add_column("Confidence", justify="center", width=12)
    table.add_column("Suggested Response", max_width=35, overflow="fold")

    priority_colors = {"low": "green", "medium": "yellow", "high": "red", "critical": "bold red"}
    priority_emojis = {"low": "🟢", "medium": "🟡", "high": "🟠", "critical": "🔴"}

    for i, (ticket, clf) in enumerate(zip(tickets, classifications), 1):
        priority = clf.get("priority", "medium").lower()
        color = priority_colors.get(priority, "white")
        emoji = priority_emojis.get(priority, "⚪")
        confidence = clf.get("confidence", 0.5)

        table.add_row(
            str(i),
            str(ticket.get(text_col, ""))[:80],
            clf.get("category", "N/A"),
            f"[{color}]{emoji} {priority.title()}[/{color}]",
            f"{confidence:.0%}",
            str(clf.get("suggested_response", "N/A"))[:60],
        )

    console.print(table)


def display_summary(classifications: list[dict], categories: list[str]) -> None:
    """Display a summary of classifications."""
    cat_counts = {c: 0 for c in categories}
    priority_counts = {"low": 0, "medium": 0, "high": 0, "critical": 0}

    for clf in classifications:
        cat = clf.get("category", "").lower()
        for c in categories:
            if c.lower() == cat:
                cat_counts[c] += 1
                break
        pri = clf.get("priority", "medium").lower()
        priority_counts[pri] = priority_counts.get(pri, 0) + 1

    summary = f"**Total Tickets:** {len(classifications)}\n\n"
    summary += "**By Category:**\n"
    for cat, count in cat_counts.items():
        summary += f"  • {cat}: {count}\n"
    summary += "\n**By Priority:**\n"
    for pri, count in priority_counts.items():
        emoji = {"low": "🟢", "medium": "🟡", "high": "🟠", "critical": "🔴"}.get(pri, "⚪")
        summary += f"  {emoji} {pri.title()}: {count}\n"

    console.print(Panel(Markdown(summary), title="📊 Classification Summary", border_style="blue"))


@click.command()
@click.option("--file", "-f", required=True, help="Path to tickets CSV file.")
@click.option("--categories", "-c", required=True, help="Comma-separated category names.")
@click.option("--column", "-col", default=None, help="Column name containing ticket text.")
def main(file: str, categories: str, column: str) -> None:
    """Support Ticket Classifier - Classify tickets by category and priority."""
    category_list = [c.strip() for c in categories.split(",") if c.strip()]

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

    classifications = []
    with Progress(console=console) as progress:
        task = progress.add_task("[green]Classifying tickets...", total=len(tickets))
        for ticket in tickets:
            text = str(ticket.get(text_col, ""))
            clf = classify_ticket(text, category_list)
            classifications.append(clf)
            progress.update(task, advance=1)

    console.print()
    display_results(tickets, classifications, text_col)
    console.print()
    display_summary(classifications, category_list)


if __name__ == "__main__":
    main()
