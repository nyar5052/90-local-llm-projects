#!/usr/bin/env python3
"""
Curriculum Planner CLI — Click-based command-line interface.
"""

import sys
import os
import json

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.tree import Tree

from .core import (
    ConfigManager,
    check_ollama_running,
    generate_curriculum,
    validate_curriculum_data,
    build_course_design,
    export_curriculum,
    setup_logging,
    OutcomeMapper,
    AssessmentPlanner,
    ResourceSuggester,
    PrerequisiteTracker,
    LearningOutcome,
    Prerequisite,
)

console = Console()


def _load_curriculum_file(path: str) -> dict:
    """Load a curriculum JSON file."""
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        console.print(f"[red]Error loading curriculum file: {exc}[/red]")
        raise SystemExit(1) from exc


# ---------------------------------------------------------------------------
# CLI group
# ---------------------------------------------------------------------------

@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """📚 Curriculum Planner — Design production-grade course curricula."""
    ctx.ensure_object(dict)
    cfg = ConfigManager()
    setup_logging(cfg)
    ctx.obj["config"] = cfg
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


# ---------------------------------------------------------------------------
# design command
# ---------------------------------------------------------------------------

@cli.command()
@click.option("--course", "-c", required=True, help="Course name (e.g., 'Intro to ML')")
@click.option("--weeks", "-w", default=12, type=int, help="Duration in weeks (default: 12)")
@click.option("--level", "-l", type=click.Choice(["beginner", "intermediate", "advanced"]),
              default="beginner", help="Student level")
@click.option("--focus", "-f", default="", help="Special focus areas (comma-separated)")
@click.option("--output", "-o", type=click.Path(), default=None, help="Save curriculum to file")
@click.pass_context
def design(ctx, course, weeks, level, focus, output):
    """Design a comprehensive course curriculum."""
    cfg = ctx.obj["config"]

    console.print(Panel("[bold blue]📚 Curriculum Planner[/bold blue]",
                        subtitle="Powered by Local LLM"))

    if not check_ollama_running():
        console.print("[red]Error: Ollama is not running. Start with: ollama serve[/red]")
        raise SystemExit(1)

    console.print(f"[cyan]Designing {weeks}-week curriculum for '{course}' ({level})...[/cyan]")

    with console.status("[bold green]Planning curriculum..."):
        data = generate_curriculum(course, weeks, level, focus, cfg=cfg)

    issues = validate_curriculum_data(data)
    if issues:
        console.print("[yellow]Validation warnings:[/yellow]")
        for issue in issues:
            console.print(f"  ⚠  {issue}")

    _display_curriculum(data)

    if output:
        fmt = "markdown" if output.endswith(".md") else "json"
        export_curriculum(data, output, fmt=fmt)
        console.print(f"\n[green]✓ Curriculum saved to {output}[/green]")


# ---------------------------------------------------------------------------
# outcomes command
# ---------------------------------------------------------------------------

@cli.command()
@click.option("--curriculum-file", "-f", required=True, type=click.Path(exists=True),
              help="Path to curriculum JSON file")
@click.argument("action", type=click.Choice(["list", "map", "check"]))
def outcomes(curriculum_file, action):
    """Manage learning outcomes: list, map, or check coverage."""
    data = _load_curriculum_file(curriculum_file)
    design_obj = build_course_design(data)

    if not design_obj.outcomes:
        # Build outcomes from objectives if none exist
        for i, obj in enumerate(design_obj.objectives, 1):
            design_obj.outcomes.append(LearningOutcome(id=f"LO-{i}", description=obj))

    mapper = OutcomeMapper(design_obj.outcomes, design_obj.weekly_plan)

    if action == "list":
        console.print("[bold cyan]🎯 Learning Outcomes:[/bold cyan]")
        for o in design_obj.outcomes:
            console.print(f"  [{o.bloom_level}] {o.id}: {o.description}")
    elif action == "map":
        matrix = mapper.generate_outcome_matrix()
        table = Table(title="Outcome-Week Matrix", show_lines=True)
        week_nums = sorted(w.week for w in design_obj.weekly_plan)
        table.add_column("Outcome", style="bold")
        for wn in week_nums:
            table.add_column(f"W{wn}", justify="center", width=4)
        for row in matrix:
            table.add_row(*row)
        console.print(table)
    elif action == "check":
        uncovered = mapper.check_coverage()
        if uncovered:
            console.print("[yellow]⚠ Uncovered outcomes:[/yellow]")
            for o in uncovered:
                console.print(f"  • {o.id}: {o.description}")
        else:
            console.print("[green]✓ All outcomes are covered.[/green]")


# ---------------------------------------------------------------------------
# resources command
# ---------------------------------------------------------------------------

@cli.command()
@click.option("--course", "-c", required=True, help="Course/topic name for resource suggestions")
@click.pass_context
def resources(ctx, course):
    """Suggest learning resources for a course topic."""
    if not check_ollama_running():
        console.print("[red]Error: Ollama is not running. Start with: ollama serve[/red]")
        raise SystemExit(1)

    suggester = ResourceSuggester()
    console.print(f"[cyan]Finding resources for '{course}'...[/cyan]")
    with console.status("[bold green]Searching for resources..."):
        res_list = suggester.suggest_resources([course])

    if not res_list:
        console.print("[yellow]No resources found.[/yellow]")
        return

    categorized = ResourceSuggester.categorize_resources(res_list)
    for cat, items in categorized.items():
        console.print(f"\n[bold green]{cat.upper()}:[/bold green]")
        for r in items:
            url_str = f" ({r.url})" if r.url else ""
            console.print(f"  • {r.title}: {r.description}{url_str}")


# ---------------------------------------------------------------------------
# export command
# ---------------------------------------------------------------------------

@cli.command(name="export")
@click.option("--input", "-i", "input_file", required=True, type=click.Path(exists=True),
              help="Input curriculum JSON file")
@click.option("--format", "-f", "fmt", type=click.Choice(["json", "markdown"]),
              default="json", help="Output format")
@click.option("--output", "-o", type=click.Path(), default=None, help="Output file path")
def export_cmd(input_file, fmt, output):
    """Export a curriculum to JSON or Markdown."""
    data = _load_curriculum_file(input_file)
    if output is None:
        ext = ".md" if fmt == "markdown" else ".json"
        output = input_file.rsplit(".", 1)[0] + f"_exported{ext}"
    export_curriculum(data, output, fmt=fmt)
    console.print(f"[green]✓ Exported to {output}[/green]")


# ---------------------------------------------------------------------------
# prerequisites command
# ---------------------------------------------------------------------------

@cli.command()
@click.option("--curriculum-file", "-f", required=True, type=click.Path(exists=True),
              help="Path to curriculum JSON file")
def prerequisites(curriculum_file):
    """Show prerequisite tree for a curriculum."""
    data = _load_curriculum_file(curriculum_file)
    tracker = PrerequisiteTracker()
    for p in data.get("prerequisites", []):
        if isinstance(p, str):
            tracker.add_prerequisite(Prerequisite(name=p))
        elif isinstance(p, dict):
            tracker.add_prerequisite(Prerequisite(
                name=p.get("name", ""),
                description=p.get("description", ""),
                required=p.get("required", True),
                alternatives=p.get("alternatives", []),
            ))

    tree_data = tracker.generate_prerequisite_tree()
    tree = Tree("📋 Prerequisites")
    req_branch = tree.add("[bold]Required")
    for item in tree_data["required"]:
        node = req_branch.add(item["name"])
        if item["description"]:
            node.add(f"[dim]{item['description']}[/dim]")
        if item["alternatives"]:
            alt_node = node.add("[yellow]Alternatives[/yellow]")
            for alt in item["alternatives"]:
                alt_node.add(alt)

    if tree_data["optional"]:
        opt_branch = tree.add("[dim]Optional")
        for item in tree_data["optional"]:
            node = opt_branch.add(item["name"])
            if item["description"]:
                node.add(f"[dim]{item['description']}[/dim]")

    console.print(tree)


# ---------------------------------------------------------------------------
# Display helper (from original app.py)
# ---------------------------------------------------------------------------

def _display_curriculum(data: dict) -> None:
    """Rich-formatted curriculum display."""
    console.print(Panel(
        f"[bold]{data.get('course_title', 'Course')}[/bold]\n"
        f"Level: {data.get('level', 'N/A')} | Duration: {data.get('duration_weeks', '?')} weeks\n\n"
        f"{data.get('description', '')}",
        title="📚 Course Overview", border_style="blue"
    ))

    if data.get("learning_objectives"):
        console.print("\n[bold cyan]🎯 Learning Objectives:[/bold cyan]")
        for i, obj in enumerate(data["learning_objectives"], 1):
            console.print(f"  {i}. {obj}")

    if data.get("prerequisites"):
        console.print("\n[bold yellow]📋 Prerequisites:[/bold yellow]")
        for p in data["prerequisites"]:
            label = p if isinstance(p, str) else p.get("name", str(p))
            console.print(f"  • {label}")

    console.print("\n")
    table = Table(title="Weekly Plan", show_lines=True, expand=True)
    table.add_column("Week", style="bold cyan", width=6)
    table.add_column("Title", style="bold", width=25)
    table.add_column("Topics", ratio=2)
    table.add_column("Activities", ratio=2)
    table.add_column("Assessment", ratio=1)

    for week in data.get("weekly_plan", []):
        topics = "\n".join(f"• {t}" for t in week.get("topics", []))
        activities = "\n".join(f"• {a}" for a in week.get("activities", []))
        table.add_row(
            str(week.get("week", "")),
            week.get("title", ""),
            topics,
            activities,
            week.get("assessment", ""),
        )

    console.print(table)

    if data.get("resources"):
        console.print("\n[bold green]📖 Recommended Resources:[/bold green]")
        res_table = Table(show_lines=True)
        res_table.add_column("Type", style="cyan", width=10)
        res_table.add_column("Title", style="bold", width=30)
        res_table.add_column("Description", ratio=2)
        for r in data["resources"]:
            res_table.add_row(r.get("type", ""), r.get("title", ""), r.get("description", ""))
        console.print(res_table)

    if data.get("assessment_strategy"):
        console.print(Panel(data["assessment_strategy"],
                            title="📊 Assessment Strategy", border_style="yellow"))


if __name__ == "__main__":
    cli()
