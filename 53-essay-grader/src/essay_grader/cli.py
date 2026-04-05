#!/usr/bin/env python3
"""
Essay Grader CLI — Command-line interface for grading essays.
"""

import sys
import os
import json
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from src.essay_grader.core import (
    check_ollama_running,
    read_essay,
    grade_essay,
    generate_annotations,
    export_grade_report,
    calculate_grade_letter,
    validate_grade_data,
    PRESET_RUBRICS,
    ConfigManager,
    setup_logging,
)

console = Console()

DEFAULT_RUBRIC_CSV = "clarity,argument,evidence,organization,grammar"


def _display_grade(grade_data: dict) -> None:
    """Display grading results in a rich format."""
    overall = grade_data.get("overall_score", "N/A")
    grade = grade_data.get("overall_grade", "N/A")

    color = (
        "green" if isinstance(overall, (int, float)) and overall >= 7
        else "yellow" if isinstance(overall, (int, float)) and overall >= 5
        else "red"
    )

    console.print(Panel(
        f"[bold {color}]Overall Score: {overall}/10 ({grade})[/bold {color}]",
        title="Essay Grade",
        border_style=color,
    ))

    table = Table(title="Rubric Scores", show_lines=True)
    table.add_column("Criterion", style="cyan", width=20)
    table.add_column("Score", style="bold", width=10)
    table.add_column("Feedback", style="white", ratio=3)

    for c in grade_data.get("criteria", []):
        score = c.get("score", 0)
        max_s = c.get("max_score", 10)
        s_color = "green" if score >= 7 else "yellow" if score >= 5 else "red"
        table.add_row(
            c.get("name", "").replace("_", " ").title(),
            f"[{s_color}]{score}/{max_s}[/{s_color}]",
            c.get("feedback", ""),
        )
    console.print(table)

    if grade_data.get("strengths"):
        console.print("\n[bold green]✓ Strengths:[/bold green]")
        for s in grade_data["strengths"]:
            console.print(f"  • {s}")

    if grade_data.get("weaknesses"):
        console.print("\n[bold red]✗ Weaknesses:[/bold red]")
        for w in grade_data["weaknesses"]:
            console.print(f"  • {w}")

    if grade_data.get("suggestions"):
        console.print("\n[bold yellow]💡 Suggestions:[/bold yellow]")
        for s in grade_data["suggestions"]:
            console.print(f"  • {s}")

    if grade_data.get("summary"):
        console.print(Panel(grade_data["summary"], title="Summary", border_style="blue"))


# ---------------------------------------------------------------------------
# CLI group
# ---------------------------------------------------------------------------

@click.group()
def cli():
    """📝 Essay Grader — Grade essays with detailed feedback using a local LLM."""
    cfg = ConfigManager.get_instance()
    setup_logging(
        level=cfg.get("logging", "level", default="INFO"),
        log_file=cfg.get("logging", "file"),
    )


# ---------------------------------------------------------------------------
# grade command
# ---------------------------------------------------------------------------

@cli.command()
@click.option("--essay", "-e", required=True, type=click.Path(exists=True),
              help="Path to essay text file")
@click.option("--rubric", "-r", default=None,
              help="Rubric preset name or comma-separated criteria")
@click.option("--context", "-c", default="", help="Assignment context or prompt")
@click.option("--output", "-o", type=click.Path(), help="Save results to file")
@click.option("--annotate", is_flag=True, help="Include inline annotations")
def grade(essay, rubric, context, output, annotate):
    """Grade an essay with rubric-based scoring."""
    console.print(Panel("[bold blue]📝 Essay Grader[/bold blue]", subtitle="Powered by Local LLM"))

    if not check_ollama_running():
        console.print("[red]Error: Ollama is not running. Start with: ollama serve[/red]")
        sys.exit(1)

    essay_text = read_essay(essay)
    console.print(f"[cyan]Grading essay from '{essay}'...[/cyan]")

    rubric_obj = None
    rubric_criteria = None
    if rubric and rubric in PRESET_RUBRICS:
        rubric_obj = PRESET_RUBRICS[rubric]
        console.print(f"[dim]Using preset rubric: {rubric_obj.name}[/dim]")
    elif rubric:
        rubric_criteria = [c.strip() for c in rubric.split(",")]
        console.print(f"[dim]Rubric: {', '.join(rubric_criteria)}[/dim]")
    else:
        cfg = ConfigManager.get_instance()
        default_name = cfg.get("grading", "default_rubric", default="academic")
        rubric_obj = PRESET_RUBRICS.get(default_name)
        if rubric_obj:
            console.print(f"[dim]Using default preset rubric: {rubric_obj.name}[/dim]")
        else:
            rubric_criteria = [c.strip() for c in DEFAULT_RUBRIC_CSV.split(",")]

    with console.status("[bold green]Analyzing essay..."):
        grade_data = grade_essay(
            essay_text,
            rubric_criteria=rubric_criteria,
            rubric=rubric_obj,
            context=context,
        )

    _display_grade(grade_data)

    if annotate:
        with console.status("[bold green]Generating annotations..."):
            annotations = generate_annotations(essay_text)
        if annotations:
            console.print("\n[bold cyan]📌 Inline Annotations:[/bold cyan]")
            for a in annotations:
                icon = {"error": "🔴", "warning": "🟡"}.get(a.severity, "🔵")
                console.print(f'  {icon} [{a.annotation_type}] "{a.text_segment[:60]}..." — {a.comment}')

    if output:
        fmt = "markdown" if output.endswith(".md") else "json"
        path = export_grade_report(grade_data, output, fmt=fmt, essay_text=essay_text)
        console.print(f"\n[green]✓ Results saved to {path}[/green]")


# ---------------------------------------------------------------------------
# rubrics command
# ---------------------------------------------------------------------------

@cli.command()
def rubrics():
    """List available rubric presets."""
    table = Table(title="Available Rubric Presets", show_lines=True)
    table.add_column("Name", style="cyan", width=20)
    table.add_column("Description", style="white", ratio=2)
    table.add_column("Criteria", style="dim", ratio=3)

    for key, r in PRESET_RUBRICS.items():
        criteria_names = ", ".join(c.name.replace("_", " ").title() for c in r.criteria)
        table.add_row(key, r.description, criteria_names)

    console.print(table)


# ---------------------------------------------------------------------------
# report command
# ---------------------------------------------------------------------------

@cli.command()
@click.option("--input", "-i", "input_file", required=True, type=click.Path(exists=True),
              help="Grade JSON file to convert")
@click.option("--format", "-f", "fmt", type=click.Choice(["markdown", "json"]), default="markdown",
              help="Output format")
@click.option("--output", "-o", type=click.Path(), help="Output file path")
def report(input_file, fmt, output):
    """Generate a report from grading results."""
    with open(input_file, "r", encoding="utf-8") as fh:
        grade_data = json.load(fh)

    if output is None:
        stem = Path(input_file).stem
        ext = ".md" if fmt == "markdown" else ".json"
        output = f"{stem}_report{ext}"

    path = export_grade_report(grade_data, output, fmt=fmt)
    console.print(f"[green]✓ Report generated: {path}[/green]")


# ---------------------------------------------------------------------------
# batch command
# ---------------------------------------------------------------------------

@cli.command()
@click.option("--directory", "-d", required=True, type=click.Path(exists=True, file_okay=False),
              help="Directory containing essay files")
@click.option("--rubric", "-r", default=None,
              help="Rubric preset name or comma-separated criteria")
@click.option("--output-dir", "-o", type=click.Path(), default="./reports",
              help="Output directory for grade reports")
def batch(directory, rubric, output_dir):
    """Grade all essays in a directory."""
    if not check_ollama_running():
        console.print("[red]Error: Ollama is not running. Start with: ollama serve[/red]")
        sys.exit(1)

    rubric_obj = PRESET_RUBRICS.get(rubric) if rubric and rubric in PRESET_RUBRICS else None
    rubric_criteria = [c.strip() for c in rubric.split(",")] if rubric and rubric_obj is None else None

    essay_dir = Path(directory)
    essay_files = sorted(
        p for p in essay_dir.iterdir()
        if p.is_file() and p.suffix in (".txt", ".md", ".text")
    )

    if not essay_files:
        console.print("[yellow]No essay files (.txt, .md) found in directory.[/yellow]")
        return

    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    console.print(f"[cyan]Grading {len(essay_files)} essay(s)...[/cyan]")

    for idx, ef in enumerate(essay_files, 1):
        console.print(f"\n[bold]({idx}/{len(essay_files)}) {ef.name}[/bold]")
        essay_text = read_essay(str(ef))

        with console.status("[bold green]Analyzing..."):
            grade_data = grade_essay(
                essay_text,
                rubric_criteria=rubric_criteria,
                rubric=rubric_obj,
            )

        _display_grade(grade_data)
        out_path = out / f"{ef.stem}_grade.json"
        export_grade_report(grade_data, str(out_path), fmt="json", essay_text=essay_text)
        console.print(f"[green]  ✓ Saved → {out_path}[/green]")

    console.print(f"\n[bold green]✓ Batch grading complete. Reports in {out}[/bold green]")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    cli()
