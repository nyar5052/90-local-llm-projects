#!/usr/bin/env python3
"""Personal Knowledge Base - Store notes and search semantically with AI."""

import sys
import os
import json
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from common.llm_client import chat, generate, embed, check_ollama_running

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown

console = Console()
KB_FILE = os.path.join(os.path.dirname(__file__), "knowledge_base.json")


def load_kb() -> dict:
    """Load the knowledge base from JSON file."""
    if os.path.exists(KB_FILE):
        try:
            with open(KB_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {"notes": [], "metadata": {"created": datetime.now().isoformat()}}
    return {"notes": [], "metadata": {"created": datetime.now().isoformat()}}


def save_kb(kb: dict) -> None:
    """Save the knowledge base to JSON file."""
    kb["metadata"]["updated"] = datetime.now().isoformat()
    with open(KB_FILE, 'w') as f:
        json.dump(kb, f, indent=2)


def add_note(title: str, content: str, tags: list[str] = None) -> dict:
    """Add a note to the knowledge base."""
    kb = load_kb()
    note_id = len(kb["notes"]) + 1
    note = {
        "id": note_id,
        "title": title,
        "content": content,
        "tags": tags or [],
        "created": datetime.now().isoformat(),
        "updated": datetime.now().isoformat(),
    }
    kb["notes"].append(note)
    save_kb(kb)
    return note


def search_notes(query: str) -> str:
    """Search notes semantically using AI."""
    kb = load_kb()
    if not kb["notes"]:
        return "No notes in knowledge base. Add some with the 'add' command."

    notes_text = "\n\n".join(
        f"Note #{n['id']}: {n['title']}\nTags: {', '.join(n.get('tags', []))}\nContent: {n['content']}"
        for n in kb["notes"]
    )

    prompt = f"""Search the following knowledge base for information related to: "{query}"

Knowledge Base:
{notes_text}

Please:
1. Identify the most relevant notes
2. Summarize the relevant information
3. Show connections between related notes
4. Suggest related topics to explore

Format your response in markdown."""

    return generate(
        prompt=prompt,
        system_prompt="You are a knowledge base search assistant. Find and synthesize relevant information from notes.",
        temperature=0.3,
    )


def summarize_kb() -> str:
    """Generate a summary of the entire knowledge base."""
    kb = load_kb()
    if not kb["notes"]:
        return "Knowledge base is empty."

    notes_text = "\n\n".join(
        f"- {n['title']}: {n['content'][:200]}" for n in kb["notes"]
    )

    prompt = f"""Summarize this knowledge base:

{notes_text}

Provide:
1. **Overview**: Main topics covered
2. **Key Insights**: Most important information
3. **Knowledge Gaps**: Areas that could use more notes
4. **Connections**: How different notes relate to each other"""

    return generate(
        prompt=prompt,
        system_prompt="You are a knowledge organization expert.",
        temperature=0.5,
    )


def display_notes(notes: list[dict]) -> None:
    """Display notes in a formatted table."""
    table = Table(title="📚 Knowledge Base", show_lines=True)
    table.add_column("ID", style="cyan", width=5)
    table.add_column("Title", style="white", min_width=20)
    table.add_column("Tags", style="green", min_width=15)
    table.add_column("Created", style="yellow", min_width=12)
    table.add_column("Preview", style="dim", max_width=40)

    for note in notes:
        created = note.get("created", "N/A")[:10]
        preview = note.get("content", "")[:40] + "..." if len(note.get("content", "")) > 40 else note.get("content", "")
        table.add_row(
            str(note["id"]),
            note["title"],
            ", ".join(note.get("tags", [])),
            created,
            preview,
        )

    console.print(table)


@click.group()
def cli():
    """Personal Knowledge Base - AI-powered note storage and semantic search."""
    pass


@cli.command()
@click.option('--title', '-t', required=True, help='Note title')
@click.option('--content', '-c', required=True, help='Note content')
@click.option('--tags', '-g', default='', help='Comma-separated tags')
def add(title, content, tags):
    """Add a new note to the knowledge base."""
    console.print(Panel(
        "[bold blue]📚 Personal Knowledge Base[/bold blue]\n"
        "[dim]Adding new note...[/dim]",
        border_style="blue",
    ))

    tag_list = [t.strip() for t in tags.split(',') if t.strip()] if tags else []
    note = add_note(title, content, tag_list)
    console.print(f"[green]✅ Note #{note['id']} added:[/green] {title}")
    if tag_list:
        console.print(f"[dim]Tags: {', '.join(tag_list)}[/dim]")


@cli.command()
@click.option('--query', '-q', required=True, help='Search query')
def search(query):
    """Search the knowledge base semantically."""
    console.print(Panel(
        "[bold blue]📚 Personal Knowledge Base[/bold blue]\n"
        f"[dim]Searching for: {query}[/dim]",
        border_style="blue",
    ))

    if not check_ollama_running():
        console.print("[red]Error:[/red] Ollama is not running. Start it with: [bold]ollama serve[/bold]")
        sys.exit(1)

    with console.status("[bold green]Searching knowledge base..."):
        result = search_notes(query)
    console.print(Panel(Markdown(result), title="🔍 Search Results", border_style="green"))


@cli.command(name='list')
def list_notes():
    """List all notes in the knowledge base."""
    console.print(Panel(
        "[bold blue]📚 Personal Knowledge Base[/bold blue]",
        border_style="blue",
    ))

    kb = load_kb()
    if not kb["notes"]:
        console.print("[yellow]Knowledge base is empty. Add notes with: python app.py add --title '...' --content '...'[/yellow]")
        return

    display_notes(kb["notes"])
    console.print(f"\n[dim]Total notes: {len(kb['notes'])}[/dim]")


@cli.command()
def summary():
    """Generate an AI summary of the knowledge base."""
    console.print(Panel(
        "[bold blue]📚 Personal Knowledge Base[/bold blue]\n"
        "[dim]Generating summary...[/dim]",
        border_style="blue",
    ))

    if not check_ollama_running():
        console.print("[red]Error:[/red] Ollama is not running. Start it with: [bold]ollama serve[/bold]")
        sys.exit(1)

    with console.status("[bold green]Summarizing knowledge base..."):
        result = summarize_kb()
    console.print(Panel(Markdown(result), title="📋 Knowledge Base Summary", border_style="cyan"))


@cli.command()
@click.option('--note-id', '-i', required=True, type=int, help='Note ID to delete')
def delete(note_id):
    """Delete a note from the knowledge base."""
    kb = load_kb()
    original_len = len(kb["notes"])
    kb["notes"] = [n for n in kb["notes"] if n["id"] != note_id]

    if len(kb["notes"]) == original_len:
        console.print(f"[red]Note #{note_id} not found.[/red]")
        return

    save_kb(kb)
    console.print(f"[green]✅ Note #{note_id} deleted.[/green]")


if __name__ == '__main__':
    cli()
