#!/usr/bin/env python3
"""
Science Experiment Explainer — CLI interface.

Provides click-based commands for experiment explanation, search, safety
lookups, equipment management, and export.
"""

import sys
import json

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .core import (
    check_ollama_running,
    explain_experiment,
    search_experiments,
    suggest_alternatives as suggest_alternatives_fn,
    export_experiment,
    validate_experiment_data,
    SafetyDatabase,
    EquipmentManager,
    ConfigManager,
    setup_logging,
)

console = Console()


def _check_ollama() -> None:
    if not check_ollama_running():
        console.print("[red]Error: Ollama is not running. Start with: ollama serve[/red]")
        sys.exit(1)


# ---------------------------------------------------------------------------
# Rich display helpers
# ---------------------------------------------------------------------------


def display_experiment(data: dict) -> None:
    """Render experiment data with Rich."""
    console.print(Panel(
        f"[bold]{data.get('experiment_name', 'Experiment')}[/bold]\n"
        f"Subject: {data.get('subject', 'N/A')} | "
        f"Level: {data.get('grade_level', 'N/A')} | "
        f"Duration: {data.get('duration', 'N/A')}",
        title="🔬 Science Experiment",
        border_style="blue",
    ))

    if data.get("objective"):
        console.print(f"\n[bold cyan]🎯 Objective:[/bold cyan] {data['objective']}")

    if data.get("scientific_concepts"):
        console.print("\n[bold cyan]📖 Scientific Concepts:[/bold cyan]")
        for c in data["scientific_concepts"]:
            console.print(f"  • {c}")

    if data.get("safety_precautions"):
        console.print(Panel(
            "\n".join(f"⚠️  {p}" for p in data["safety_precautions"]),
            title="🛡️ Safety Precautions",
            border_style="red",
        ))

    if data.get("materials"):
        mat_table = Table(title="📦 Materials", show_lines=True)
        mat_table.add_column("Item", style="cyan", width=25)
        mat_table.add_column("Quantity", width=15)
        mat_table.add_column("Notes", style="dim")
        for m in data["materials"]:
            mat_table.add_row(m.get("item", ""), m.get("quantity", ""), m.get("notes", ""))
        console.print(mat_table)

    if data.get("procedure"):
        console.print("\n[bold green]📋 Procedure:[/bold green]")
        for step in data["procedure"]:
            console.print(f"\n  [bold]Step {step.get('step', '?')}:[/bold] {step.get('instruction', '')}")
            if step.get("tip"):
                console.print(f"  [yellow]💡 Tip: {step['tip']}[/yellow]")

    if data.get("expected_results"):
        console.print(Panel(data["expected_results"], title="📊 Expected Results", border_style="green"))

    if data.get("explanation"):
        console.print(Panel(data["explanation"], title="🧪 Why It Works", border_style="cyan"))

    if data.get("variations"):
        console.print("\n[bold magenta]🔄 Variations to Try:[/bold magenta]")
        for v in data["variations"]:
            console.print(f"  • {v}")

    if data.get("discussion_questions"):
        console.print("\n[bold yellow]❓ Discussion Questions:[/bold yellow]")
        for i, q in enumerate(data["discussion_questions"], 1):
            console.print(f"  {i}. {q}")


# ---------------------------------------------------------------------------
# CLI group
# ---------------------------------------------------------------------------


@click.group()
@click.version_option(package_name="science-experiment-explainer")
def cli():
    """🔬 Science Experiment Explainer — Powered by Local LLM."""
    config = ConfigManager()
    setup_logging(config)


# -- explain ----------------------------------------------------------------


@cli.command()
@click.option("--experiment", "-e", required=True, help="Experiment name")
@click.option("--level", "-l", default="middle school", help="Grade level")
@click.option("--detail", "-d", type=click.Choice(["brief", "medium", "detailed"]),
              default="medium", help="Detail level")
@click.option("--output", "-o", type=click.Path(), help="Save to file (JSON)")
def explain(experiment, level, detail, output):
    """Explain a science experiment step-by-step."""
    console.print(Panel("[bold blue]🔬 Science Experiment Explainer[/bold blue]",
                        subtitle="Powered by Local LLM"))
    _check_ollama()

    console.print(f"[cyan]Explaining '{experiment}' for {level} level...[/cyan]")
    with console.status("[bold green]Researching experiment..."):
        data = explain_experiment(experiment, level, detail)

    errors = validate_experiment_data(data)
    if errors:
        console.print("[yellow]Warning: response has issues:[/yellow]")
        for e in errors:
            console.print(f"  ⚠️ {e}")

    display_experiment(data)

    if output:
        with open(output, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        console.print(f"\n[green]✓ Explanation saved to {output}[/green]")


# -- search -----------------------------------------------------------------


@cli.command()
@click.option("--topic", "-t", default="", help="Topic keyword")
@click.option("--subject", "-s", default="", help="Subject area")
@click.option("--difficulty", "-d", default="", help="Difficulty level")
def search(topic, subject, difficulty):
    """Search for experiments by topic, subject, or difficulty."""
    _check_ollama()
    console.print("[cyan]Searching experiments...[/cyan]")
    with console.status("[bold green]Searching..."):
        results = search_experiments(topic, subject, difficulty)

    table = Table(title="🔍 Search Results", show_lines=True)
    table.add_column("#", width=3)
    table.add_column("Name", style="cyan")
    table.add_column("Subject")
    table.add_column("Level")
    table.add_column("Description", width=40)
    for i, r in enumerate(results, 1):
        table.add_row(
            str(i),
            r.get("name", ""),
            r.get("subject", ""),
            r.get("grade_level", ""),
            r.get("description", ""),
        )
    console.print(table)


# -- safety -----------------------------------------------------------------


@cli.command()
@click.option("--experiment", "-e", required=True, help="Experiment name or material")
def safety(experiment):
    """Show safety information for an experiment or material."""
    db = SafetyDatabase()
    info = db.get_safety_info(experiment)
    if info:
        color_map = {"low": "green", "medium": "yellow", "high": "red", "critical": "bold red"}
        color = color_map.get(info.level, "white")
        console.print(Panel(
            f"[{color}]Level: {info.level.upper()}[/{color}]\n\n"
            f"{info.description}\n\n"
            f"Precaution: {info.precaution}\n"
            f"PPE: {', '.join(info.equipment_needed) or 'None specific'}",
            title=f"🛡️ Safety — {experiment}",
            border_style=color_map.get(info.level, "white"),
        ))
    else:
        console.print(f"[yellow]No built-in safety data for '{experiment}'. "
                       f"Always follow general lab safety practices.[/yellow]")


# -- equipment --------------------------------------------------------------


@cli.command()
@click.option("--experiment", "-e", required=True, help="Experiment name or equipment item")
def equipment(experiment):
    """Show equipment details and alternatives."""
    mgr = EquipmentManager()
    alts = mgr.suggest_alternatives(experiment)
    if alts:
        console.print(f"[cyan]Alternatives for [bold]{experiment}[/bold]:[/cyan]")
        for a in alts:
            console.print(f"  • {a}")
    else:
        console.print(f"[yellow]No equipment data for '{experiment}'.[/yellow]")


# -- alternatives -----------------------------------------------------------


@cli.command()
@click.option("--experiment", "-e", required=True, help="Experiment name")
@click.option("--level", "-l", default="middle school", help="Grade level")
def alternatives(experiment, level):
    """Suggest alternative experiments."""
    _check_ollama()
    console.print(f"[cyan]Finding alternatives for '{experiment}'...[/cyan]")
    with console.status("[bold green]Thinking..."):
        results = suggest_alternatives_fn(experiment, level)

    for i, r in enumerate(results, 1):
        console.print(Panel(
            f"[bold]{r.get('name', '')}[/bold]\n{r.get('description', '')}\n"
            f"Difficulty: {r.get('difficulty', '?')}\n"
            f"Why: {r.get('why_alternative', '')}",
            title=f"Option {i}",
            border_style="magenta",
        ))


# -- export -----------------------------------------------------------------


@cli.command(name="export")
@click.option("--input", "-i", "input_file", required=True,
              type=click.Path(exists=True), help="Input JSON experiment file")
@click.option("--format", "-f", "fmt", type=click.Choice(["json", "markdown", "checklist"]),
              default="markdown", help="Output format")
@click.option("--output", "-o", type=click.Path(), help="Output file path")
def export_cmd(input_file, fmt, output):
    """Export an experiment to different formats."""
    with open(input_file, "r", encoding="utf-8") as fh:
        data = json.load(fh)

    result = export_experiment(data, fmt)

    if output:
        with open(output, "w", encoding="utf-8") as fh:
            fh.write(result)
        console.print(f"[green]✓ Exported to {output}[/green]")
    else:
        console.print(result)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    cli()
