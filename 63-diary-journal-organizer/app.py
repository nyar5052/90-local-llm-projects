#!/usr/bin/env python3
"""Diary Journal Organizer - Private diary with AI-powered insights."""

import sys
import os
import json
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from common.llm_client import chat, generate, check_ollama_running

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt

console = Console()
DIARY_FILE = os.path.join(os.path.dirname(__file__), "diary.json")


def load_diary() -> dict:
    """Load diary entries from JSON file."""
    if os.path.exists(DIARY_FILE):
        try:
            with open(DIARY_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {"entries": []}
    return {"entries": []}


def save_diary(diary: dict) -> None:
    """Save diary entries to JSON file."""
    with open(DIARY_FILE, 'w') as f:
        json.dump(diary, f, indent=2)


def write_entry(content: str, mood: str = "", tags: list[str] = None) -> dict:
    """Write a new diary entry."""
    diary = load_diary()
    entry = {
        "id": len(diary["entries"]) + 1,
        "date": datetime.now().isoformat(),
        "content": content,
        "mood": mood,
        "tags": tags or [],
    }
    diary["entries"].append(entry)
    save_diary(diary)
    return entry


def get_entries_for_period(period: str) -> list[dict]:
    """Get entries for a specific time period."""
    diary = load_diary()
    now = datetime.now()

    if period == "week":
        cutoff = now - timedelta(days=7)
    elif period == "month":
        cutoff = now - timedelta(days=30)
    elif period == "year":
        cutoff = now - timedelta(days=365)
    else:
        cutoff = now - timedelta(days=7)

    filtered = []
    for entry in diary["entries"]:
        try:
            entry_date = datetime.fromisoformat(entry["date"])
            if entry_date >= cutoff:
                filtered.append(entry)
        except (ValueError, KeyError):
            continue

    return filtered


def analyze_mood(entries: list[dict]) -> str:
    """Analyze mood patterns using AI."""
    entries_text = "\n\n".join(
        f"Date: {e['date'][:10]}\nMood: {e.get('mood', 'not specified')}\nEntry: {e['content']}"
        for e in entries
    )

    prompt = f"""Analyze the mood patterns in these diary entries:

{entries_text}

Provide:
1. **Overall Mood Trend**: How has the mood changed over time?
2. **Common Emotions**: Most frequently expressed emotions
3. **Mood Triggers**: What events or topics affect mood positively/negatively
4. **Emotional Patterns**: Any recurring patterns (day of week, time patterns)
5. **Wellness Suggestions**: Kind, supportive suggestions for emotional well-being

Be empathetic, supportive, and non-judgmental in your analysis."""

    return generate(
        prompt=prompt,
        system_prompt="You are a compassionate journal therapist who provides supportive mood analysis. Be warm, empathetic, and constructive.",
        temperature=0.6,
    )


def find_themes(entries: list[dict]) -> str:
    """Find recurring themes in diary entries."""
    entries_text = "\n\n".join(
        f"- {e['date'][:10]}: {e['content'][:200]}" for e in entries
    )

    prompt = f"""Identify recurring themes in these diary entries:

{entries_text}

Provide:
1. **Major Themes**: Top 5 recurring topics or concerns
2. **Growth Areas**: Topics showing personal development
3. **Patterns**: Recurring situations or feelings
4. **Reflection Prompts**: Questions for deeper self-reflection based on themes

Format in clear markdown."""

    return generate(
        prompt=prompt,
        system_prompt="You are a thoughtful journal analysis assistant.",
        temperature=0.5,
    )


def generate_insights(entries: list[dict]) -> str:
    """Generate comprehensive insights from diary entries."""
    entries_text = "\n\n".join(
        f"Date: {e['date'][:10]}\nMood: {e.get('mood', 'N/A')}\nTags: {', '.join(e.get('tags', []))}\nEntry: {e['content']}"
        for e in entries
    )

    prompt = f"""Provide comprehensive insights from these diary entries:

{entries_text}

Generate:
1. **Summary**: Brief overview of the period
2. **Mood Analysis**: Emotional trends and patterns
3. **Key Events**: Most significant happenings
4. **Recurring Themes**: Topics that come up repeatedly
5. **Personal Growth**: Areas of development or change
6. **Recommendations**: Supportive suggestions for well-being

Be compassionate and constructive."""

    return generate(
        prompt=prompt,
        system_prompt="You are a caring journal insights assistant providing thoughtful, supportive analysis.",
        temperature=0.6,
    )


def display_entries(entries: list[dict]) -> None:
    """Display diary entries in formatted panels."""
    for entry in entries:
        mood_emoji = {"happy": "😊", "sad": "😢", "anxious": "😰", "calm": "😌",
                      "excited": "🎉", "angry": "😤", "grateful": "🙏", "tired": "😴"
                      }.get(entry.get("mood", "").lower(), "📝")
        date_str = entry["date"][:10]
        tags = ", ".join(entry.get("tags", []))
        header = f"{mood_emoji} {date_str}"
        if entry.get("mood"):
            header += f" | Mood: {entry['mood']}"
        if tags:
            header += f" | Tags: {tags}"

        console.print(Panel(entry["content"], title=header, border_style="blue"))


@click.group()
def cli():
    """Diary Journal Organizer - Private diary with AI-powered insights."""
    pass


@cli.command()
@click.option('--content', '-c', default=None, help='Entry content (or enter interactively)')
@click.option('--mood', '-m', default='', help='Your current mood')
@click.option('--tags', '-t', default='', help='Comma-separated tags')
def write(content, mood, tags):
    """Write a new diary entry."""
    console.print(Panel(
        "[bold blue]📔 Diary Journal[/bold blue]\n"
        "[dim]Write a new entry...[/dim]",
        border_style="blue",
    ))

    if not content:
        content = Prompt.ask("[cyan]What's on your mind today?[/cyan]")

    if not mood:
        mood = Prompt.ask(
            "[cyan]How are you feeling?[/cyan]",
            default="neutral",
        )

    tag_list = [t.strip() for t in tags.split(',') if t.strip()] if tags else []
    entry = write_entry(content, mood, tag_list)
    console.print(f"\n[green]✅ Entry #{entry['id']} saved for {entry['date'][:10]}[/green]")


@cli.command()
@click.option('--period', '-p', default='week', type=click.Choice(['week', 'month', 'year']),
              help='Time period for insights')
@click.option('--mood-only', is_flag=True, help='Show only mood analysis')
@click.option('--themes-only', is_flag=True, help='Show only theme analysis')
def insights(period, mood_only, themes_only):
    """Get AI-powered insights from your diary."""
    console.print(Panel(
        "[bold blue]📔 Diary Journal[/bold blue]\n"
        f"[dim]Generating {period}ly insights...[/dim]",
        border_style="blue",
    ))

    if not check_ollama_running():
        console.print("[red]Error:[/red] Ollama is not running. Start it with: [bold]ollama serve[/bold]")
        sys.exit(1)

    entries = get_entries_for_period(period)
    if not entries:
        console.print(f"[yellow]No entries found for the past {period}.[/yellow]")
        return

    console.print(f"[dim]Found {len(entries)} entries for the past {period}[/dim]\n")

    if mood_only:
        with console.status("[bold green]Analyzing mood patterns..."):
            result = analyze_mood(entries)
        console.print(Panel(Markdown(result), title="🎭 Mood Analysis", border_style="magenta"))
    elif themes_only:
        with console.status("[bold green]Finding themes..."):
            result = find_themes(entries)
        console.print(Panel(Markdown(result), title="🔍 Recurring Themes", border_style="cyan"))
    else:
        with console.status("[bold green]Generating comprehensive insights..."):
            result = generate_insights(entries)
        console.print(Panel(Markdown(result), title="✨ Journal Insights", border_style="green"))


@cli.command()
@click.option('--period', '-p', default='week', type=click.Choice(['week', 'month', 'year']),
              help='Time period to view')
@click.option('--last', '-n', default=10, help='Number of recent entries to show')
def view(period, last):
    """View recent diary entries."""
    console.print(Panel(
        "[bold blue]📔 Diary Journal[/bold blue]",
        border_style="blue",
    ))

    entries = get_entries_for_period(period)
    if not entries:
        console.print(f"[yellow]No entries found for the past {period}.[/yellow]")
        return

    display_entries(entries[-last:])
    console.print(f"\n[dim]Showing {min(last, len(entries))} of {len(entries)} entries[/dim]")


if __name__ == '__main__':
    cli()
