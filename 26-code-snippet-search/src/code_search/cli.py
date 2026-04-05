"""
CLI interface for Code Snippet Search.
Provides a rich terminal experience with syntax highlighting.
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
from rich.progress import Progress, SpinnerColumn, TextColumn

from .core import (
    load_config,
    scan_directory,
    build_search_context,
    search_code,
    rank_files,
    load_bookmarks,
    save_bookmark,
    remove_bookmark,
    DEFAULT_EXTENSIONS,
)

console = Console()
logger = logging.getLogger(__name__)


def setup_logging(verbose: bool = False) -> None:
    """Configure logging based on verbosity."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


@click.group(invoke_without_command=True)
@click.pass_context
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging.")
@click.option("--config", "config_path", default="config.yaml", help="Config file path.")
def cli(ctx, verbose, config_path):
    """🔎 Code Snippet Search - Search code with natural language."""
    setup_logging(verbose)
    ctx.ensure_object(dict)
    ctx.obj["config"] = load_config(config_path)
    if ctx.invoked_subcommand is None:
        console.print(
            Panel(
                "[bold cyan]🔎 Code Snippet Search[/bold cyan]\n"
                "Search your codebase with natural language queries\n\n"
                "Use [bold]--help[/bold] to see available commands.",
                border_style="cyan",
            )
        )


@cli.command()
@click.option("--dir", "-d", "directory", required=True, help="Directory to search.")
@click.option("--query", "-q", required=True, help="Natural language search query.")
@click.option("--max-files", default=100, help="Max files to index (default: 100).")
@click.option("--ext", multiple=True, help="File extensions to include (e.g., .py .js).")
@click.option("--bookmark", "-b", is_flag=True, help="Bookmark this search result.")
@click.pass_context
def search(ctx, directory: str, query: str, max_files: int, ext: tuple, bookmark: bool):
    """Search codebase with a natural language query."""
    config = ctx.obj["config"]

    if not check_ollama_running():
        console.print("[red]Error:[/red] Ollama is not running. Start it with: ollama serve")
        sys.exit(1)

    if not os.path.isdir(directory):
        console.print(f"[red]Error:[/red] Directory '{directory}' not found.")
        sys.exit(1)

    extensions = set(ext) if ext else set(config.get("extensions", DEFAULT_EXTENSIONS))
    console.print(f"[dim]Directory:[/dim] {directory}")
    console.print(f'[dim]Query:[/dim] "{query}"')

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
        task = progress.add_task("Indexing files...", total=None)
        files = scan_directory(directory, extensions, max_files)
        progress.update(task, completed=True)

    console.print(f"[dim]Indexed {len(files)} file(s)[/dim]\n")

    if not files:
        console.print("[yellow]No matching files found.[/yellow]")
        sys.exit(0)

    table = Table(title="📁 Indexed Files", border_style="dim", show_lines=False)
    table.add_column("File", style="cyan")
    table.add_column("Language", style="yellow")
    table.add_column("Lines", style="white", justify="right")
    for f in files[:20]:
        table.add_row(f["path"], f["language"], str(f["lines"]))
    if len(files) > 20:
        table.add_row(f"... and {len(files) - 20} more", "", "")
    console.print(table)
    console.print()

    result = search_code(directory, query, chat, config)
    console.print(Panel(Markdown(result), title="🎯 Search Results", border_style="green"))

    if bookmark:
        save_bookmark({"query": query, "directory": directory, "result_preview": result[:200]},
                       config.get("bookmarks_file", "bookmarks.json"))
        console.print("[green]✅ Result bookmarked![/green]")


@cli.command()
@click.pass_context
def bookmarks(ctx):
    """View saved bookmarks."""
    config = ctx.obj["config"]
    bmarks = load_bookmarks(config.get("bookmarks_file", "bookmarks.json"))
    if not bmarks:
        console.print("[dim]No bookmarks saved yet.[/dim]")
        return

    table = Table(title="⭐ Bookmarks", border_style="yellow")
    table.add_column("#", style="dim", justify="right")
    table.add_column("Query", style="cyan")
    table.add_column("Directory", style="white")
    table.add_column("Preview", style="dim", max_width=40)
    for i, bm in enumerate(bmarks):
        table.add_row(str(i), bm.get("query", ""), bm.get("directory", ""), bm.get("result_preview", "")[:40])
    console.print(table)


@cli.command(name="remove-bookmark")
@click.argument("index", type=int)
@click.pass_context
def remove_bookmark_cmd(ctx, index: int):
    """Remove a bookmark by index."""
    config = ctx.obj["config"]
    if remove_bookmark(index, config.get("bookmarks_file", "bookmarks.json")):
        console.print(f"[green]✅ Removed bookmark #{index}[/green]")
    else:
        console.print(f"[red]Invalid bookmark index: {index}[/red]")


def main():
    """Entry point for CLI."""
    cli(obj={})


if __name__ == "__main__":
    main()
