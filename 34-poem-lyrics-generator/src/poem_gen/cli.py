#!/usr/bin/env python3
"""CLI for Poem & Lyrics Generator."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from common.llm_client import check_ollama_running  # noqa: E402
from poem_gen.core import (  # noqa: E402
    STYLES,
    MOODS,
    Poem,
    generate_poem,
    generate_with_rhyme_scheme,
    mix_styles,
    analyze_poem,
    format_poem,
    manage_collection,
)

console = Console()


def _display_analysis(text: str) -> None:
    """Render poem analysis in a Rich table."""
    analysis = analyze_poem(text)
    table = Table(title="📊 Poem Analysis", border_style="blue")
    table.add_column("Metric", style="cyan", no_wrap=True)
    table.add_column("Value", style="white")
    table.add_row("Lines", str(analysis["line_count"]))
    table.add_row("Words", str(analysis["word_count"]))
    table.add_row("Rhyme Scheme", analysis["detected_rhyme_scheme"] or "—")
    syllables = analysis["syllables_per_line"]
    if syllables:
        syl_str = ", ".join(str(s) for s in syllables)
        table.add_row("Syllables/Line", syl_str)
    console.print(table)


@click.command()
@click.option("--theme", required=False, default=None, help="Theme or subject for the poem/lyrics.")
@click.option(
    "--style",
    type=click.Choice(STYLES, case_sensitive=False),
    default="free-verse",
    help="Poetic style.",
)
@click.option(
    "--mood",
    type=click.Choice(MOODS, case_sensitive=False),
    default=None,
    help="Mood/emotion.",
)
@click.option("--title", default=None, help="Specify a title (auto-generated if omitted).")
@click.option("--output", "-o", default=None, help="Save output to file.")
@click.option(
    "--rhyme-scheme",
    default=None,
    help="Generate with a specific rhyme scheme (e.g. ABAB, AABB).",
)
@click.option(
    "--mix-styles",
    "mix_styles_opt",
    default=None,
    help="Mix two styles (comma-separated, e.g. 'haiku,rap').",
)
@click.option("--analyze", "do_analyze", is_flag=True, help="Show poem analysis after generation.")
@click.option(
    "--collection",
    default=None,
    help="Save generated poem to a named collection.",
)
@click.option(
    "--list-collection",
    default=None,
    help="Display poems in a saved collection (no generation).",
)
def main(
    theme: str | None,
    style: str,
    mood: str | None,
    title: str | None,
    output: str | None,
    rhyme_scheme: str | None,
    mix_styles_opt: str | None,
    do_analyze: bool,
    collection: str | None,
    list_collection: str | None,
):
    """🎭 Generate poems or song lyrics from themes and styles."""
    console.print(
        Panel.fit(
            "[bold cyan]✨ Poem & Lyrics Generator v2.0[/bold cyan]",
            border_style="cyan",
        )
    )

    # --list-collection: display and exit
    if list_collection:
        coll = manage_collection(list_collection, "list")
        if not coll.poems:
            console.print(f"[yellow]Collection '{list_collection}' is empty.[/yellow]")
            return
        console.print(f"[bold cyan]Collection:[/bold cyan] {coll.name}  ({len(coll.poems)} poems)\n")
        for i, p in enumerate(coll.poems, 1):
            console.print(
                Panel(
                    p.content,
                    title=f"#{i} — {p.title}  [{p.style}]",
                    border_style="magenta",
                )
            )
        return

    # Require --theme for generation
    if not theme:
        console.print("[red]Error: --theme is required for poem generation.[/red]")
        sys.exit(1)

    if not check_ollama_running():
        console.print("[red]Error: Ollama is not running. Start it with: ollama serve[/red]")
        sys.exit(1)

    # Display parameters
    console.print(f"[cyan]Theme:[/cyan] {theme}")
    console.print(f"[cyan]Style:[/cyan] {style}")
    if mood:
        console.print(f"[cyan]Mood:[/cyan] {mood}")
    if title:
        console.print(f"[cyan]Title:[/cyan] {title}")
    if rhyme_scheme:
        console.print(f"[cyan]Rhyme Scheme:[/cyan] {rhyme_scheme}")
    if mix_styles_opt:
        console.print(f"[cyan]Mix Styles:[/cyan] {mix_styles_opt}")
    console.print()

    # Generate
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        progress.add_task(f"Composing {style}...", total=None)

        if mix_styles_opt:
            parts = [s.strip() for s in mix_styles_opt.split(",")]
            if len(parts) < 2:
                console.print("[red]--mix-styles requires two comma-separated styles.[/red]")
                sys.exit(1)
            result = mix_styles(theme, parts, mood)
        elif rhyme_scheme:
            result = generate_with_rhyme_scheme(theme, rhyme_scheme, mood)
        else:
            result = generate_poem(theme, style, mood, title)

    # Format and display
    formatted = format_poem(result, style)
    border = "magenta" if mood in ("romantic", "melancholic") else "cyan"
    console.print(Panel(formatted, title=f"✨ {style.title()}", border_style=border))

    # Analysis
    if do_analyze:
        _display_analysis(result)

    # Save to file
    if output:
        with open(output, "w", encoding="utf-8") as f:
            f.write(result)
        console.print(f"[green]✅ Saved to {output}[/green]")

    # Save to collection
    if collection:
        poem_obj = Poem(
            title=title or "Untitled",
            content=result,
            style=style,
            mood=mood,
            theme=theme,
        )
        coll = manage_collection(collection, "add", poem_obj)
        console.print(
            f"[green]✅ Added to collection '{collection}' "
            f"({len(coll.poems)} poems total)[/green]"
        )


if __name__ == "__main__":
    main()
