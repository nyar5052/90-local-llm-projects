#!/usr/bin/env python3
"""Product Description Writer - Generate e-commerce product descriptions using a local LLM."""

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

PLATFORMS = ["amazon", "shopify", "etsy", "ebay", "generic"]
LENGTHS = ["short", "medium", "long"]


def build_prompt(
    product: str, features: list[str], platform: str, length: str, variants: int
) -> str:
    """Build the product description generation prompt."""
    feat_str = "\n".join(f"- {f.strip()}" for f in features) if features else "- Not specified"

    length_guide = {
        "short": "50-100 words",
        "medium": "150-250 words",
        "long": "300-500 words",
    }

    platform_tips = {
        "amazon": "Use bullet points for features, include A+ content structure, focus on benefits over features.",
        "shopify": "Storytelling approach, lifestyle-focused, brand voice consistency.",
        "etsy": "Handmade/unique angle, personal touch, craftsmanship details.",
        "ebay": "Clear specifications, condition details, competitive positioning.",
        "generic": "Versatile format suitable for any e-commerce platform.",
    }

    return (
        f"Create {variants} product description variant(s) for:\n\n"
        f"**Product:** {product}\n"
        f"**Key Features:**\n{feat_str}\n\n"
        f"**Platform:** {platform}\n"
        f"**Platform Tips:** {platform_tips[platform]}\n"
        f"**Length:** {length_guide[length]}\n\n"
        f"For each variant provide:\n"
        f"1. **Product Title** (SEO-optimized, keyword-rich)\n"
        f"2. **Short Description** (1-2 sentences for search results)\n"
        f"3. **Full Description** (complete product copy)\n"
        f"4. **Bullet Points** (5-7 key selling points)\n"
        f"5. **SEO Keywords** (10 relevant search terms)\n\n"
        f"Label each variant as 'Variant 1:', 'Variant 2:', etc.\n"
        f"Focus on benefits, use power words, and create urgency.\n"
    )


def generate_descriptions(
    product: str, features: list[str], platform: str, length: str, variants: int
) -> str:
    """Generate product descriptions using the LLM."""
    system_prompt = (
        "You are an expert e-commerce copywriter and SEO specialist. "
        "You write product descriptions that convert browsers into buyers. "
        "You understand platform-specific best practices and consumer psychology."
    )
    user_prompt = build_prompt(product, features, platform, length, variants)
    messages = [{"role": "user", "content": user_prompt}]
    return chat(messages, system_prompt=system_prompt, temperature=0.7, max_tokens=4096)


@click.command()
@click.option("--product", required=True, help="Product name.")
@click.option("--features", default="", help="Comma-separated product features.")
@click.option(
    "--platform",
    type=click.Choice(PLATFORMS, case_sensitive=False),
    default="generic",
    help="E-commerce platform.",
)
@click.option(
    "--length",
    type=click.Choice(LENGTHS, case_sensitive=False),
    default="medium",
    help="Description length.",
)
@click.option("--variants", default=2, type=int, help="Number of variants to generate.")
@click.option("--output", "-o", default=None, help="Save output to file.")
def main(product: str, features: str, platform: str, length: str, variants: int, output: str):
    """Generate SEO-optimized e-commerce product descriptions."""
    console.print(Panel.fit("[bold yellow]Product Description Writer[/bold yellow]", border_style="yellow"))

    if not check_ollama_running():
        console.print("[red]Error: Ollama is not running. Start it with: ollama serve[/red]")
        sys.exit(1)

    feat_list = [f.strip() for f in features.split(",") if f.strip()] if features else []

    console.print(f"[cyan]Product:[/cyan] {product}")
    console.print(f"[cyan]Features:[/cyan] {', '.join(feat_list) if feat_list else 'None specified'}")
    console.print(f"[cyan]Platform:[/cyan] {platform}")
    console.print(f"[cyan]Length:[/cyan] {length}")
    console.print(f"[cyan]Variants:[/cyan] {variants}")
    console.print()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        progress.add_task("Writing product descriptions...", total=None)
        result = generate_descriptions(product, feat_list, platform, length, variants)

    console.print(Panel(Markdown(result), title="🛒 Product Descriptions", border_style="yellow"))

    if output:
        with open(output, "w", encoding="utf-8") as f:
            f.write(result)
        console.print(f"[green]Saved to {output}[/green]")


if __name__ == "__main__":
    main()
