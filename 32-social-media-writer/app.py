#!/usr/bin/env python3
"""Social Media Writer - Create platform-specific social media posts using a local LLM."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from common.llm_client import chat, check_ollama_running

console = Console()

PLATFORMS = ["twitter", "linkedin", "instagram"]
TONES = ["professional", "casual", "excited", "informative", "humorous"]

PLATFORM_CONFIG = {
    "twitter": {"max_chars": 280, "name": "Twitter/X", "hashtag_count": 3},
    "linkedin": {"max_chars": 3000, "name": "LinkedIn", "hashtag_count": 5},
    "instagram": {"max_chars": 2200, "name": "Instagram", "hashtag_count": 15},
}


def build_prompt(platform: str, topic: str, tone: str, variants: int) -> str:
    """Build the social media post generation prompt."""
    config = PLATFORM_CONFIG[platform]
    return (
        f"Create {variants} {config['name']} post(s) about: {topic}\n\n"
        f"Requirements:\n"
        f"- Platform: {config['name']}\n"
        f"- Maximum character limit: {config['max_chars']} characters\n"
        f"- Tone: {tone}\n"
        f"- Include {config['hashtag_count']} relevant hashtags\n"
        f"- Each post should be engaging and shareable\n"
        f"- For Twitter: keep it concise and punchy\n"
        f"- For LinkedIn: be professional with a hook and CTA\n"
        f"- For Instagram: be visual-oriented with emoji usage\n"
        f"- Label each variant as 'Variant 1:', 'Variant 2:', etc.\n"
        f"- Add hashtags at the end of each post\n"
    )


def generate_posts(platform: str, topic: str, tone: str, variants: int) -> str:
    """Generate social media posts using the LLM."""
    system_prompt = (
        "You are a social media marketing expert. You create viral, engaging posts "
        "tailored to each platform's best practices and audience expectations. "
        "Always respect character limits and platform norms."
    )
    user_prompt = build_prompt(platform, topic, tone, variants)
    messages = [{"role": "user", "content": user_prompt}]
    return chat(messages, system_prompt=system_prompt, temperature=0.8, max_tokens=2048)


@click.command()
@click.option("--platform", type=click.Choice(PLATFORMS, case_sensitive=False), required=True, help="Target platform.")
@click.option("--topic", required=True, help="Post topic.")
@click.option("--tone", type=click.Choice(TONES, case_sensitive=False), default="professional", help="Writing tone.")
@click.option("--variants", default=2, type=int, help="Number of post variants.")
@click.option("--output", "-o", default=None, help="Save output to file.")
def main(platform: str, topic: str, tone: str, variants: int, output: str):
    """Create platform-specific social media posts."""
    console.print(Panel.fit("[bold magenta]Social Media Writer[/bold magenta]", border_style="magenta"))

    if not check_ollama_running():
        console.print("[red]Error: Ollama is not running. Start it with: ollama serve[/red]")
        sys.exit(1)

    config = PLATFORM_CONFIG[platform]
    info_table = Table(show_header=False, box=None)
    info_table.add_row("[cyan]Platform[/cyan]", config["name"])
    info_table.add_row("[cyan]Topic[/cyan]", topic)
    info_table.add_row("[cyan]Tone[/cyan]", tone)
    info_table.add_row("[cyan]Variants[/cyan]", str(variants))
    info_table.add_row("[cyan]Max Chars[/cyan]", str(config["max_chars"]))
    console.print(info_table)
    console.print()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        progress.add_task(f"Generating {config['name']} posts...", total=None)
        result = generate_posts(platform, topic, tone, variants)

    console.print(Panel(result, title=f"{config['name']} Posts", border_style="green"))

    if output:
        with open(output, "w", encoding="utf-8") as f:
            f.write(result)
        console.print(f"[green]Saved to {output}[/green]")


if __name__ == "__main__":
    main()
