#!/usr/bin/env python3
"""
History Timeline Generator — Generates historical timelines for events and periods.
Includes key dates, figures, and significance.
"""

import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from common.llm_client import chat, check_ollama_running

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

SYSTEM_PROMPT = """You are an expert historian creating detailed timelines.
Return the timeline in valid JSON format:

{
  "title": "Timeline Title",
  "period": "Start Year - End Year",
  "overview": "Brief overview paragraph",
  "events": [
    {
      "date": "Date or year",
      "event": "Event name/title",
      "description": "What happened",
      "key_figures": ["Person 1", "Person 2"],
      "significance": "Why this matters",
      "category": "political|military|social|economic|cultural|scientific"
    }
  ],
  "key_themes": ["Theme 1", "Theme 2"],
  "legacy": "Long-term impact and legacy",
  "further_reading": ["Book or resource 1"]
}

Return ONLY the JSON, no other text."""

DETAIL_LEVELS = {
    "brief": "Include 5-8 major events with short descriptions.",
    "medium": "Include 10-15 events with moderate detail.",
    "detailed": "Include 15-25 events with comprehensive descriptions, key figures, and significance."
}


def generate_timeline(topic: str, detail: str, start_year: str = "", end_year: str = "") -> dict:
    """Generate a historical timeline using the LLM."""
    detail_instruction = DETAIL_LEVELS.get(detail, DETAIL_LEVELS["medium"])
    prompt = f"Create a historical timeline about '{topic}'.\n{detail_instruction}\n"
    if start_year:
        prompt += f"Start from: {start_year}\n"
    if end_year:
        prompt += f"End at: {end_year}\n"
    prompt += "Order events chronologically. Include key figures and significance for each event."

    response = chat(
        messages=[{"role": "user", "content": prompt}],
        system_prompt=SYSTEM_PROMPT,
        temperature=0.5,
        max_tokens=8192,
    )

    try:
        text = response.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1].rsplit("```", 1)[0]
        return json.loads(text)
    except json.JSONDecodeError:
        console.print("[red]Error: Could not parse timeline response.[/red]")
        sys.exit(1)


def display_timeline(data: dict) -> None:
    """Display the timeline in a rich format."""
    # Header
    console.print(Panel(
        f"[bold]{data.get('title', 'Timeline')}[/bold]\n"
        f"Period: {data.get('period', 'N/A')}\n\n"
        f"{data.get('overview', '')}",
        title="📜 Historical Timeline",
        border_style="blue"
    ))

    # Events table
    table = Table(title="Timeline Events", show_lines=True, expand=True)
    table.add_column("Date", style="bold cyan", width=15)
    table.add_column("Event", style="bold", width=25)
    table.add_column("Description", ratio=2)
    table.add_column("Key Figures", style="yellow", width=20)
    table.add_column("Significance", style="green", ratio=1)

    category_colors = {
        "political": "blue", "military": "red", "social": "magenta",
        "economic": "yellow", "cultural": "cyan", "scientific": "green"
    }

    for event in data.get("events", []):
        cat = event.get("category", "")
        color = category_colors.get(cat, "white")
        figures = ", ".join(event.get("key_figures", []))
        table.add_row(
            event.get("date", ""),
            f"[{color}]{event.get('event', '')}[/{color}]",
            event.get("description", ""),
            figures,
            event.get("significance", "")
        )

    console.print(table)

    # Key Themes
    if data.get("key_themes"):
        console.print("\n[bold cyan]🔑 Key Themes:[/bold cyan]")
        for t in data["key_themes"]:
            console.print(f"  • {t}")

    # Legacy
    if data.get("legacy"):
        console.print(Panel(data["legacy"], title="🏛️ Legacy", border_style="yellow"))

    # Further Reading
    if data.get("further_reading"):
        console.print("\n[bold green]📚 Further Reading:[/bold green]")
        for r in data["further_reading"]:
            console.print(f"  • {r}")


@click.command()
@click.option("--topic", "-t", required=True,
              help="Historical topic (e.g., 'American Civil War')")
@click.option("--detail", "-d", type=click.Choice(["brief", "medium", "detailed"]),
              default="medium", help="Detail level (default: medium)")
@click.option("--start", "-s", default="", help="Start year (optional)")
@click.option("--end", "-e", default="", help="End year (optional)")
@click.option("--output", "-o", type=click.Path(),
              help="Save timeline to JSON file")
def main(topic, detail, start, end, output):
    """Generate historical timelines using a local LLM."""
    console.print(Panel("[bold blue]📜 History Timeline Generator[/bold blue]",
                        subtitle="Powered by Local LLM"))

    if not check_ollama_running():
        console.print("[red]Error: Ollama is not running. Start with: ollama serve[/red]")
        sys.exit(1)

    console.print(f"[cyan]Generating {detail} timeline for '{topic}'...[/cyan]")

    with console.status("[bold green]Researching history..."):
        data = generate_timeline(topic, detail, start, end)

    display_timeline(data)

    if output:
        with open(output, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        console.print(f"\n[green]✓ Timeline saved to {output}[/green]")


if __name__ == "__main__":
    main()
