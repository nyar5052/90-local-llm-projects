#!/usr/bin/env python3
"""Family Story Creator - CLI interface with Rich output."""

import sys
import os
import logging

import click
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.table import Table

from .core import (
    STORY_STYLES,
    load_config,
    load_stories,
    save_story,
    delete_story,
    create_story,
    create_chapter,
    create_book,
    continue_story,
    create_poem,
    export_story,
)

console = Console()
logger = logging.getLogger(__name__)

# Try importing Ollama health check (optional, graceful fallback)
try:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    from common.llm_client import check_ollama_running
except ImportError:
    def check_ollama_running():
        return True


def _banner():
    console.print(Panel(
        "[bold blue]📖 Family Story Creator[/bold blue] [dim]v2.0.0[/dim]",
        border_style="blue",
    ))


@click.group()
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging.")
@click.option("--config", "-c", "config_path", default="config.yaml", help="Path to config file.")
@click.pass_context
def cli(ctx, verbose, config_path):
    """Family Story Creator - Create personalized family stories from memories."""
    ctx.ensure_object(dict)
    cfg = load_config(config_path)
    ctx.obj["config"] = cfg
    if verbose:
        logging.basicConfig(level=logging.DEBUG, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    else:
        log_level = cfg.get("logging", {}).get("level", "WARNING")
        logging.basicConfig(level=getattr(logging, log_level, logging.WARNING))


@cli.command()
@click.option("--members", "-m", required=True, help="Comma-separated family member names.")
@click.option("--event", "-e", required=True, help="Event or occasion description.")
@click.option("--style", "-s", default=None, type=click.Choice(list(STORY_STYLES.keys())), help="Story style.")
@click.option("--details", "-d", default="", help="Additional details about the event.")
@click.option("--photos", "-p", default="", help="Descriptions of photos from the event.")
@click.option("--length", "-l", default=None, type=click.Choice(["short", "medium", "long"]))
@click.option("--save", is_flag=True, help="Save the story to library.")
@click.option("--output", "-o", default=None, help="Output file path.")
@click.pass_context
def create(ctx, members, event, style, details, photos, length, save, output):
    """Create a personalized family story."""
    cfg = ctx.obj["config"]
    style = style or cfg.get("default_style", "heartwarming")
    length = length or cfg.get("default_length", "medium")
    _banner()

    if not check_ollama_running():
        console.print("[red]Error:[/red] Ollama is not running. Start it with: [bold]ollama serve[/bold]")
        raise SystemExit(1)

    console.print(f"[cyan]Family:[/cyan] {members}")
    console.print(f"[cyan]Event:[/cyan] {event}")
    console.print(f"[cyan]Style:[/cyan] {style} | [cyan]Length:[/cyan] {length}\n")

    with console.status("[bold green]Crafting your family story..."):
        story_text = create_story(members, event, style, details, photos, length, config=cfg)

    console.print(Panel(Markdown(story_text), title="📖 Your Family Story", border_style="green"))

    if save:
        saved = save_story(
            {"members": members, "event": event, "style": style, "story": story_text},
            stories_file=cfg.get("stories_file"),
        )
        console.print(f"[green]✅ Story saved (id: {saved['id']})[/green]")

    if output:
        with open(output, "w") as f:
            f.write(story_text)
        console.print(f"[green]✅ Story written to {output}[/green]")


@cli.command()
@click.option("--members", "-m", required=True, help="Family member names.")
@click.option("--event", "-e", required=True, help="Event description.")
@click.option("--style", "-s", default="rhyming", help="Poem style (rhyming, free-verse, haiku).")
@click.pass_context
def poem(ctx, members, event, style):
    """Create a family poem."""
    cfg = ctx.obj["config"]
    _banner()

    if not check_ollama_running():
        console.print("[red]Error:[/red] Ollama is not running.")
        raise SystemExit(1)

    with console.status("[bold green]Writing your family poem..."):
        result = create_poem(members, event, style, config=cfg)

    console.print(Panel(Markdown(result), title="🎭 Family Poem", border_style="magenta"))


@cli.command()
@click.option("--title", "-t", required=True, help="Chapter title.")
@click.option("--number", "-n", required=True, type=int, help="Chapter number.")
@click.option("--members", "-m", required=True, help="Family member names.")
@click.option("--events", "-e", required=True, help="Chapter events.")
@click.option("--style", "-s", default=None, type=click.Choice(list(STORY_STYLES.keys())))
@click.pass_context
def chapter(ctx, title, number, members, events, style):
    """Create a single story chapter."""
    cfg = ctx.obj["config"]
    style = style or cfg.get("default_style", "heartwarming")
    _banner()

    if not check_ollama_running():
        console.print("[red]Error:[/red] Ollama is not running.")
        raise SystemExit(1)

    with console.status(f"[bold green]Writing Chapter {number}..."):
        result = create_chapter(number, title, members, events, style, config=cfg)

    console.print(Panel(Markdown(result), title=f"📖 Chapter {number}: {title}", border_style="green"))


@cli.command()
@click.option("--title", "-t", required=True, help="Book title.")
@click.option("--members", "-m", required=True, help="Family member names.")
@click.option("--chapters", "-c", required=True, multiple=True, help="Chapters in title:events format (repeat for each chapter).")
@click.pass_context
def book(ctx, title, members, chapters):
    """Create a multi-chapter story book."""
    cfg = ctx.obj["config"]
    _banner()

    if not check_ollama_running():
        console.print("[red]Error:[/red] Ollama is not running.")
        raise SystemExit(1)

    parsed_chapters = []
    for ch in chapters:
        if ":" in ch:
            ch_title, ch_events = ch.split(":", 1)
            parsed_chapters.append({"title": ch_title.strip(), "events": ch_events.strip()})
        else:
            parsed_chapters.append({"title": ch, "events": ch})

    with console.status(f"[bold green]Creating book '{title}' with {len(parsed_chapters)} chapters..."):
        result = create_book(title, parsed_chapters, members, config=cfg)

    console.print(Panel(f"[bold]{result['title']}[/bold]", title="📚 Book Created", border_style="green"))
    console.print("\n[bold]Table of Contents:[/bold]")
    for i, t in enumerate(result["toc"], 1):
        console.print(f"  {i}. {t}")
    console.print()
    for ch_text in result["chapters"]:
        console.print(Panel(Markdown(ch_text), border_style="blue"))


@cli.command(name="list")
@click.pass_context
def list_cmd(ctx):
    """List all saved stories."""
    cfg = ctx.obj["config"]
    _banner()
    stories = load_stories(cfg.get("stories_file"))

    if not stories:
        console.print("[yellow]No saved stories yet. Create one with: family-story create -m '...' -e '...'[/yellow]")
        return

    table = Table(title="📚 Saved Stories", show_lines=True)
    table.add_column("ID", style="cyan", width=10)
    table.add_column("Members", style="white", min_width=20)
    table.add_column("Event", style="green", min_width=20)
    table.add_column("Style", style="yellow", min_width=12)
    table.add_column("Created", style="dim", min_width=12)

    for s in stories:
        table.add_row(
            str(s.get("id", "")),
            s.get("members", ""),
            s.get("event", ""),
            s.get("style", ""),
            str(s.get("created", ""))[:10],
        )
    console.print(table)


@cli.command(name="export")
@click.option("--story-id", "-i", required=True, help="Story ID to export.")
@click.option("--format", "-f", "fmt", default="markdown", type=click.Choice(["markdown", "html"]))
@click.option("--output", "-o", default=None, help="Output file path.")
@click.pass_context
def export_cmd(ctx, story_id, fmt, output):
    """Export a saved story to markdown or HTML."""
    cfg = ctx.obj["config"]
    _banner()
    stories = load_stories(cfg.get("stories_file"))
    story = next((s for s in stories if str(s.get("id")) == str(story_id)), None)

    if not story:
        console.print(f"[red]Story with id '{story_id}' not found.[/red]")
        raise SystemExit(1)

    result = export_story(story, format=fmt)

    if output:
        with open(output, "w") as f:
            f.write(result)
        console.print(f"[green]✅ Exported to {output}[/green]")
    else:
        console.print(result)


@cli.command(name="delete")
@click.option("--story-id", "-i", required=True, help="Story ID to delete.")
@click.pass_context
def delete_cmd(ctx, story_id):
    """Delete a saved story."""
    cfg = ctx.obj["config"]
    _banner()

    if delete_story(story_id, cfg.get("stories_file")):
        console.print(f"[green]✅ Story {story_id} deleted.[/green]")
    else:
        console.print(f"[red]Story with id '{story_id}' not found.[/red]")


def main():
    """Entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
