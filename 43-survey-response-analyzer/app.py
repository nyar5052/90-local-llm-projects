#!/usr/bin/env python3
"""
Survey Response Analyzer - Analyze survey free-text responses.

Groups themes, extracts insights, and generates comprehensive reports
from survey response data using a local Gemma 4 LLM.
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


def load_survey_data(file_path: str) -> list[dict]:
    """Load survey responses from a CSV file."""
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


def identify_text_columns(data: list[dict]) -> list[str]:
    """Identify columns likely containing free-text responses."""
    text_cols = []
    for col in data[0].keys():
        sample_values = [row.get(col, "") for row in data[:10]]
        avg_len = sum(len(str(v)) for v in sample_values) / max(len(sample_values), 1)
        if avg_len > 20:
            text_cols.append(col)
    return text_cols if text_cols else list(data[0].keys())


def extract_themes(responses: list[str]) -> dict:
    """Extract major themes from survey responses."""
    combined = "\n".join(f"- {r}" for r in responses[:50])

    system_prompt = (
        "You are a survey analysis expert. Analyze the survey responses and identify "
        "the major themes. Respond ONLY with valid JSON:\n"
        '{"themes": [{"name": "theme name", "count": estimated_count, '
        '"description": "brief description", "sentiment": "positive|negative|mixed"}], '
        '"total_responses": N}'
    )

    messages = [{"role": "user", "content": f"Analyze these {len(responses)} survey responses:\n\n{combined}"}]
    response = chat(messages, system_prompt=system_prompt, temperature=0.3, max_tokens=3000)

    try:
        start = response.find("{")
        end = response.rfind("}") + 1
        if start >= 0 and end > start:
            return json.loads(response[start:end])
    except (json.JSONDecodeError, ValueError):
        pass

    return {"themes": [], "total_responses": len(responses)}


def generate_insights(responses: list[str], themes: dict) -> str:
    """Generate detailed insights from the survey data."""
    combined = "\n".join(f"- {r}" for r in responses[:30])
    themes_text = json.dumps(themes.get("themes", []), indent=2)

    system_prompt = (
        "You are a survey analysis expert. Generate a detailed insights report "
        "based on survey responses and identified themes. Include actionable "
        "recommendations. Format with markdown headings and bullet points."
    )

    messages = [{"role": "user", "content": (
        f"Survey Responses Sample:\n{combined}\n\n"
        f"Identified Themes:\n{themes_text}\n\n"
        "Generate a comprehensive insights report with:\n"
        "1. Executive Summary\n"
        "2. Key Findings\n"
        "3. Theme Analysis\n"
        "4. Actionable Recommendations"
    )}]

    return chat(messages, system_prompt=system_prompt, temperature=0.4, max_tokens=4000)


def display_themes(themes: dict) -> None:
    """Display extracted themes in a table."""
    table = Table(title="Identified Themes", show_lines=True)
    table.add_column("#", style="dim", width=4)
    table.add_column("Theme", style="cyan bold", min_width=15)
    table.add_column("Responses", justify="center", width=12)
    table.add_column("Sentiment", justify="center", width=12)
    table.add_column("Description", max_width=50, overflow="fold")

    sentiment_colors = {"positive": "green", "negative": "red", "mixed": "yellow"}

    for i, theme in enumerate(themes.get("themes", []), 1):
        sentiment = theme.get("sentiment", "mixed")
        color = sentiment_colors.get(sentiment, "white")
        table.add_row(
            str(i),
            theme.get("name", "Unknown"),
            str(theme.get("count", "N/A")),
            f"[{color}]{sentiment.title()}[/{color}]",
            theme.get("description", "N/A"),
        )

    console.print(table)


@click.command()
@click.option("--file", "-f", required=True, help="Path to survey responses CSV file.")
@click.option("--report", "-r", type=click.Choice(["brief", "detailed"]),
              default="brief", help="Report detail level.")
@click.option("--column", "-c", default=None, help="Specific column to analyze.")
def main(file: str, report: str, column: str) -> None:
    """Survey Response Analyzer - Extract themes and insights from survey data."""
    console.print(Panel("📋 [bold blue]Survey Response Analyzer[/bold blue]", expand=False))

    if not check_ollama_running():
        console.print("[red]Error:[/red] Ollama is not running. Start it with: ollama serve")
        sys.exit(1)

    with console.status("[bold green]Loading survey data..."):
        data = load_survey_data(file)

    console.print(f"[green]✓[/green] Loaded [bold]{len(data)}[/bold] responses from [bold]{file}[/bold]\n")

    if column:
        text_cols = [column]
    else:
        text_cols = identify_text_columns(data)

    console.print(f"[bold]Analyzing columns:[/bold] {', '.join(text_cols)}\n")

    for col in text_cols:
        responses = [str(row.get(col, "")).strip() for row in data if row.get(col, "").strip()]
        if not responses:
            console.print(f"[yellow]Skipping empty column: {col}[/yellow]")
            continue

        console.print(f"\n[bold cyan]Column: {col}[/bold cyan] ({len(responses)} responses)")

        with console.status("[bold green]Extracting themes..."):
            themes = extract_themes(responses)

        display_themes(themes)

        if report == "detailed":
            console.print()
            with console.status("[bold green]Generating detailed insights..."):
                insights = generate_insights(responses, themes)
            console.print(Panel(Markdown(insights), title="📊 Detailed Insights", border_style="green"))


if __name__ == "__main__":
    main()
