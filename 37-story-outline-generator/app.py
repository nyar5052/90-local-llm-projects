#!/usr/bin/env python3
"""Story Outline Generator - Create detailed story/novel outlines using a local LLM."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import click
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, TextColumn
from common.llm_client import chat, check_ollama_running

console = Console()

GENRES = ["sci-fi", "fantasy", "mystery", "thriller", "romance", "horror", "literary", "historical"]


def build_prompt(genre: str, premise: str, chapters: int, characters: int) -> str:
    """Build the story outline generation prompt."""
    return (
        f"Create a detailed story outline for a {genre} novel.\n\n"
        f"Premise: {premise}\n"
        f"Number of Chapters: {chapters}\n\n"
        f"Please provide:\n\n"
        f"## 1. Story Overview\n"
        f"- Title (suggest 3 options)\n"
        f"- Logline (one sentence that captures the story)\n"
        f"- Theme(s)\n"
        f"- Setting (time, place, world-building details)\n\n"
        f"## 2. Characters ({characters} main characters)\n"
        f"For each character provide:\n"
        f"- Name and role (protagonist, antagonist, supporting)\n"
        f"- Physical description\n"
        f"- Background and motivation\n"
        f"- Character arc (how they change)\n"
        f"- Key relationships\n\n"
        f"## 3. Plot Structure\n"
        f"- Act 1: Setup (inciting incident)\n"
        f"- Act 2: Rising action (complications, midpoint reversal)\n"
        f"- Act 3: Climax and resolution\n\n"
        f"## 4. Chapter Breakdown\n"
        f"For each of the {chapters} chapters:\n"
        f"- Chapter title\n"
        f"- POV character\n"
        f"- Key events (3-4 bullet points)\n"
        f"- Emotional beat\n"
        f"- Cliffhanger/hook for next chapter\n"
    )


def generate_outline(genre: str, premise: str, chapters: int, characters: int) -> str:
    """Generate a story outline using the LLM."""
    system_prompt = (
        "You are a bestselling novelist and story development expert. "
        "You create compelling, well-structured story outlines with rich characters, "
        "engaging plots, and satisfying arcs. You understand genre conventions and "
        "narrative structure deeply."
    )
    user_prompt = build_prompt(genre, premise, chapters, characters)
    messages = [{"role": "user", "content": user_prompt}]
    return chat(messages, system_prompt=system_prompt, temperature=0.8, max_tokens=4096)


@click.command()
@click.option("--genre", type=click.Choice(GENRES, case_sensitive=False), required=True, help="Story genre.")
@click.option("--premise", required=True, help="Story premise or concept.")
@click.option("--chapters", default=10, type=int, help="Number of chapters.")
@click.option("--characters", default=4, type=int, help="Number of main characters.")
@click.option("--output", "-o", default=None, help="Save output to file.")
def main(genre: str, premise: str, chapters: int, characters: int, output: str):
    """Create detailed story/novel outlines with characters and plot."""
    console.print(Panel.fit("[bold magenta]Story Outline Generator[/bold magenta]", border_style="magenta"))

    if not check_ollama_running():
        console.print("[red]Error: Ollama is not running. Start it with: ollama serve[/red]")
        sys.exit(1)

    console.print(f"[cyan]Genre:[/cyan] {genre}")
    console.print(f"[cyan]Premise:[/cyan] {premise}")
    console.print(f"[cyan]Chapters:[/cyan] {chapters}")
    console.print(f"[cyan]Characters:[/cyan] {characters}")
    console.print()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        progress.add_task("Creating story outline...", total=None)
        result = generate_outline(genre, premise, chapters, characters)

    console.print(Panel(Markdown(result), title="📖 Story Outline", border_style="magenta"))

    if output:
        with open(output, "w", encoding="utf-8") as f:
            f.write(result)
        console.print(f"[green]Saved to {output}[/green]")


if __name__ == "__main__":
    main()
