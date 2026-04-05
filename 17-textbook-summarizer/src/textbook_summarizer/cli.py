"""Click CLI interface for the Textbook Summarizer."""

import sys
import click
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.text import Text

from .core import (
    read_chapter_file,
    detect_chapter_info,
    summarize_chapter,
    summarize_multi_chapter,
    generate_glossary,
    generate_concept_map,
    generate_study_questions,
    STYLE_PROMPTS,
)
from .config import load_config
from .utils import setup_logging, setup_sys_path, count_words

setup_sys_path()
from common.llm_client import check_ollama_running

console = Console()


def display_summary(summary: str, chapter_info: str, style: str) -> None:
    """Display the formatted summary in the terminal using Rich."""
    style_labels = {
        "concise": "Concise Summary",
        "detailed": "Detailed Summary",
        "study-guide": "Study Guide",
    }
    label = style_labels.get(style, style.title())

    header = Text()
    header.append("📚 ", style="bold")
    header.append(chapter_info, style="bold cyan")
    header.append(f"  ({label})", style="dim")

    console.print()
    console.print(Panel(header, border_style="blue", expand=False))
    console.print()
    console.print(Markdown(summary))
    console.print()


@click.command()
@click.option(
    "--file", "filepath", required=True,
    type=click.Path(exists=True),
    help="Path to the textbook chapter text file.",
)
@click.option(
    "--style",
    type=click.Choice(["concise", "detailed", "study-guide"], case_sensitive=False),
    default="concise", show_default=True,
    help="Summary style.",
)
@click.option("--multi-chapter", is_flag=True, help="Process as multi-chapter file.")
@click.option("--glossary", is_flag=True, help="Generate key terms glossary.")
@click.option("--concept-map", is_flag=True, help="Generate concept map.")
@click.option("--quiz", is_flag=True, help="Generate study questions.")
@click.option("--num-questions", default=5, type=int, help="Number of quiz questions.")
@click.option("--config", "config_path", type=click.Path(), default=None, help="Path to config.yaml.")
@click.option("--verbose", is_flag=True, help="Enable verbose logging.")
def main(filepath: str, style: str, multi_chapter: bool, glossary: bool,
         concept_map: bool, quiz: bool, num_questions: int, config_path: str, verbose: bool) -> None:
    """📚 Textbook Chapter Summarizer — Generate structured summaries with study aids."""
    setup_logging(verbose)
    config = load_config(config_path)

    console.print("[bold blue]📚 Textbook Chapter Summarizer[/bold blue]\n")

    # Check Ollama
    with console.status("[yellow]Checking Ollama connection...[/yellow]"):
        if not check_ollama_running():
            console.print(
                "[bold red]Error:[/bold red] Ollama is not running. "
                "Please start Ollama first with: [cyan]ollama serve[/cyan]"
            )
            sys.exit(1)
    console.print("[green]✓[/green] Ollama is running.\n")

    # Read file
    try:
        text = read_chapter_file(filepath)
    except (FileNotFoundError, IOError) as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)

    if not text.strip():
        console.print("[bold red]Error:[/bold red] The file is empty.")
        sys.exit(1)

    word_count = count_words(text)
    console.print(f"[green]✓[/green] Loaded [cyan]{filepath}[/cyan] ({word_count:,} words)\n")

    if multi_chapter:
        # Multi-chapter processing
        with console.status(f"[yellow]Processing multiple chapters ({style})...[/yellow]"):
            results = summarize_multi_chapter(filepath, style=style, config=config)

        for result in results:
            display_summary(result["summary"], result["title"], style)
    else:
        # Single chapter
        chapter_info = detect_chapter_info(text)
        if chapter_info != "Unknown Chapter":
            console.print(f"[green]✓[/green] Detected: [cyan]{chapter_info}[/cyan]\n")

        with console.status(f"[yellow]Generating {style} summary...[/yellow]"):
            summary = summarize_chapter(text, style, config=config)
        display_summary(summary, chapter_info, style)

    # Optional features
    if glossary:
        with console.status("[yellow]Generating glossary...[/yellow]"):
            glossary_text = generate_glossary(text, config=config)
        console.print(Panel(Markdown(glossary_text), title="📖 Key Terms Glossary", border_style="green"))

    if concept_map:
        with console.status("[yellow]Generating concept map...[/yellow]"):
            map_text = generate_concept_map(text, config=config)
        console.print(Panel(Markdown(map_text), title="🗺️ Concept Map", border_style="yellow"))

    if quiz:
        with console.status(f"[yellow]Generating {num_questions} study questions...[/yellow]"):
            quiz_text = generate_study_questions(text, num_questions=num_questions, config=config)
        console.print(Panel(Markdown(quiz_text), title="❓ Study Questions", border_style="magenta"))

    console.print("[dim]Summary complete.[/dim]")


if __name__ == "__main__":
    main()
