#!/usr/bin/env python3
"""Family Story Creator - Creates personalized family stories from memories and events."""

import sys
import os
import json
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from common.llm_client import chat, generate, check_ollama_running

import click
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.progress import Progress

console = Console()
STORIES_FILE = os.path.join(os.path.dirname(__file__), "family_stories.json")

STORY_STYLES = {
    "heartwarming": "Write in a warm, emotional, feel-good style that celebrates family bonds.",
    "humorous": "Write with humor, funny anecdotes, and light-hearted observations.",
    "adventurous": "Write as an exciting adventure story with dramatic moments.",
    "nostalgic": "Write with a nostalgic, reflective tone that cherishes memories.",
    "fairy-tale": "Write in a fairy-tale style with magical elements woven into real events.",
    "poetic": "Write with poetic language, rich imagery, and lyrical prose.",
}


def load_stories() -> list[dict]:
    """Load saved stories."""
    if os.path.exists(STORIES_FILE):
        try:
            with open(STORIES_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    return []


def save_story(story: dict) -> None:
    """Save a new story."""
    stories = load_stories()
    story["id"] = len(stories) + 1
    story["created"] = datetime.now().isoformat()
    stories.append(story)
    with open(STORIES_FILE, 'w') as f:
        json.dump(stories, f, indent=2)


def create_story(members: str, event: str, style: str, details: str = "",
                 photos: str = "", length: str = "medium") -> str:
    """Create a personalized family story using AI."""
    style_instruction = STORY_STYLES.get(style, STORY_STYLES["heartwarming"])

    length_guide = {
        "short": "Write a short story of about 300-500 words.",
        "medium": "Write a medium-length story of about 500-800 words.",
        "long": "Write a detailed story of about 800-1200 words.",
    }

    prompt = f"""Create a personalized family story with these details:

**Family Members**: {members}
**Event/Occasion**: {event}
{f'**Additional Details**: {details}' if details else ''}
{f'**Photo Descriptions**: {photos}' if photos else ''}

Style: {style_instruction}
{length_guide.get(length, length_guide['medium'])}

Requirements:
1. Use the actual family member names naturally in the story
2. Make the event the central focus of the narrative
3. Include realistic dialogue between family members
4. Add sensory details (sights, sounds, smells) to bring scenes alive
5. End with a meaningful reflection or heartwarming moment
6. Make it feel personal and authentic

Write the story in markdown format with a creative title."""

    return generate(
        prompt=prompt,
        system_prompt="You are a gifted family storyteller who creates beautiful, personalized narratives from real family memories and events. Your stories are touching, authentic, and treasured keepsakes.",
        temperature=0.8,
        max_tokens=3000,
    )


def continue_story(existing_story: str, continuation_prompt: str) -> str:
    """Continue or expand an existing story."""
    prompt = f"""Here is an existing family story:

{existing_story}

Please continue the story with this direction: {continuation_prompt}

Maintain the same style, characters, and tone. Add 300-500 more words."""

    return generate(
        prompt=prompt,
        system_prompt="You are a gifted family storyteller continuing a narrative.",
        temperature=0.8,
    )


def create_poem(members: str, event: str, style: str = "rhyming") -> str:
    """Create a family poem about an event."""
    prompt = f"""Create a beautiful {style} poem about this family event:

Family Members: {members}
Event: {event}

Write a poem of 4-6 stanzas that:
1. Mentions each family member by name
2. Captures the spirit of the event
3. Is emotionally moving and personal
4. Has a memorable final stanza"""

    return generate(
        prompt=prompt,
        system_prompt="You are a poet who creates personalized family poems.",
        temperature=0.8,
    )


@click.group()
def cli():
    """Family Story Creator - Create personalized family stories from memories."""
    pass


@cli.command()
@click.option('--members', '-m', required=True, help='Comma-separated family member names')
@click.option('--event', '-e', required=True, help='Event or occasion description')
@click.option('--style', '-s', default='heartwarming',
              type=click.Choice(list(STORY_STYLES.keys())),
              help='Story style')
@click.option('--details', '-d', default='', help='Additional details about the event')
@click.option('--photos', '-p', default='', help='Descriptions of photos from the event')
@click.option('--length', '-l', default='medium', type=click.Choice(['short', 'medium', 'long']))
@click.option('--save', is_flag=True, help='Save the story')
@click.option('--output', '-o', default=None, help='Output file path')
def create(members, event, style, details, photos, length, save, output):
    """Create a personalized family story."""
    console.print(Panel(
        "[bold blue]👨‍👩‍👧‍👦 Family Story Creator[/bold blue]\n"
        f"[dim]Style: {style} | Length: {length}[/dim]",
        border_style="blue",
    ))

    if not check_ollama_running():
        console.print("[red]Error:[/red] Ollama is not running. Start it with: [bold]ollama serve[/bold]")
        sys.exit(1)

    console.print(f"[cyan]Family:[/cyan] {members}")
    console.print(f"[cyan]Event:[/cyan] {event}\n")

    with console.status("[bold green]Crafting your family story..."):
        story = create_story(members, event, style, details, photos, length)

    console.print(Panel(Markdown(story), title="📖 Your Family Story", border_style="green"))

    if save:
        save_story({
            "members": members,
            "event": event,
            "style": style,
            "story": story,
        })
        console.print("[green]✅ Story saved![/green]")

    if output:
        with open(output, 'w') as f:
            f.write(story)
        console.print(f"[green]✅ Story saved to {output}[/green]")


@cli.command()
@click.option('--members', '-m', required=True, help='Family member names')
@click.option('--event', '-e', required=True, help='Event description')
@click.option('--style', '-s', default='rhyming', help='Poem style (rhyming, free-verse, haiku)')
def poem(members, event, style):
    """Create a family poem."""
    console.print(Panel("[bold blue]👨‍👩‍👧‍👦 Family Story Creator[/bold blue]", border_style="blue"))

    if not check_ollama_running():
        console.print("[red]Error:[/red] Ollama is not running.")
        sys.exit(1)

    with console.status("[bold green]Writing your family poem..."):
        result = create_poem(members, event, style)

    console.print(Panel(Markdown(result), title="🎭 Family Poem", border_style="magenta"))


@cli.command(name='list')
def list_stories():
    """List all saved stories."""
    console.print(Panel("[bold blue]👨‍👩‍👧‍👦 Family Story Creator[/bold blue]", border_style="blue"))
    stories = load_stories()

    if not stories:
        console.print("[yellow]No saved stories yet. Create one with: python app.py create --members '...' --event '...'[/yellow]")
        return

    from rich.table import Table
    table = Table(title="📚 Saved Stories", show_lines=True)
    table.add_column("ID", style="cyan", width=5)
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
            s.get("created", "")[:10],
        )

    console.print(table)


if __name__ == '__main__':
    cli()
