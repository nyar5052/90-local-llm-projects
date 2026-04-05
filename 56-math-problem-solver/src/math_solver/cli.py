"""CLI interface for Math Problem Solver."""

import json
import logging
import sys

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .core import (
    solve_problem,
    generate_practice_problems,
    get_formula_library,
    get_formulas_from_llm,
    check_service,
)

console = Console()
logger = logging.getLogger(__name__)


def _setup_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


# ---------------------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------------------


def display_solution(result, show_steps: bool = True) -> None:
    """Display the math solution in rich format."""
    console.print(Panel(
        f"[bold]{result.problem}[/bold]\n"
        f"Category: {result.category} | Difficulty: {result.difficulty}",
        title="📐 Problem",
        border_style="blue",
    ))

    if show_steps and result.solution and result.solution.steps:
        console.print("\n[bold cyan]📝 Solution Steps:[/bold cyan]\n")
        for step in result.solution.steps:
            console.print(f"[bold yellow]Step {step.step_number}:[/bold yellow] {step.description}")
            if step.work:
                console.print(Panel(step.work, border_style="dim", padding=(0, 2)))
            if step.explanation:
                console.print(f"  [dim]{step.explanation}[/dim]")
            console.print()

    if result.solution:
        console.print(Panel(
            f"[bold green]{result.solution.answer}[/bold green]",
            title="✅ Answer",
            border_style="green",
        ))

    if result.latex_output:
        console.print(Panel(result.latex_output, title="📄 LaTeX", border_style="magenta"))

    if result.concepts_used:
        console.print("\n[bold cyan]📖 Concepts Used:[/bold cyan]")
        for c in result.concepts_used:
            console.print(f"  • {c}")

    if result.tips:
        console.print("\n[bold yellow]💡 Tips:[/bold yellow]")
        for t in result.tips:
            console.print(f"  • {t}")

    if result.related_problems:
        console.print("\n[bold magenta]🔗 Practice Problems:[/bold magenta]")
        for p in result.related_problems:
            console.print(f"  • {p}")


def display_formulas(data: dict) -> None:
    """Display formula library."""
    if "categories" in data:
        for cat, formulas in data["categories"].items():
            _print_formula_table(cat, formulas)
    else:
        _print_formula_table(data.get("category", ""), data.get("formulas", []))


def _print_formula_table(category: str, formulas: list) -> None:
    table = Table(title=f"📐 {category.title()} Formulas", show_lines=True)
    table.add_column("Name", style="bold cyan", width=22)
    table.add_column("Formula", style="white")
    table.add_column("Description", style="dim")
    for f in formulas:
        table.add_row(f.get("name", ""), f.get("formula", ""), f.get("description", ""))
    console.print(table)
    console.print()


def display_practice(data: dict) -> None:
    """Display practice problems."""
    console.print(Panel(
        f"[bold]{data.get('category', 'Practice')}[/bold] — {data.get('difficulty', '')}",
        title="🏋️ Practice Problems",
        border_style="green",
    ))
    for p in data.get("problems", []):
        console.print(f"\n[bold yellow]Problem {p.get('number', '?')}:[/bold yellow] {p.get('problem', '')}")
        console.print(f"  [dim]Hint: {p.get('hint', '')}[/dim]")
        console.print(f"  [green]Answer: {p.get('answer', '')}[/green]")


# ---------------------------------------------------------------------------
# CLI commands
# ---------------------------------------------------------------------------


@click.group()
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
def cli(verbose):
    """📐 Math Problem Solver — Solve math problems with step-by-step explanations."""
    _setup_logging(verbose)


@cli.command()
@click.option("--problem", "-p", required=True, help="Math problem to solve")
@click.option("--show-steps/--no-steps", default=True, help="Show step-by-step solution")
@click.option("--category", "-c",
              type=click.Choice(["algebra", "calculus", "geometry", "statistics",
                                 "arithmetic", "trigonometry", ""], case_sensitive=False),
              default="", help="Problem category")
@click.option("--output", "-o", type=click.Path(), help="Save solution to JSON file")
def solve(problem, show_steps, category, output):
    """Solve a math problem with detailed explanations."""
    console.print(Panel("[bold blue]📐 Math Problem Solver[/bold blue]", subtitle="Powered by Local LLM"))

    if not check_service():
        console.print("[red]Error: Ollama is not running. Start with: ollama serve[/red]")
        sys.exit(1)

    console.print(f"[cyan]Solving: {problem}[/cyan]")

    with console.status("[bold green]Working on solution..."):
        result = solve_problem(problem, show_steps, category)

    display_solution(result, show_steps)

    if output:
        with open(output, "w", encoding="utf-8") as f:
            json.dump(result.to_dict(), f, indent=2, ensure_ascii=False)
        console.print(f"\n[green]✓ Solution saved to {output}[/green]")


@cli.command()
@click.option("--category", "-c", default="", help="Formula category (e.g. algebra, geometry)")
@click.option("--extended", is_flag=True, help="Fetch extended formulas from LLM")
def formulas(category, extended):
    """Browse the formula reference library."""
    console.print(Panel("[bold blue]📐 Formula Library[/bold blue]"))
    if extended:
        if not check_service():
            console.print("[red]Error: Ollama is not running.[/red]")
            sys.exit(1)
        with console.status("[bold green]Fetching formulas..."):
            data = get_formulas_from_llm(category or "all mathematics")
    else:
        data = get_formula_library(category)
    display_formulas(data)


@cli.command()
@click.option("--category", "-c", required=True, help="Problem category")
@click.option("--difficulty", "-d", type=click.Choice(["basic", "intermediate", "advanced"]),
              default="intermediate", help="Difficulty level")
@click.option("--count", "-n", default=5, type=int, help="Number of problems")
def practice(category, difficulty, count):
    """Generate practice problems with hints and answers."""
    console.print(Panel("[bold blue]🏋️ Practice Mode[/bold blue]"))

    if not check_service():
        console.print("[red]Error: Ollama is not running.[/red]")
        sys.exit(1)

    with console.status("[bold green]Generating practice problems..."):
        data = generate_practice_problems(category, difficulty, count)

    display_practice(data)


def main():
    """Entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
