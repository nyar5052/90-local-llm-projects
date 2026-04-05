"""
CLI interface for Code Translator.
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
    detect_source_language,
    get_language_name,
    read_source_file,
    translate_code,
    compare_codes,
    batch_translate_files,
    generate_translation_notes,
    SUPPORTED_LANGUAGES,
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
    """🔄 Code Translator - Translate code between programming languages."""
    setup_logging(verbose)
    ctx.ensure_object(dict)
    ctx.obj["config"] = load_config(config_path)
    if ctx.invoked_subcommand is None:
        console.print(
            Panel(
                "[bold cyan]🔄 Code Translator[/bold cyan]\n"
                "Translate code between programming languages\n\n"
                "Use [bold]--help[/bold] to see available commands.",
                border_style="cyan",
            )
        )


@cli.command()
@click.option("--file", "-f", required=True, type=click.Path(exists=True), help="Source code file.")
@click.option("--target", "-t", required=True,
              type=click.Choice(list(SUPPORTED_LANGUAGES.keys()), case_sensitive=False),
              help="Target programming language.")
@click.option("--source-lang", "-s", help="Source language (auto-detected if not specified).")
@click.option("--output", "-o", help="Output file path for the translated code.")
@click.pass_context
def translate(ctx, file, target, source_lang, output):
    """Translate a source file to another language."""
    config = ctx.obj["config"]

    if not check_ollama_running():
        console.print("[red]Error:[/red] Ollama is not running. Start it with: ollama serve")
        sys.exit(1)

    src_lang = source_lang or detect_source_language(file)
    if not src_lang:
        console.print("[yellow]Warning:[/yellow] Could not detect source language. Specify with --source-lang.")
        src_lang = "unknown"

    src_name = get_language_name(src_lang)
    tgt_name = get_language_name(target)

    console.print(f"[dim]Source:[/dim] {file} ({src_name})")
    console.print(f"[dim]Target:[/dim] {tgt_name}\n")

    code = read_source_file(file)
    syntax = Syntax(code, src_lang, line_numbers=True, theme="monokai")
    console.print(Panel(syntax, title=f"📄 Source ({src_name})", border_style="dim"))

    with console.status(f"[bold cyan]Translating {src_name} → {tgt_name}...[/bold cyan]", spinner="dots"):
        result = translate_code(code, src_lang, target, chat, config)

    console.print()
    console.print(Panel(Markdown(result), title=f"🔄 Translated to {tgt_name}", border_style="green"))

    # Comparison
    comparison = compare_codes(code, result)
    table = Table(title="📊 Translation Summary", border_style="cyan")
    table.add_column("Metric", style="cyan")
    table.add_column("Source", style="yellow", justify="right")
    table.add_column("Target", style="green", justify="right")
    table.add_row("Lines", str(comparison["source_lines"]), str(comparison["target_lines"]))
    table.add_row("Characters", str(comparison["source_chars"]), str(comparison["target_chars"]))
    table.add_row("Line Ratio", "", str(comparison["line_ratio"]))
    console.print(table)

    if output:
        with open(output, "w", encoding="utf-8") as f:
            f.write(result)
        console.print(f"\n[green]✅ Saved to:[/green] {output}")


@cli.command()
@click.option("--files", "-f", multiple=True, required=True, type=click.Path(exists=True), help="Files to translate.")
@click.option("--target", "-t", required=True,
              type=click.Choice(list(SUPPORTED_LANGUAGES.keys()), case_sensitive=False),
              help="Target language.")
@click.option("--output-dir", "-o", default="translations", help="Output directory.")
@click.pass_context
def batch(ctx, files, target, output_dir):
    """Translate multiple files in batch."""
    config = ctx.obj["config"]

    if not check_ollama_running():
        console.print("[red]Error:[/red] Ollama is not running.")
        sys.exit(1)

    console.print(f"[dim]Translating {len(files)} file(s) to {get_language_name(target)}[/dim]\n")

    with console.status("[bold cyan]Batch translating...[/bold cyan]", spinner="dots"):
        results = batch_translate_files(list(files), target, chat, output_dir, config)

    table = Table(title="📊 Batch Results", border_style="cyan")
    table.add_column("Source", style="white")
    table.add_column("Output", style="cyan")
    table.add_column("Status", style="green")
    for r in results:
        status = "[green]✅[/green]" if r["status"] == "success" else f"[red]❌ {r.get('error', '')}[/red]"
        table.add_row(r["source"], r.get("output", ""), status)
    console.print(table)


@cli.command()
@click.option("--source", "-s", required=True,
              type=click.Choice(list(SUPPORTED_LANGUAGES.keys()), case_sensitive=False))
@click.option("--target", "-t", required=True,
              type=click.Choice(list(SUPPORTED_LANGUAGES.keys()), case_sensitive=False))
@click.pass_context
def notes(ctx, source, target):
    """Show translation notes between two languages."""
    if not check_ollama_running():
        console.print("[red]Error:[/red] Ollama is not running.")
        sys.exit(1)

    with console.status("[bold cyan]Generating notes...[/bold cyan]", spinner="dots"):
        result = generate_translation_notes(source, target, chat)

    console.print(Panel(Markdown(result),
                        title=f"📝 {get_language_name(source)} → {get_language_name(target)} Notes",
                        border_style="yellow"))


def main():
    cli(obj={})


if __name__ == "__main__":
    main()
