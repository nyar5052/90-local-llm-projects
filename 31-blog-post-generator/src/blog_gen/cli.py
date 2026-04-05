#!/usr/bin/env python3
"""CLI interface for Blog Post Generator."""

import sys
import os
import logging

import click
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

from blog_gen.core import (
    TONES,
    build_prompt,
    generate_blog_post,
    generate_outline,
    generate_multiple_drafts,
    score_seo,
    analyze_tone,
    export_markdown,
    parse_blog_post,
    load_config,
    setup_logging,
)

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
from common.llm_client import check_ollama_running  # noqa: E402

logger = logging.getLogger(__name__)
console = Console()


def _render_seo_table(seo: dict) -> Table:
    """Build a rich Table showing the SEO score breakdown."""
    table = Table(title="SEO Analysis Report", show_header=True, header_style="bold cyan")
    table.add_column("Criterion", style="bold")
    table.add_column("Score", justify="right")
    table.add_column("Max", justify="right")
    table.add_column("Rating", justify="center")

    criteria = [
        ("Keyword Density", "keyword_density", 30),
        ("Heading Structure", "heading_structure", 25),
        ("Meta Description", "meta_description", 20),
        ("Content Length", "content_length", 25),
    ]

    for label, key, max_score in criteria:
        score = seo.get(key, 0)
        pct = score / max_score if max_score else 0
        if pct >= 0.8:
            rating = "[green]★★★[/green]"
        elif pct >= 0.5:
            rating = "[yellow]★★☆[/yellow]"
        else:
            rating = "[red]★☆☆[/red]"
        table.add_row(label, f"{score:.1f}", str(max_score), rating)

    total = seo.get("total", 0)
    if total >= 80:
        color = "green"
    elif total >= 50:
        color = "yellow"
    else:
        color = "red"
    table.add_row("", "", "", "")
    table.add_row("[bold]TOTAL[/bold]", f"[bold {color}]{total:.1f}[/bold {color}]", "100", "")

    return table


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
@click.option("--output", "-o", default=None, help="Save raw output to file.")
@click.option("--drafts", default=1, type=int, help="Number of drafts to generate (1-5).")
@click.option("--outline", is_flag=True, default=False, help="Preview outline before generating.")
@click.option("--seo-report", is_flag=True, default=False, help="Show SEO analysis report.")
@click.option("--export-md", default=None, help="Export to markdown file with frontmatter.")
def main(
    topic: str,
    keywords: str,
    tone: str,
    length: int,
    output: str,
    drafts: int,
    outline: bool,
    seo_report: bool,
    export_md: str,
) -> None:
    """Generate SEO-friendly blog posts from a topic and keywords."""
    setup_logging()
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

    # --- Outline preview ---
    if outline:
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as prog:
            prog.add_task("Generating outline...", total=None)
            outline_text = generate_outline(topic, kw_list, tone)
        console.print(Panel(Markdown(outline_text), title="Outline Preview", border_style="yellow"))
        console.print()

    # --- Generate posts ---
    if drafts > 1:
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as prog:
            prog.add_task(f"Generating {drafts} drafts...", total=None)
            results = generate_multiple_drafts(topic, kw_list, tone, length, num_drafts=drafts)

        for idx, draft in enumerate(results, 1):
            console.print(Panel(Markdown(draft), title=f"Draft {idx}/{len(results)}", border_style="green"))
            word_count = len(draft.split())
            console.print(f"[dim]Word count: ~{word_count}[/dim]\n")

            if seo_report:
                seo = score_seo(draft, kw_list)
                console.print(_render_seo_table(seo))
                console.print()

        result = results[0]  # primary draft for export
    else:
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as prog:
            prog.add_task("Generating blog post...", total=None)
            result = generate_blog_post(topic, kw_list, tone, length)

        console.print(Panel(Markdown(result), title="Generated Blog Post", border_style="green"))
        word_count = len(result.split())
        console.print(f"\n[dim]Word count: ~{word_count}[/dim]")

    # --- SEO report ---
    if seo_report and drafts <= 1:
        seo = score_seo(result, kw_list)
        console.print()
        console.print(_render_seo_table(seo))

    # --- Tone analysis (included with SEO report) ---
    if seo_report:
        tone_result = analyze_tone(result)
        console.print()
        tone_table = Table(title="Tone Analysis", show_header=True, header_style="bold magenta")
        tone_table.add_column("Tone", style="bold")
        tone_table.add_column("Confidence", justify="right")
        for t in TONES:
            conf = tone_result.get(t, 0)
            bar = "█" * int(conf * 20)
            tone_table.add_row(t.capitalize(), f"{conf:.0%} {bar}")
        tone_table.add_row("", "")
        tone_table.add_row("[bold]Dominant[/bold]", f"[bold]{tone_result.get('dominant_tone', 'N/A').capitalize()}[/bold]")
        console.print(tone_table)

    # --- Save raw output ---
    if output:
        with open(output, "w", encoding="utf-8") as f:
            f.write(result)
        console.print(f"\n[green]Saved to {output}[/green]")

    # --- Export markdown with frontmatter ---
    if export_md:
        path = export_markdown(result, export_md, keywords=kw_list)
        console.print(f"[green]Exported markdown with frontmatter to {path}[/green]")


if __name__ == "__main__":
    main()
