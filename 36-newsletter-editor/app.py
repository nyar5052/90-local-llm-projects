#!/usr/bin/env python3
"""Newsletter Editor - Curate and rewrite content into newsletter format using a local LLM."""

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


def read_input_file(filepath: str) -> str:
    """Read raw notes/content from a file."""
    if not os.path.exists(filepath):
        console.print(f"[red]Error: File not found: {filepath}[/red]")
        sys.exit(1)
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()


def build_prompt(raw_content: str, name: str, sections: int, tone: str) -> str:
    """Build the newsletter generation prompt."""
    return (
        f"Transform the following raw notes into a polished, professional newsletter.\n\n"
        f"Newsletter Name: {name}\n"
        f"Number of Sections: {sections}\n"
        f"Tone: {tone}\n\n"
        f"Raw Notes/Content:\n---\n{raw_content}\n---\n\n"
        f"Requirements:\n"
        f"1. Create a compelling newsletter header with the name and a tagline\n"
        f"2. Write an engaging editorial intro (2-3 sentences)\n"
        f"3. Organize the content into {sections} distinct sections with:\n"
        f"   - Section title (catchy and descriptive)\n"
        f"   - Rewritten content (clear, concise, engaging)\n"
        f"   - Key takeaway or action item for each section\n"
        f"4. Add a brief closing/sign-off\n"
        f"5. Use markdown formatting throughout\n"
        f"6. Add relevant emoji for visual appeal\n"
        f"7. If the raw notes mention links/URLs, preserve them\n"
    )


def generate_newsletter(raw_content: str, name: str, sections: int, tone: str) -> str:
    """Generate a newsletter using the LLM."""
    system_prompt = (
        "You are an expert newsletter editor and content curator. "
        "You transform raw, unstructured notes into polished, engaging newsletters "
        "that readers love. You have a keen eye for storytelling and information hierarchy."
    )
    user_prompt = build_prompt(raw_content, name, sections, tone)
    messages = [{"role": "user", "content": user_prompt}]
    return chat(messages, system_prompt=system_prompt, temperature=0.7, max_tokens=4096)


@click.command()
@click.option("--input", "input_file", required=True, help="Path to raw notes/content file.")
@click.option("--name", required=True, help="Newsletter name.")
@click.option("--sections", default=4, type=int, help="Number of newsletter sections.")
@click.option("--tone", default="informative", help="Writing tone (e.g., informative, casual, witty).")
@click.option("--output", "-o", default=None, help="Save output to file.")
def main(input_file: str, name: str, sections: int, tone: str, output: str):
    """Curate and rewrite content into polished newsletter format."""
    console.print(Panel.fit("[bold green]Newsletter Editor[/bold green]", border_style="green"))

    if not check_ollama_running():
        console.print("[red]Error: Ollama is not running. Start it with: ollama serve[/red]")
        sys.exit(1)

    raw_content = read_input_file(input_file)
    console.print(f"[cyan]Input:[/cyan] {input_file} ({len(raw_content)} chars)")
    console.print(f"[cyan]Newsletter:[/cyan] {name}")
    console.print(f"[cyan]Sections:[/cyan] {sections}")
    console.print(f"[cyan]Tone:[/cyan] {tone}")
    console.print()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        progress.add_task("Editing newsletter...", total=None)
        result = generate_newsletter(raw_content, name, sections, tone)

    console.print(Panel(Markdown(result), title=f"📰 {name}", border_style="green"))

    if output:
        with open(output, "w", encoding="utf-8") as f:
            f.write(result)
        console.print(f"[green]Saved to {output}[/green]")


if __name__ == "__main__":
    main()
