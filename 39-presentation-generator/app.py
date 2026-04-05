#!/usr/bin/env python3
"""Presentation Generator - Generate slide content with speaker notes using a local LLM."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import click
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from common.llm_client import chat, check_ollama_running

console = Console()

FORMATS = ["standard", "pecha-kucha", "lightning", "keynote"]


def build_prompt(topic: str, slides: int, audience: str, format_type: str) -> str:
    """Build the presentation generation prompt."""
    format_guides = {
        "standard": "Standard presentation with detailed slides and transitions.",
        "pecha-kucha": "20 slides × 20 seconds each. Concise, visual-focused.",
        "lightning": "5-minute lightning talk. Fast-paced, key points only.",
        "keynote": "Keynote-style with storytelling, big ideas, and minimal text per slide.",
    }

    return (
        f"Create a complete presentation about: {topic}\n\n"
        f"Number of Slides: {slides}\n"
        f"Target Audience: {audience}\n"
        f"Format: {format_type} - {format_guides[format_type]}\n\n"
        f"For EACH slide provide:\n\n"
        f"### Slide N: [Title]\n"
        f"**Content:**\n"
        f"- 3-5 bullet points (concise, impactful)\n"
        f"- Or a key quote/statistic\n\n"
        f"**Visual Suggestion:** Describe an ideal image, chart, or diagram\n\n"
        f"**Speaker Notes:** 3-5 sentences of what to say (conversational tone)\n\n"
        f"**Transition:** How to segue to the next slide\n\n"
        f"---\n\n"
        f"Include these slide types:\n"
        f"- Title slide (slide 1)\n"
        f"- Agenda/overview slide (slide 2)\n"
        f"- Content slides with varied layouts\n"
        f"- At least one data/statistics slide\n"
        f"- Q&A or discussion slide\n"
        f"- Closing/thank you slide (last)\n"
    )


def generate_presentation(topic: str, slides: int, audience: str, format_type: str) -> str:
    """Generate a presentation using the LLM."""
    system_prompt = (
        "You are a presentation design expert and public speaking coach. "
        "You create compelling slide decks that balance visuals with content. "
        "You understand how to structure information for maximum audience engagement "
        "and retention."
    )
    user_prompt = build_prompt(topic, slides, audience, format_type)
    messages = [{"role": "user", "content": user_prompt}]
    return chat(messages, system_prompt=system_prompt, temperature=0.7, max_tokens=4096)


@click.command()
@click.option("--topic", required=True, help="Presentation topic.")
@click.option("--slides", default=12, type=int, help="Number of slides.")
@click.option("--audience", default="general", help="Target audience.")
@click.option(
    "--format",
    "format_type",
    type=click.Choice(FORMATS, case_sensitive=False),
    default="standard",
    help="Presentation format.",
)
@click.option("--output", "-o", default=None, help="Save output to file.")
def main(topic: str, slides: int, audience: str, format_type: str, output: str):
    """Generate presentation slide content with speaker notes."""
    console.print(Panel.fit("[bold blue]Presentation Generator[/bold blue]", border_style="blue"))

    if not check_ollama_running():
        console.print("[red]Error: Ollama is not running. Start it with: ollama serve[/red]")
        sys.exit(1)

    console.print(f"[cyan]Topic:[/cyan] {topic}")
    console.print(f"[cyan]Slides:[/cyan] {slides}")
    console.print(f"[cyan]Audience:[/cyan] {audience}")
    console.print(f"[cyan]Format:[/cyan] {format_type}")
    console.print()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        progress.add_task("Generating presentation...", total=None)
        result = generate_presentation(topic, slides, audience, format_type)

    console.print(Panel(Markdown(result), title="📊 Presentation", border_style="blue"))

    if output:
        with open(output, "w", encoding="utf-8") as f:
            f.write(result)
        console.print(f"[green]Saved to {output}[/green]")


if __name__ == "__main__":
    main()
