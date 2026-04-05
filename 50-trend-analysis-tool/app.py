#!/usr/bin/env python3
"""
Trend Analysis Tool - Analyze trends from text data.

Reads articles and reports from a directory, identifies emerging topics,
sentiment shifts, and generates trend analysis using a local Gemma 4 LLM.
"""

import sys
import os
import json
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown
from rich.progress import Progress

from common.llm_client import chat, check_ollama_running

console = Console()


def load_text_files(directory: str) -> list[dict]:
    """Load text files from a directory."""
    dir_path = Path(directory)
    if not dir_path.exists():
        console.print(f"[red]Error:[/red] Directory '{directory}' not found.")
        sys.exit(1)

    documents = []
    extensions = {".txt", ".md", ".text", ".csv", ".log"}
    for file_path in sorted(dir_path.iterdir()):
        if file_path.is_file() and file_path.suffix.lower() in extensions:
            try:
                content = file_path.read_text(encoding="utf-8")
                if content.strip():
                    documents.append({
                        "filename": file_path.name,
                        "content": content,
                        "size": len(content),
                        "modified": os.path.getmtime(str(file_path)),
                    })
            except (UnicodeDecodeError, PermissionError):
                continue

    if not documents:
        console.print(f"[red]Error:[/red] No readable text files found in '{directory}'.")
        sys.exit(1)

    return documents


def extract_topics(documents: list[dict]) -> dict:
    """Extract emerging topics from the documents."""
    doc_summaries = []
    for doc in documents[:20]:
        preview = doc["content"][:500]
        doc_summaries.append(f"[{doc['filename']}]: {preview}")

    combined = "\n\n".join(doc_summaries)

    system_prompt = (
        "You are a trend analysis expert. Identify the key topics and emerging trends "
        "from the provided documents. Respond ONLY with valid JSON:\n"
        '{"topics": [{"name": "topic", "frequency": "high|medium|low", '
        '"trend": "emerging|growing|stable|declining", '
        '"description": "brief description", "related_docs": ["file1.txt"]}], '
        '"overall_theme": "main theme description"}'
    )

    messages = [{"role": "user", "content": (
        f"Analyze these {len(documents)} documents for trends and topics:\n\n{combined}"
    )}]

    response = chat(messages, system_prompt=system_prompt, temperature=0.3, max_tokens=3000)

    try:
        start = response.find("{")
        end = response.rfind("}") + 1
        if start >= 0 and end > start:
            return json.loads(response[start:end])
    except (json.JSONDecodeError, ValueError):
        pass

    return {"topics": [], "overall_theme": "Analysis unavailable"}


def analyze_sentiment_trends(documents: list[dict]) -> dict:
    """Analyze sentiment trends across documents."""
    doc_summaries = []
    for doc in documents[:15]:
        preview = doc["content"][:300]
        doc_summaries.append(f"[{doc['filename']}]: {preview}")

    combined = "\n\n".join(doc_summaries)

    system_prompt = (
        "You are a sentiment analysis expert. Analyze sentiment patterns across "
        "the provided documents. Respond ONLY with valid JSON:\n"
        '{"overall_sentiment": "positive|negative|neutral|mixed", '
        '"sentiment_distribution": {"positive": N, "negative": N, "neutral": N}, '
        '"sentiment_shifts": ["description of any notable shifts"], '
        '"key_positive_themes": ["theme1"], "key_negative_themes": ["theme1"]}'
    )

    messages = [{"role": "user", "content": (
        f"Analyze sentiment trends across these {len(documents)} documents:\n\n{combined}"
    )}]

    response = chat(messages, system_prompt=system_prompt, temperature=0.3, max_tokens=2000)

    try:
        start = response.find("{")
        end = response.rfind("}") + 1
        if start >= 0 and end > start:
            return json.loads(response[start:end])
    except (json.JSONDecodeError, ValueError):
        pass

    return {
        "overall_sentiment": "neutral",
        "sentiment_distribution": {"positive": 0, "negative": 0, "neutral": 0},
        "sentiment_shifts": [],
        "key_positive_themes": [],
        "key_negative_themes": [],
    }


def generate_trend_report(documents: list[dict], topics: dict, sentiments: dict, timeframe: str) -> str:
    """Generate a comprehensive trend analysis report."""
    topics_text = json.dumps(topics, indent=2)
    sentiments_text = json.dumps(sentiments, indent=2)

    system_prompt = (
        "You are a senior research analyst. Write a comprehensive trend analysis "
        "report. Be specific about emerging patterns, provide evidence from the data, "
        "and offer forward-looking insights. Format with markdown."
    )

    messages = [{"role": "user", "content": (
        f"Generate a trend analysis report for timeframe: {timeframe}\n\n"
        f"Documents analyzed: {len(documents)}\n\n"
        f"Extracted Topics:\n{topics_text}\n\n"
        f"Sentiment Analysis:\n{sentiments_text}\n\n"
        "Include:\n"
        "1. Executive Summary\n"
        "2. Emerging Topics & Trends\n"
        "3. Sentiment Analysis\n"
        "4. Key Insights\n"
        "5. Predictions & Outlook"
    )}]

    return chat(messages, system_prompt=system_prompt, temperature=0.4, max_tokens=4000)


def display_topics(topics: dict) -> None:
    """Display extracted topics in a table."""
    table = Table(title="🔍 Identified Topics & Trends", show_lines=True)
    table.add_column("#", style="dim", width=4)
    table.add_column("Topic", style="cyan bold", min_width=18)
    table.add_column("Frequency", justify="center", width=12)
    table.add_column("Trend", justify="center", width=12)
    table.add_column("Description", max_width=45, overflow="fold")

    trend_colors = {"emerging": "green", "growing": "blue", "stable": "yellow", "declining": "red"}
    freq_emojis = {"high": "🔥", "medium": "📈", "low": "📊"}

    for i, topic in enumerate(topics.get("topics", []), 1):
        trend = topic.get("trend", "stable")
        freq = topic.get("frequency", "medium")
        color = trend_colors.get(trend, "white")
        emoji = freq_emojis.get(freq, "📊")

        table.add_row(
            str(i),
            topic.get("name", "Unknown"),
            f"{emoji} {freq.title()}",
            f"[{color}]{trend.title()}[/{color}]",
            topic.get("description", "N/A"),
        )

    console.print(table)

    overall = topics.get("overall_theme", "")
    if overall:
        console.print(f"\n[bold]Overall Theme:[/bold] {overall}")


def display_sentiment_summary(sentiments: dict) -> None:
    """Display sentiment analysis summary."""
    dist = sentiments.get("sentiment_distribution", {})
    overall = sentiments.get("overall_sentiment", "neutral")

    sentiment_colors = {"positive": "green", "negative": "red", "neutral": "yellow", "mixed": "blue"}
    color = sentiment_colors.get(overall, "white")

    summary = f"**Overall Sentiment:** [{color}]{overall.title()}[/{color}]\n\n"
    summary += f"😊 Positive: {dist.get('positive', 0)} | "
    summary += f"😞 Negative: {dist.get('negative', 0)} | "
    summary += f"😐 Neutral: {dist.get('neutral', 0)}\n\n"

    shifts = sentiments.get("sentiment_shifts", [])
    if shifts:
        summary += "**Notable Shifts:**\n"
        for shift in shifts:
            summary += f"  • {shift}\n"

    console.print(Panel(Markdown(summary), title="💭 Sentiment Overview", border_style="blue"))


@click.command()
@click.option("--dir", "-d", "directory", required=True, help="Directory containing text files to analyze.")
@click.option("--timeframe", "-t", default="recent", help="Timeframe label (e.g., 'last month', 'Q1-2024').")
@click.option("--sentiment/--no-sentiment", default=True, help="Include sentiment analysis.")
def main(directory: str, timeframe: str, sentiment: bool) -> None:
    """Trend Analysis Tool - Analyze trends from text data."""
    console.print(Panel("📈 [bold blue]Trend Analysis Tool[/bold blue]", expand=False))

    if not check_ollama_running():
        console.print("[red]Error:[/red] Ollama is not running. Start it with: ollama serve")
        sys.exit(1)

    with console.status("[bold green]Loading documents..."):
        documents = load_text_files(directory)

    console.print(f"[green]✓[/green] Loaded [bold]{len(documents)}[/bold] documents from [bold]{directory}[/bold]")
    console.print(f"[bold]Timeframe:[/bold] {timeframe}\n")

    with console.status("[bold green]Extracting topics and trends..."):
        topics = extract_topics(documents)

    display_topics(topics)
    console.print()

    sentiments = {}
    if sentiment:
        with console.status("[bold green]Analyzing sentiment trends..."):
            sentiments = analyze_sentiment_trends(documents)
        display_sentiment_summary(sentiments)
        console.print()

    with console.status("[bold green]Generating trend report..."):
        report = generate_trend_report(documents, topics, sentiments, timeframe)

    console.print(Panel(Markdown(report), title=f"📋 Trend Report - {timeframe}", border_style="green"))


if __name__ == "__main__":
    main()
