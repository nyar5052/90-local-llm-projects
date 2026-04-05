"""
CLI interface for SQL Query Generator.
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
    read_schema,
    parse_schema_text,
    get_table_names,
    generate_sql,
    generate_sql_no_schema,
    optimize_query,
    load_history,
    save_to_history,
    clear_history,
    SUPPORTED_DIALECTS,
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
    """🗃️ SQL Query Generator - Convert natural language to SQL."""
    setup_logging(verbose)
    ctx.ensure_object(dict)
    ctx.obj["config"] = load_config(config_path)
    if ctx.invoked_subcommand is None:
        console.print(
            Panel(
                "[bold cyan]🗃️ SQL Query Generator[/bold cyan]\n"
                "Convert natural language questions to SQL queries\n\n"
                "Use [bold]--help[/bold] to see available commands.",
                border_style="cyan",
            )
        )


@cli.command()
@click.option("--schema", "-s", type=click.Path(exists=True), help="Path to SQL schema file.")
@click.option("--schema-text", help="Inline schema definition.")
@click.option("--query", "-q", required=True, help="Natural language query to convert.")
@click.option("--dialect", "-d", default="standard",
              type=click.Choice(SUPPORTED_DIALECTS, case_sensitive=False),
              help="SQL dialect (default: standard).")
@click.pass_context
def generate(ctx, schema, schema_text, query, dialect):
    """Generate SQL from a natural language query."""
    config = ctx.obj["config"]

    if not check_ollama_running():
        console.print("[red]Error:[/red] Ollama is not running. Start it with: ollama serve")
        sys.exit(1)

    console.print(f'[dim]Query:[/dim] "{query}"')
    console.print(f"[dim]Dialect:[/dim] {dialect}")

    if schema:
        schema_content = read_schema(schema)
        tables = get_table_names(schema_content)
        if tables:
            console.print(f"[dim]Tables found:[/dim] {', '.join(tables)}")
        console.print()

        syntax = Syntax(schema_content[:1000], "sql", line_numbers=True, theme="monokai")
        console.print(Panel(syntax, title="📊 Schema", border_style="dim"))

        with console.status("[bold cyan]Generating SQL query...[/bold cyan]", spinner="dots"):
            result = generate_sql(schema_content, query, chat, dialect, config)
    elif schema_text:
        with console.status("[bold cyan]Generating SQL query...[/bold cyan]", spinner="dots"):
            result = generate_sql(schema_text, query, chat, dialect, config)
    else:
        console.print("[dim]No schema provided — generating with assumed table structure[/dim]\n")
        with console.status("[bold cyan]Generating SQL query...[/bold cyan]", spinner="dots"):
            result = generate_sql_no_schema(query, chat, dialect, config)

    console.print()
    console.print(Panel(Markdown(result), title="📝 Generated SQL", border_style="green"))

    save_to_history(
        {"query": query, "dialect": dialect, "result_preview": result[:200]},
        config.get("history_file", "query_history.json"),
    )


@cli.command()
@click.pass_context
def history(ctx):
    """View query history."""
    config = ctx.obj["config"]
    hist = load_history(config.get("history_file", "query_history.json"))
    if not hist:
        console.print("[dim]No query history yet.[/dim]")
        return

    table = Table(title="📜 Query History", border_style="cyan")
    table.add_column("#", style="dim", justify="right")
    table.add_column("Query", style="cyan")
    table.add_column("Dialect", style="yellow")
    for i, entry in enumerate(hist[-20:]):
        table.add_row(str(i), entry.get("query", ""), entry.get("dialect", "standard"))
    console.print(table)


@cli.command(name="clear-history")
@click.pass_context
def clear_history_cmd(ctx):
    """Clear query history."""
    config = ctx.obj["config"]
    clear_history(config.get("history_file", "query_history.json"))
    console.print("[green]✅ History cleared[/green]")


def main():
    cli(obj={})


if __name__ == "__main__":
    main()
