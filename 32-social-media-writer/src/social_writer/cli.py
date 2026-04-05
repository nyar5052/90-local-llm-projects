#!/usr/bin/env python3
"""CLI interface for Social Media Writer."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

from social_writer.core import (
    PLATFORMS,
    TONES,
    build_prompt,
    generate_posts,
    generate_hashtags,
    suggest_schedule,
    generate_ab_variants,
    format_for_platform,
    preview_post,
    validate_char_count,
    load_config,
    setup_logging,
    SocialPost,
    _get_platform_config,
)
from common.llm_client import check_ollama_running

console = Console()


def _show_preview_table(content: str, platform: str) -> None:
    """Display a Rich table with post preview metrics."""
    preview = preview_post(content, platform)
    config = _get_platform_config(platform)

    is_valid, count, limit = validate_char_count(content, platform)
    ratio = count / limit if limit else 0
    if ratio <= 0.8:
        bar_color = "green"
    elif ratio <= 1.0:
        bar_color = "yellow"
    else:
        bar_color = "red"

    table = Table(title=f"{config['name']} Post Preview", border_style="cyan")
    table.add_column("Metric", style="bold")
    table.add_column("Value")

    status = f"[{bar_color}]{count}/{limit}[/{bar_color}]"
    table.add_row("Characters", status)
    table.add_row("Within Limit", "✅ Yes" if is_valid else "❌ No")
    table.add_row("Hashtags Found", str(preview["hashtag_count"]))
    table.add_row("Reach Score", f"{preview['estimated_reach_score']}/100")

    console.print(table)


@click.command()
@click.option(
    "--platform",
    type=click.Choice(PLATFORMS, case_sensitive=False),
    default=None,
    help="Target platform (twitter/linkedin/instagram).",
)
@click.option("--topic", required=True, help="Post topic.")
@click.option(
    "--tone",
    type=click.Choice(TONES, case_sensitive=False),
    default="professional",
    help="Writing tone.",
)
@click.option("--variants", default=2, type=int, help="Number of post variants.")
@click.option("--output", "-o", default=None, help="Save output to file.")
@click.option("--hashtags", is_flag=True, help="Generate standalone hashtag suggestions.")
@click.option("--schedule", is_flag=True, help="Show best posting times.")
@click.option("--ab-test", is_flag=True, help="Generate A/B test variants.")
@click.option("--all-platforms", is_flag=True, help="Generate posts for all platforms.")
def main(
    platform: str,
    topic: str,
    tone: str,
    variants: int,
    output: str,
    hashtags: bool,
    schedule: bool,
    ab_test: bool,
    all_platforms: bool,
) -> None:
    """🚀 Social Media Writer - Create platform-specific social media posts."""
    setup_logging()

    console.print(
        Panel.fit(
            "[bold magenta]✨ Social Media Writer[/bold magenta]",
            border_style="magenta",
        )
    )

    if not platform and not all_platforms:
        console.print("[red]Error: Please specify --platform or --all-platforms.[/red]")
        sys.exit(1)

    if not check_ollama_running():
        console.print("[red]Error: Ollama is not running. Start it with: ollama serve[/red]")
        sys.exit(1)

    target_platforms = PLATFORMS if all_platforms else [platform]
    all_output: list[str] = []

    for plat in target_platforms:
        config = _get_platform_config(plat)

        # Info table
        info_table = Table(show_header=False, box=None, padding=(0, 2))
        info_table.add_row("[cyan]Platform[/cyan]", config["name"])
        info_table.add_row("[cyan]Topic[/cyan]", topic)
        info_table.add_row("[cyan]Tone[/cyan]", tone)
        info_table.add_row("[cyan]Variants[/cyan]", str(variants))
        info_table.add_row("[cyan]Max Chars[/cyan]", str(config["max_chars"]))
        console.print(info_table)
        console.print()

        # Schedule display
        if schedule:
            times = suggest_schedule(plat)
            sched_table = Table(title=f"📅 Best Posting Times for {config['name']}", border_style="blue")
            sched_table.add_column("Rank", style="bold")
            sched_table.add_column("Time")
            for i, t in enumerate(times, 1):
                sched_table.add_row(f"#{i}", t)
            console.print(sched_table)
            console.print()

        # Hashtag-only mode
        if hashtags:
            with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
                progress.add_task(f"Generating hashtags for {config['name']}...", total=None)
                tag_result = generate_hashtags(topic, plat)
            console.print(Panel(tag_result, title=f"# {config['name']} Hashtags", border_style="yellow"))
            all_output.append(f"--- {config['name']} Hashtags ---\n{tag_result}\n")
            console.print()
            continue

        # A/B test mode
        if ab_test:
            with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
                progress.add_task(f"Generating A/B variants for {config['name']}...", total=None)
                ab_result = generate_ab_variants(topic, plat, tone, variants)
            console.print(Panel(ab_result, title=f"🔬 {config['name']} A/B Test Variants", border_style="magenta"))
            _show_preview_table(ab_result, plat)
            all_output.append(f"--- {config['name']} A/B Variants ---\n{ab_result}\n")
            console.print()
            continue

        # Standard generation
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
            progress.add_task(f"Generating {config['name']} posts...", total=None)
            result = generate_posts(plat, topic, tone, variants)

        formatted = format_for_platform(result, plat)
        console.print(Panel(formatted, title=f"{config['name']} Posts", border_style="green"))
        _show_preview_table(formatted, plat)
        all_output.append(f"--- {config['name']} Posts ---\n{formatted}\n")
        console.print()

    if output:
        full_text = "\n".join(all_output)
        with open(output, "w", encoding="utf-8") as f:
            f.write(full_text)
        console.print(f"[green]✅ Saved to {output}[/green]")


if __name__ == "__main__":
    main()
