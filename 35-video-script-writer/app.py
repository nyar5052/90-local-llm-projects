#!/usr/bin/env python3
"""Video Script Writer - Create YouTube/video scripts with timestamps and B-roll suggestions."""

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

STYLES = ["educational", "entertainment", "tutorial", "review", "vlog", "documentary"]


def build_prompt(topic: str, duration: int, style: str, audience: str | None) -> str:
    """Build the video script generation prompt."""
    audience_str = f"Target Audience: {audience}\n" if audience else ""
    return (
        f"Create a complete YouTube video script about: {topic}\n\n"
        f"Video Duration: {duration} minutes\n"
        f"Style: {style}\n"
        f"{audience_str}\n"
        f"Structure the script with:\n"
        f"1. **HOOK** (first 15 seconds) - grab viewer attention immediately\n"
        f"2. **INTRO** (30-60 seconds) - introduce the topic and what viewers will learn\n"
        f"3. **MAIN CONTENT** - divided into clear sections with timestamps\n"
        f"4. **OUTRO** (30 seconds) - summary, CTA (subscribe, like, comment)\n\n"
        f"For each section include:\n"
        f"- **[TIMESTAMP]** e.g., [0:00-0:30]\n"
        f"- **Script** (exact words to say)\n"
        f"- **[B-ROLL]** suggestions (visuals to show while speaking)\n"
        f"- **[ON-SCREEN TEXT]** any text overlays or graphics\n\n"
        f"Make it engaging, well-paced for a {duration}-minute video.\n"
        f"Include natural transitions between sections.\n"
    )


def generate_script(topic: str, duration: int, style: str, audience: str | None) -> str:
    """Generate a video script using the LLM."""
    system_prompt = (
        "You are a professional YouTube scriptwriter and content strategist. "
        "You create engaging, well-structured video scripts that keep viewers watching. "
        "You understand pacing, hooks, retention strategies, and platform best practices."
    )
    user_prompt = build_prompt(topic, duration, style, audience)
    messages = [{"role": "user", "content": user_prompt}]
    return chat(messages, system_prompt=system_prompt, temperature=0.7, max_tokens=4096)


@click.command()
@click.option("--topic", required=True, help="Video topic.")
@click.option("--duration", default=10, type=int, help="Target video duration in minutes.")
@click.option("--style", type=click.Choice(STYLES, case_sensitive=False), default="educational", help="Video style.")
@click.option("--audience", default=None, help="Target audience description.")
@click.option("--output", "-o", default=None, help="Save output to file.")
def main(topic: str, duration: int, style: str, audience: str | None, output: str):
    """Create YouTube/video scripts with intro, body, outro, and B-roll suggestions."""
    console.print(Panel.fit("[bold red]Video Script Writer[/bold red]", border_style="red"))

    if not check_ollama_running():
        console.print("[red]Error: Ollama is not running. Start it with: ollama serve[/red]")
        sys.exit(1)

    console.print(f"[cyan]Topic:[/cyan] {topic}")
    console.print(f"[cyan]Duration:[/cyan] {duration} minutes")
    console.print(f"[cyan]Style:[/cyan] {style}")
    if audience:
        console.print(f"[cyan]Audience:[/cyan] {audience}")
    console.print()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        progress.add_task("Writing video script...", total=None)
        result = generate_script(topic, duration, style, audience)

    console.print(Panel(Markdown(result), title="🎬 Video Script", border_style="red"))

    word_count = len(result.split())
    est_minutes = word_count / 150  # ~150 words per minute speaking rate
    console.print(f"\n[dim]Word count: ~{word_count} | Estimated speaking time: ~{est_minutes:.1f} min[/dim]")

    if output:
        with open(output, "w", encoding="utf-8") as f:
            f.write(result)
        console.print(f"[green]Saved to {output}[/green]")


if __name__ == "__main__":
    main()
