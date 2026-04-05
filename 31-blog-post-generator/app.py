#!/usr/bin/env python3
"""Blog Post Generator - Generate SEO-friendly blog posts using a local LLM."""

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

TONES = ["professional", "casual", "technical", "friendly", "persuasive"]


def build_prompt(topic: str, keywords: list[str], tone: str, length: int) -> str:
    """Build the blog post generation prompt."""
    kw_str = ", ".join(keywords) if keywords else "none specified"
    return (
        f"Write a {length}-word SEO-friendly blog post about: {topic}\n\n"
        f"Requirements:\n"
        f"- Tone: {tone}\n"
        f"- Target keywords to include naturally: {kw_str}\n"
        f"- Include an engaging title (prefixed with '# ')\n"
        f"- Include a meta description (1-2 sentences, prefixed with '> ')\n"
        f"- Use proper markdown headings (##, ###) for sections\n"
        f"- Include an introduction, 3-4 main sections, and a conclusion\n"
        f"- Optimize for SEO with keyword placement in headings and first paragraphs\n"
        f"- Approximate length: {length} words\n"
    )


def generate_blog_post(topic: str, keywords: list[str], tone: str, length: int) -> str:
    """Generate a blog post using the LLM."""
    system_prompt = (
        "You are an expert content writer and SEO specialist. "
        "You write engaging, well-structured blog posts optimized for search engines. "
        "Always output in clean markdown format."
    )
    user_prompt = build_prompt(topic, keywords, tone, length)
    messages = [{"role": "user", "content": user_prompt}]
    return chat(messages, system_prompt=system_prompt, temperature=0.7, max_tokens=length * 3)


@click.command()
@click.option("--topic", required=True, help="Blog post topic.")
@click.option("--keywords", default="", help="Comma-separated SEO keywords.")
@click.option(
    "--tone",
    type=click.Choice(TONES, case_sensitive=False),
    default="professional",
    help="Writing tone.",
)
@click.option("--length", default=800, type=int, help="Approximate word count.")
@click.option("--output", "-o", default=None, help="Save output to file.")
def main(topic: str, keywords: str, tone: str, length: int, output: str):
    """Generate SEO-friendly blog posts from a topic and keywords."""
    console.print(Panel.fit("[bold blue]Blog Post Generator[/bold blue]", border_style="blue"))

    if not check_ollama_running():
        console.print("[red]Error: Ollama is not running. Start it with: ollama serve[/red]")
        sys.exit(1)

    kw_list = [k.strip() for k in keywords.split(",") if k.strip()] if keywords else []

    console.print(f"[cyan]Topic:[/cyan] {topic}")
    console.print(f"[cyan]Keywords:[/cyan] {', '.join(kw_list) if kw_list else 'None'}")
    console.print(f"[cyan]Tone:[/cyan] {tone}")
    console.print(f"[cyan]Target Length:[/cyan] ~{length} words")
    console.print()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        progress.add_task("Generating blog post...", total=None)
        result = generate_blog_post(topic, kw_list, tone, length)

    console.print(Panel(Markdown(result), title="Generated Blog Post", border_style="green"))

    word_count = len(result.split())
    console.print(f"\n[dim]Word count: ~{word_count}[/dim]")

    if output:
        with open(output, "w", encoding="utf-8") as f:
            f.write(result)
        console.print(f"[green]Saved to {output}[/green]")


if __name__ == "__main__":
    main()
