"""Click CLI interface for the Report Generator."""

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.markdown import Markdown
from rich.table import Table

from .core import (
    read_csv_data,
    summarize_data,
    generate_report,
    save_report,
    REPORT_TEMPLATES,
)
from .config import load_config
from .utils import setup_logging, setup_sys_path, truncate_text

setup_sys_path()
from common.llm_client import check_ollama_running

console = Console()


@click.command()
@click.option("--topic", required=True, type=str, help="Report topic or title.")
@click.option(
    "--data", required=True, type=click.Path(exists=True), help="Path to CSV data file."
)
@click.option(
    "--output",
    default="report.md",
    type=click.Path(),
    help="Output file path (default: report.md).",
)
@click.option(
    "--template",
    type=click.Choice(["executive", "technical", "summary"], case_sensitive=False),
    default="executive",
    show_default=True,
    help="Report template style.",
)
@click.option(
    "--format",
    "fmt",
    type=click.Choice(["markdown", "html", "text"], case_sensitive=False),
    default="markdown",
    show_default=True,
    help="Output format.",
)
@click.option("--config", "config_path", type=click.Path(), default=None, help="Path to config.yaml.")
@click.option("--verbose", is_flag=True, help="Enable verbose logging.")
def main(topic: str, data: str, output: str, template: str, fmt: str, config_path: str, verbose: bool):
    """📊 Generate a structured report from CSV data using a local LLM."""
    setup_logging(verbose)
    config = load_config(config_path)

    console.print(
        Panel(
            f"[bold cyan]📊 Report Generator[/bold cyan]\n"
            f"Topic: [yellow]{topic}[/yellow] | Template: [green]{template}[/green]",
            border_style="cyan",
        )
    )

    # Check Ollama
    with Progress(
        SpinnerColumn(), TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Checking Ollama connection...", total=None)
        if not check_ollama_running():
            console.print("[bold red]✗ Ollama is not running.[/bold red]")
            console.print("  Start it with: [cyan]ollama serve[/cyan]")
            raise SystemExit(1)
        progress.update(task, description="[green]✓ Ollama connected[/green]")

    # Read CSV
    console.print(f"\n[bold]Reading data from:[/bold] {data}")
    try:
        headers, rows = read_csv_data(data)
    except (FileNotFoundError, ValueError) as e:
        console.print(f"[bold red]✗ Data error:[/bold red] {e}")
        raise SystemExit(1)

    # Show data preview
    max_preview = config.get("data", {}).get("max_rows_preview", 5)
    preview_table = Table(title=f"Data Preview (first {min(max_preview, len(rows))} of {len(rows)} rows)")
    for h in headers:
        preview_table.add_column(h, style="cyan")
    for row in rows[:max_preview]:
        preview_table.add_row(*[row.get(h, "") for h in headers])
    console.print(preview_table)

    # Summarize
    data_summary = summarize_data(headers, rows)
    console.print(f"\n[dim]{data_summary}[/dim]\n")

    # Generate report
    with Progress(
        SpinnerColumn(), TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task(f"Generating {template} report with LLM...", total=None)
        report_content = generate_report(topic, data_summary, template=template, config=config)
        progress.update(task, description="[green]✓ Report generated[/green]")

    # Save
    saved_path = save_report(report_content, output, topic, fmt=fmt)
    console.print(f"\n[bold green]✓ Report saved to:[/bold green] {saved_path}")

    # Preview
    preview = truncate_text(report_content)
    console.print(Panel(Markdown(preview), title="Report Preview", border_style="green"))


if __name__ == "__main__":
    main()
