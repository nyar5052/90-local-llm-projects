#!/usr/bin/env python3
"""
Sentiment Analysis Dashboard - Analyze sentiment of text files.

Reads text files containing reviews or feedback, analyzes each entry's
sentiment using a local Gemma 4 LLM, and outputs results with confidence scores.
"""

import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress
from rich.markdown import Markdown

from common.llm_client import chat, check_ollama_running

console = Console()


def read_text_file(file_path: str) -> list[str]:
    """Read a text file and return non-empty lines."""
    if not os.path.exists(file_path):
        console.print(f"[red]Error:[/red] File '{file_path}' not found.")
        sys.exit(1)
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]
        if not lines:
            console.print("[red]Error:[/red] File is empty.")
            sys.exit(1)
        return lines
    except Exception as e:
        console.print(f"[red]Error reading file:[/red] {e}")
        sys.exit(1)


def analyze_sentiment(text: str) -> dict:
    """Analyze sentiment of a single text entry."""
    system_prompt = (
        "You are a sentiment analysis expert. Analyze the sentiment of the given text. "
        "Respond ONLY with valid JSON in this exact format:\n"
        '{"sentiment": "positive|negative|neutral", "confidence": 0.0-1.0, '
        '"key_phrases": ["phrase1", "phrase2"], "summary": "brief explanation"}\n'
        "Do not include any other text outside the JSON."
    )

    messages = [{"role": "user", "content": f"Analyze the sentiment of this text:\n\n{text}"}]
    response = chat(messages, system_prompt=system_prompt, temperature=0.2)

    try:
        start = response.find("{")
        end = response.rfind("}") + 1
        if start >= 0 and end > start:
            return json.loads(response[start:end])
    except (json.JSONDecodeError, ValueError):
        pass

    return {
        "sentiment": "neutral",
        "confidence": 0.5,
        "key_phrases": [],
        "summary": response[:200],
    }


def display_table(results: list[dict], texts: list[str]) -> None:
    """Display results as a rich table."""
    table = Table(title="Sentiment Analysis Results", show_lines=True)
    table.add_column("#", style="dim", width=4)
    table.add_column("Text", style="white", max_width=50, overflow="fold")
    table.add_column("Sentiment", justify="center", width=12)
    table.add_column("Confidence", justify="center", width=12)
    table.add_column("Summary", max_width=40, overflow="fold")

    sentiment_colors = {"positive": "green", "negative": "red", "neutral": "yellow"}

    for i, (result, text) in enumerate(zip(results, texts), 1):
        sentiment = result.get("sentiment", "neutral").lower()
        confidence = result.get("confidence", 0.5)
        summary = result.get("summary", "N/A")
        color = sentiment_colors.get(sentiment, "white")
        emoji = {"positive": "😊", "negative": "😞", "neutral": "😐"}.get(sentiment, "❓")

        table.add_row(
            str(i),
            text[:100] + ("..." if len(text) > 100 else ""),
            f"[{color}]{emoji} {sentiment.title()}[/{color}]",
            f"[bold]{confidence:.0%}[/bold]",
            summary[:80],
        )

    console.print(table)


def display_summary(results: list[dict]) -> None:
    """Display an overall summary of sentiment distribution."""
    total = len(results)
    counts = {"positive": 0, "negative": 0, "neutral": 0}
    total_confidence = 0.0

    for r in results:
        sentiment = r.get("sentiment", "neutral").lower()
        counts[sentiment] = counts.get(sentiment, 0) + 1
        total_confidence += r.get("confidence", 0.5)

    avg_conf = total_confidence / total if total > 0 else 0

    summary = (
        f"**Total Entries:** {total}\n\n"
        f"😊 **Positive:** {counts['positive']} ({counts['positive']/total:.0%})\n"
        f"😞 **Negative:** {counts['negative']} ({counts['negative']/total:.0%})\n"
        f"😐 **Neutral:** {counts['neutral']} ({counts['neutral']/total:.0%})\n\n"
        f"**Average Confidence:** {avg_conf:.0%}"
    )

    console.print(Panel(Markdown(summary), title="📊 Overall Summary", border_style="blue"))


def display_json(results: list[dict], texts: list[str]) -> None:
    """Display results as JSON."""
    output = []
    for text, result in zip(texts, results):
        output.append({"text": text, **result})
    console.print_json(json.dumps(output, indent=2))


@click.command()
@click.option("--file", "-f", required=True, help="Path to text file with reviews/feedback (one per line).")
@click.option("--format", "-fmt", "output_format", type=click.Choice(["table", "json", "summary"]),
              default="table", help="Output format.")
def main(file: str, output_format: str) -> None:
    """Sentiment Analysis Dashboard - Analyze sentiment of text files."""
    console.print(Panel("💬 [bold blue]Sentiment Analysis Dashboard[/bold blue]", expand=False))

    if not check_ollama_running():
        console.print("[red]Error:[/red] Ollama is not running. Start it with: ollama serve")
        sys.exit(1)

    texts = read_text_file(file)
    console.print(f"[green]✓[/green] Loaded [bold]{len(texts)}[/bold] text entries from [bold]{file}[/bold]\n")

    results = []
    with Progress(console=console) as progress:
        task = progress.add_task("[green]Analyzing sentiment...", total=len(texts))
        for text in texts:
            result = analyze_sentiment(text)
            results.append(result)
            progress.update(task, advance=1)

    console.print()

    if output_format == "table":
        display_table(results, texts)
        console.print()
        display_summary(results)
    elif output_format == "json":
        display_json(results, texts)
    elif output_format == "summary":
        display_summary(results)


if __name__ == "__main__":
    main()
