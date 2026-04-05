#!/usr/bin/env python3
"""Personal Knowledge Base - Click CLI interface."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from common.llm_client import check_ollama_running  # noqa: E402

import click  # noqa: E402
from rich.console import Console  # noqa: E402
from rich.panel import Panel  # noqa: E402
from rich.markdown import Markdown  # noqa: E402
from rich.table import Table  # noqa: E402

from knowledge_base.core import (  # noqa: E402
    add_note,
    delete_note,
    get_note,
    load_kb,
    search_notes,
    summarize_kb,
    display_notes,
    get_all_tags,
    get_notes_by_tag,
    find_backlinks,
    search_fulltext,
    get_templates,
    apply_template,
    export_notes,
    import_notes,
)

console = Console()

BANNER = "[bold blue]📚 Personal Knowledge Base[/bold blue]"


@click.group()
def cli():
    """Personal Knowledge Base - AI-powered note storage and semantic search."""
    pass


# ── Original commands ────────────────────────────────────────────────────


@cli.command()
@click.option('--title', '-t', required=True, help='Note title')
@click.option('--content', '-c', required=True, help='Note content')
@click.option('--tags', '-g', default='', help='Comma-separated tags')
def add(title, content, tags):
    """Add a new note to the knowledge base."""
    console.print(Panel(f"{BANNER}\n[dim]Adding new note...[/dim]", border_style="blue"))
    tag_list = [t.strip() for t in tags.split(',') if t.strip()] if tags else []
    note = add_note(title, content, tag_list)
    console.print(f"[green]✅ Note #{note['id']} added:[/green] {title}")
    if tag_list:
        console.print(f"[dim]Tags: {', '.join(tag_list)}[/dim]")


@cli.command()
@click.option('--query', '-q', required=True, help='Search query')
def search(query):
    """Search the knowledge base semantically."""
    console.print(Panel(f"{BANNER}\n[dim]Searching for: {query}[/dim]", border_style="blue"))
    if not check_ollama_running():
        console.print("[red]Error:[/red] Ollama is not running. Start it with: [bold]ollama serve[/bold]")
        sys.exit(1)
    with console.status("[bold green]Searching knowledge base..."):
        result = search_notes(query)
    console.print(Panel(Markdown(result), title="🔍 Search Results", border_style="green"))


@cli.command(name='list')
@click.option('--tag', '-g', default=None, help='Filter by tag')
def list_notes(tag):
    """List all notes in the knowledge base."""
    console.print(Panel(BANNER, border_style="blue"))
    if tag:
        notes = get_notes_by_tag(tag)
        if not notes:
            console.print(f"[yellow]No notes with tag '{tag}'.[/yellow]")
            return
    else:
        kb = load_kb()
        notes = kb["notes"]

    if not notes:
        console.print("[yellow]Knowledge base is empty. Add notes with: knowledge-base add -t '...' -c '...'[/yellow]")
        return

    display_notes(notes)
    console.print(f"\n[dim]Total notes: {len(notes)}[/dim]")


@cli.command()
def summary():
    """Generate an AI summary of the knowledge base."""
    console.print(Panel(f"{BANNER}\n[dim]Generating summary...[/dim]", border_style="blue"))
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
    if delete_note(note_id):
        console.print(f"[green]✅ Note #{note_id} deleted.[/green]")
    else:
        console.print(f"[red]Note #{note_id} not found.[/red]")


# ── New commands ─────────────────────────────────────────────────────────


@cli.command()
def tags():
    """Show all tags with note counts."""
    console.print(Panel(f"{BANNER}\n[dim]Tag Cloud[/dim]", border_style="blue"))
    all_tags = get_all_tags()
    if not all_tags:
        console.print("[yellow]No tags found.[/yellow]")
        return

    table = Table(title="🏷️  Tags", show_lines=True)
    table.add_column("Tag", style="green", min_width=15)
    table.add_column("Count", style="cyan", justify="right", width=8)

    for tag, count in sorted(all_tags.items(), key=lambda x: (-x[1], x[0])):
        table.add_row(tag, str(count))

    console.print(table)


@cli.command()
@click.option('--note-id', '-i', required=True, type=int, help='Note ID to find backlinks for')
def backlinks(note_id):
    """Show notes that reference a given note."""
    note = get_note(note_id)
    if note is None:
        console.print(f"[red]Note #{note_id} not found.[/red]")
        return

    console.print(Panel(f"{BANNER}\n[dim]Backlinks for: {note['title']}[/dim]", border_style="blue"))
    links = find_backlinks(note_id)
    if not links:
        console.print("[yellow]No backlinks found for this note.[/yellow]")
        return

    display_notes(links)
    console.print(f"\n[dim]{len(links)} note(s) reference this note.[/dim]")


@cli.command(name='find')
@click.option('--query', '-q', required=True, help='Full-text search query')
def fulltext(query):
    """Full-text search (no LLM required)."""
    console.print(Panel(f"{BANNER}\n[dim]Searching: {query}[/dim]", border_style="blue"))
    results = search_fulltext(query)
    if not results:
        console.print("[yellow]No matching notes found.[/yellow]")
        return
    display_notes(results)
    console.print(f"\n[dim]{len(results)} result(s)[/dim]")


@cli.command(name='export')
@click.option('--output', '-o', default=None, help='Output markdown file path')
def export_cmd(output):
    """Export notes to Markdown."""
    path = export_notes(output)
    console.print(f"[green]✅ Notes exported to:[/green] {path}")


@cli.command(name='import')
@click.argument('filepath')
def import_cmd(filepath):
    """Import notes from a Markdown file."""
    try:
        count = import_notes(filepath)
        console.print(f"[green]✅ Imported {count} note(s) from:[/green] {filepath}")
    except FileNotFoundError as exc:
        console.print(f"[red]Error:[/red] {exc}")


@cli.command()
@click.option('--name', '-n', default=None, help='Template name to apply')
@click.option('--param', '-p', multiple=True, help='Template parameters as key=value')
def template(name, param):
    """List or apply note templates."""
    templates = get_templates()
    if name is None:
        console.print(Panel(f"{BANNER}\n[dim]Available Templates[/dim]", border_style="blue"))
        table = Table(title="📝 Templates", show_lines=True)
        table.add_column("Name", style="cyan", min_width=15)
        table.add_column("Title Pattern", style="white", min_width=25)

        for tname, tpl in templates.items():
            table.add_row(tname, tpl["title"])
        console.print(table)
        return

    kwargs = {}
    for p in param:
        if '=' in p:
            k, v = p.split('=', 1)
            kwargs[k.strip()] = v.strip()

    result = apply_template(name, **kwargs)
    if result is None:
        console.print(f"[red]Template '{name}' not found.[/red]")
        return

    console.print(Panel(
        f"[bold]{result['title']}[/bold]\n\n{result['content']}",
        title="📝 Template Preview",
        border_style="green",
    ))


def main():
    """Entry point."""
    cli()


if __name__ == '__main__':
    main()
