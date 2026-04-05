"""
News Digest Generator

Aggregates news articles from text files, groups them by topic,
generates per-topic summaries, and produces an overall digest
using a local LLM via Ollama.
"""

import sys
import os
import glob

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from common.llm_client import chat, generate, check_ollama_running

import click
from rich.console import Console
from rich.panel import Panel
from rich.tree import Tree
from rich.markdown import Markdown
from rich.table import Table

console = Console()


def read_news_files(sources_dir: str) -> list[dict]:
    """Read all .txt files from the sources directory.

    Args:
        sources_dir: Path to folder containing .txt news files.

    Returns:
        List of dicts with 'filename' and 'content' keys.

    Raises:
        FileNotFoundError: If the sources directory does not exist.
        ValueError: If no .txt files are found in the directory.
    """
    if not os.path.isdir(sources_dir):
        raise FileNotFoundError(f"Sources directory not found: {sources_dir}")

    pattern = os.path.join(sources_dir, "*.txt")
    files = sorted(glob.glob(pattern))

    if not files:
        raise ValueError(f"No .txt files found in: {sources_dir}")

    articles = []
    for filepath in files:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            content = f.read().strip()
        if content:
            articles.append({
                "filename": os.path.basename(filepath),
                "content": content,
            })

    if not articles:
        raise ValueError(f"All .txt files in '{sources_dir}' are empty.")

    return articles


def categorize_articles(articles: list[dict], num_topics: int) -> str:
    """Send articles to the LLM for topic categorization.

    Args:
        articles: List of article dicts with 'filename' and 'content'.
        num_topics: Desired number of topic groups.

    Returns:
        Raw LLM response with categorized articles.
    """
    articles_text = "\n\n---\n\n".join(
        f"[File: {a['filename']}]\n{a['content']}" for a in articles
    )

    prompt = (
        f"You are a news editor. Below are {len(articles)} news articles. "
        f"Group them into exactly {num_topics} topic categories.\n\n"
        f"For each topic category:\n"
        f"1. Give the topic a clear, concise name\n"
        f"2. List which articles (by filename) belong to it\n"
        f"3. Write a 2-3 sentence summary of that topic group\n\n"
        f"Format your response as:\n\n"
        f"## Topic: <topic name>\n"
        f"**Articles:** <comma-separated filenames>\n"
        f"**Summary:** <summary text>\n\n"
        f"Repeat for each topic.\n\n"
        f"ARTICLES:\n\n{articles_text}"
    )

    return generate(
        prompt=prompt,
        system_prompt="You are a professional news editor who categorizes and summarizes news articles.",
        temperature=0.4,
        max_tokens=4096,
    )


def generate_digest(articles: list[dict], categorization: str) -> str:
    """Generate an overall news digest from the categorized articles.

    Args:
        articles: List of article dicts.
        categorization: LLM-generated categorization text.

    Returns:
        Raw LLM response with the full news digest.
    """
    prompt = (
        f"Based on the following topic categorization of {len(articles)} news articles, "
        f"generate a professional news digest.\n\n"
        f"The digest should include:\n"
        f"1. **Key Headlines** — the 3-5 most important headlines\n"
        f"2. **Trending Themes** — overarching themes across all articles\n"
        f"3. **Topic Summaries** — a polished paragraph for each topic group\n"
        f"4. **Outlook** — a brief forward-looking paragraph\n\n"
        f"CATEGORIZATION:\n\n{categorization}"
    )

    return generate(
        prompt=prompt,
        system_prompt="You are a professional news digest writer producing concise, informative summaries.",
        temperature=0.5,
        max_tokens=4096,
    )


def display_results(
    articles: list[dict],
    categorization: str,
    digest: str,
    num_topics: int,
) -> None:
    """Render results to the console using Rich formatting.

    Args:
        articles: List of article dicts.
        categorization: LLM categorization output.
        digest: LLM digest output.
        num_topics: Number of requested topic groups.
    """
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
        border_style="yellow",
        padding=(1, 2),
    ))
    console.print()

    # Full digest
    console.print(Panel(
        Markdown(digest),
        title="[bold green]📋 News Digest[/bold green]",
        border_style="green",
        padding=(1, 2),
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


def save_output(filepath: str, categorization: str, digest: str) -> None:
    """Save the digest output to a file.

    Args:
        filepath: Destination file path.
        categorization: LLM categorization text.
        digest: LLM digest text.
    """
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("# News Digest\n\n")
        f.write("## Topic Categorization\n\n")
        f.write(categorization)
        f.write("\n\n---\n\n")
        f.write("## Full Digest\n\n")
        f.write(digest)
        f.write("\n")


@click.command()
@click.option(
    "--sources",
    required=True,
    type=click.Path(exists=False),
    help="Path to folder containing .txt news files.",
)
@click.option(
    "--topics",
    default=5,
    type=int,
    show_default=True,
    help="Number of topic groups to categorize articles into.",
)
@click.option(
    "--output",
    default=None,
    type=click.Path(),
    help="Optional file path to save the generated digest.",
)
def main(sources: str, topics: int, output: str | None) -> None:
    """📰 News Digest Generator — aggregate, categorize, and summarize news articles."""
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
        categorization = categorize_articles(articles, topics)
    console.print("[green]✓[/green] Categorization complete")

    # Generate digest
    with console.status("[bold green]Generating news digest…[/bold green]"):
        digest = generate_digest(articles, categorization)
    console.print("[green]✓[/green] Digest generated")

    # Display
    display_results(articles, categorization, digest, topics)

    # Save
    if output:
        save_output(output, categorization, digest)
        console.print(f"[green]✓[/green] Digest saved to [cyan]{output}[/cyan]")


if __name__ == "__main__":
    main()
