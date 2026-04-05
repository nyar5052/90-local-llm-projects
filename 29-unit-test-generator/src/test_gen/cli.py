"""
CLI interface for Unit Test Generator.
"""

import sys
import os
import logging

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
from common.llm_client import chat, check_ollama_running

import click
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich.table import Table

from .core import (
    load_config,
    extract_code_info,
    generate_tests,
    analyze_coverage,
    organize_test_structure,
    SUPPORTED_FRAMEWORKS,
)

console = Console()
logger = logging.getLogger(__name__)


def setup_logging(verbose: bool = False) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")


@click.group(invoke_without_command=True)
@click.pass_context
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging.")
@click.option("--config", "config_path", default="config.yaml", help="Config file path.")
def cli(ctx, verbose, config_path):
    """🧪 Unit Test Generator - Generate tests for Python functions."""
    setup_logging(verbose)
    ctx.ensure_object(dict)
    ctx.obj["config"] = load_config(config_path)
    if ctx.invoked_subcommand is None:
        console.print(
            Panel(
                "[bold cyan]🧪 Unit Test Generator[/bold cyan]\n"
                "Generate comprehensive unit tests for Python code\n\n"
                "Use [bold]--help[/bold] to see available commands.",
                border_style="cyan",
            )
        )


@cli.command()
@click.option("--file", "-f", required=True, type=click.Path(exists=True), help="Python file to generate tests for.")
@click.option("--framework", "-F", default="pytest",
              type=click.Choice(SUPPORTED_FRAMEWORKS, case_sensitive=False),
              help="Testing framework (default: pytest).")
@click.option("--output", "-o", help="Output file for generated tests.")
@click.option("--show-source", is_flag=True, help="Show source code before generating tests.")
@click.pass_context
def generate(ctx, file, framework, output, show_source):
    """Generate unit tests for a Python file."""
    config = ctx.obj["config"]

    if not check_ollama_running():
        console.print("[red]Error:[/red] Ollama is not running. Start it with: ollama serve")
        sys.exit(1)

    console.print(f"[dim]File:[/dim] {file}")
    console.print(f"[dim]Framework:[/dim] {framework}")

    info = extract_code_info(file)

    # Code structure table
    table = Table(title="📊 Code Structure", border_style="dim")
    table.add_column("Type", style="cyan")
    table.add_column("Name", style="white")
    table.add_column("Details", style="dim")
    table.add_column("Edge Cases", style="yellow")
    for func in info["functions"]:
        args = ", ".join(func["args"])
        edges = ", ".join(func.get("edge_cases", [])) or "—"
        table.add_row("Function", func["name"], f"({args})", edges)
    for cls in info["classes"]:
        table.add_row("Class", cls["name"], f"{len(cls['methods'])} methods", "")
        for m in cls["methods"]:
            edges = ", ".join(m.get("edge_cases", [])) or "—"
            table.add_row("  Method", f"  {m['name']}", f"({', '.join(m['args'])})", edges)
    console.print(table)

    # Coverage analysis
    coverage = analyze_coverage(info)
    console.print(f"\n[dim]Testable units: {coverage['total_testable']} | "
                  f"Estimated tests: {coverage['estimated_tests']} | "
                  f"Edge cases: {coverage['edge_case_count']}[/dim]")

    if show_source:
        syntax = Syntax(info["source"], "python", line_numbers=True, theme="monokai")
        console.print(Panel(syntax, title="📄 Source Code", border_style="dim"))

    console.print()
    with console.status("[bold cyan]Generating unit tests...[/bold cyan]", spinner="dots"):
        result = generate_tests(file, chat, framework, config)

    if output:
        with open(output, "w", encoding="utf-8") as f:
            f.write(result)
        console.print(f"[green]✅ Tests written to:[/green] {output}")
    else:
        console.print(Panel(Markdown(result), title="🧪 Generated Tests", border_style="green"))


@cli.command()
@click.option("--file", "-f", required=True, type=click.Path(exists=True), help="Python file to analyze.")
@click.pass_context
def analyze(ctx, file):
    """Analyze a Python file and show coverage requirements."""
    info = extract_code_info(file)
    coverage = analyze_coverage(info)

    table = Table(title="📊 Coverage Analysis", border_style="cyan")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="white", justify="right")
    table.add_row("Functions", str(coverage["total_functions"]))
    table.add_row("Methods", str(coverage["total_methods"]))
    table.add_row("Total Testable", str(coverage["total_testable"]))
    table.add_row("Estimated Tests", str(coverage["estimated_tests"]))
    table.add_row("Edge Cases", str(coverage["edge_case_count"]))
    console.print(table)

    if coverage["edge_cases_detected"]:
        console.print("\n[bold]🔍 Edge Cases Detected:[/bold]")
        for ec in coverage["edge_cases_detected"]:
            console.print(f"  • {ec}")

    structure = organize_test_structure(info)
    console.print("\n[bold]📁 Suggested Test Structure:[/bold]")
    for tf in structure["test_files"]:
        console.print(f"  📄 {tf['filename']}: {', '.join(tf['covers'])}")


def main():
    cli(obj={})


if __name__ == "__main__":
    main()
