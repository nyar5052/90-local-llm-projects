#!/usr/bin/env python3
"""Poem & Lyrics Generator - Generate poems or song lyrics using a local LLM."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from common.llm_client import chat, check_ollama_running

console = Console()

STYLES = ["haiku", "sonnet", "free-verse", "limerick", "rap", "ballad", "acrostic"]
MOODS = ["happy", "melancholic", "romantic", "dark", "hopeful", "nostalgic"]


def build_prompt(theme: str, style: str, mood: str | None, title: str | None) -> str:
    """Build the poem/lyrics generation prompt."""
    style_instructions = {
        "haiku": "Write a traditional haiku (5-7-5 syllable structure, 3 lines). Write 3 haikus.",
        "sonnet": "Write a Shakespearean sonnet (14 lines, iambic pentameter, ABAB CDCD EFEF GG rhyme scheme).",
        "free-verse": "Write a free verse poem (no fixed meter or rhyme, 15-25 lines).",
        "limerick": "Write 3 limericks (5 lines each, AABBA rhyme scheme, humorous).",
        "rap": "Write rap lyrics with 3 verses and a chorus. Include internal rhymes and wordplay.",
        "ballad": "Write a ballad with 4-5 stanzas, ABAB rhyme scheme, telling a story.",
        "acrostic": "Write an acrostic poem where the first letters of each line spell out a word related to the theme.",
    }

    prompt = f"Theme/Subject: {theme}\n\n"
    prompt += f"Style: {style}\n"
    prompt += f"Instructions: {style_instructions.get(style, 'Write a poem in this style.')}\n"
    if mood:
        prompt += f"Mood/Emotion: {mood}\n"
    if title:
        prompt += f"Title: {title}\n"
    prompt += (
        "\nFormat the output with the title on the first line, "
        "followed by a blank line, then the poem/lyrics. "
        "Add a brief note about the style at the end."
    )
    return prompt


def generate_poem(theme: str, style: str, mood: str | None, title: str | None) -> str:
    """Generate a poem or lyrics using the LLM."""
    system_prompt = (
        "You are a talented poet and lyricist with mastery of all poetic forms. "
        "You create evocative, beautiful works that follow the rules of each form precisely. "
        "Your writing is vivid, emotionally resonant, and technically skilled."
    )
    user_prompt = build_prompt(theme, style, mood, title)
    messages = [{"role": "user", "content": user_prompt}]
    return chat(messages, system_prompt=system_prompt, temperature=0.9, max_tokens=2048)


@click.command()
@click.option("--theme", required=True, help="Theme or subject for the poem/lyrics.")
@click.option("--style", type=click.Choice(STYLES, case_sensitive=False), default="free-verse", help="Poetic style.")
@click.option("--mood", type=click.Choice(MOODS, case_sensitive=False), default=None, help="Mood/emotion.")
@click.option("--title", default=None, help="Specify a title (auto-generated if omitted).")
@click.option("--output", "-o", default=None, help="Save output to file.")
def main(theme: str, style: str, mood: str | None, title: str | None, output: str):
    """Generate poems or song lyrics from themes and styles."""
    console.print(Panel.fit("[bold cyan]Poem & Lyrics Generator[/bold cyan]", border_style="cyan"))

    if not check_ollama_running():
        console.print("[red]Error: Ollama is not running. Start it with: ollama serve[/red]")
        sys.exit(1)

    console.print(f"[cyan]Theme:[/cyan] {theme}")
    console.print(f"[cyan]Style:[/cyan] {style}")
    if mood:
        console.print(f"[cyan]Mood:[/cyan] {mood}")
    if title:
        console.print(f"[cyan]Title:[/cyan] {title}")
    console.print()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        progress.add_task(f"Composing {style}...", total=None)
        result = generate_poem(theme, style, mood, title)

    border = "magenta" if mood in ("romantic", "melancholic") else "cyan"
    console.print(Panel(result, title=f"✨ {style.title()}", border_style=border))

    if output:
        with open(output, "w", encoding="utf-8") as f:
            f.write(result)
        console.print(f"[green]Saved to {output}[/green]")


if __name__ == "__main__":
    main()
