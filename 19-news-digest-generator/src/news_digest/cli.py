"""Click CLI interface for the News Digest Generator."""

import sys
import click
from rich.console import Console
from rich.panel import Panel
from rich.tree import Tree
from rich.markdown import Markdown
from rich.table import Table

from .core import (
    read_news_files,
    categorize_articles,
    generate_digest,
    analyze_sentiment,
    save_output,
)
from .config import load_config
from .utils import setup_logging, setup_sys_path

setup_sys_path()
from common.llm_client import check_ollama_running

console = Console()


def display_results(articles: list[dict], categorization: str, digest: str, num_topics: int) -> None:
    """Render results to the console using Rich formatting."""
    console.print()
    console.rule("[bold cyan]📰 News Digest Generator[/bold cyan]")
    console.print()

    # Source summary
    source_table = Table(title="Source Articles", show_header=True)
    source_table.add_column("File", style="green")
    source_table.add_column("Length", justify="right", style="cyan")
    for a in articles:
        source_table.add_row(a["filename"], f"{len(a['content']):,} chars")
    console.print(source_table)
    console.print()

    # Topic categorization
    console.print(Panel(
        Markdown(categorization),
        title=f"[bold yellow]Topic Categorization ({num_topics} groups)[/bold yellow]",
        border_style="yellow", padding=(1, 2),
    ))
    console.print()

    # Full digest
    console.print(Panel(
        Markdown(digest),
        title="[bold green]📋 News Digest[/bold green]",
        border_style="green", padding=(1, 2),
    ))
    console.print()

    # Stats tree
    tree = Tree("[bold]📊 Generation Stats[/bold]")
    tree.add(f"Articles processed: {len(articles)}")
    tree.add(f"Topic groups requested: {num_topics}")
    total_chars = sum(len(a["content"]) for a in articles)
    tree.add(f"Total input size: {total_chars:,} characters")
    console.print(tree)
    console.print()


@click.command()
@click.option("--sources", required=True, type=click.Path(exists=False), help="Path to folder containing .txt news files.")
@click.option("--topics", default=5, type=int, show_default=True, help="Number of topic groups.")
@click.option("--output", default=None, type=click.Path(), help="Optional file path to save the digest.")
@click.option(
    "--format", "digest_format",
    type=click.Choice(["daily", "weekly"], case_sensitive=False),
    default="daily", show_default=True, help="Digest format.",
)
@click.option("--sentiment", is_flag=True, help="Include sentiment analysis.")
@click.option("--config", "config_path", type=click.Path(), default=None, help="Path to config.yaml.")
@click.option("--verbose", is_flag=True, help="Enable verbose logging.")
def main(sources: str, topics: int, output: str | None, digest_format: str,
         sentiment: bool, config_path: str, verbose: bool) -> None:
    """📰 News Digest Generator — aggregate, categorize, and summarize news articles."""
    setup_logging(verbose)
    config = load_config(config_path)

    console.print("[bold cyan]📰 News Digest Generator[/bold cyan]")
    console.print()

    # Validate Ollama
    with console.status("[bold green]Checking Ollama status…[/bold green]"):
        if not check_ollama_running():
            console.print("[bold red]Error:[/bold red] Ollama is not running. Start it with `ollama serve`.")
            raise SystemExit(1)
    console.print("[green]✓[/green] Ollama is running")

    # Read articles
    try:
        with console.status("[bold green]Reading news files…[/bold green]"):
            articles = read_news_files(sources)
        console.print(f"[green]✓[/green] Loaded {len(articles)} article(s) from [cyan]{sources}[/cyan]")
    except (FileNotFoundError, ValueError) as exc:
        console.print(f"[bold red]Error:[/bold red] {exc}")
        raise SystemExit(1)

    # Validate topic count
    if topics < 1:
        console.print("[bold red]Error:[/bold red] --topics must be at least 1.")
        raise SystemExit(1)
    if topics > len(articles):
        console.print(
            f"[yellow]Warning:[/yellow] Requested {topics} topics but only {len(articles)} article(s). "
            f"Adjusting to {len(articles)} topics."
        )
        topics = len(articles)

    # Categorize
    with console.status("[bold green]Categorizing articles by topic…[/bold green]"):
        categorization = categorize_articles(articles, topics, config=config)
    console.print("[green]✓[/green] Categorization complete")

    # Generate digest
    with console.status(f"[bold green]Generating {digest_format} digest…[/bold green]"):
        digest = generate_digest(articles, categorization, digest_format=digest_format, config=config)
    console.print("[green]✓[/green] Digest generated")

    # Display
    display_results(articles, categorization, digest, topics)

    # Sentiment analysis
    if sentiment:
        with console.status("[bold green]Analyzing sentiment…[/bold green]"):
            sentiment_result = analyze_sentiment(articles, config=config)
        console.print(Panel(Markdown(sentiment_result), title="📊 Sentiment Analysis", border_style="magenta"))

    # Save
    if output:
        save_output(output, categorization, digest)
        console.print(f"[green]✓[/green] Digest saved to [cyan]{output}[/cyan]")


if __name__ == "__main__":
    main()
