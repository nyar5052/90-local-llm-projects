"""
Textbook Chapter Summarizer
============================
Generates chapter-by-chapter textbook summaries with key concepts,
definitions, formulas, and review questions using a local LLM.
"""

import sys
import os
import re

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from common.llm_client import chat, generate, check_ollama_running

import click
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.text import Text

console = Console()

STYLE_PROMPTS = {
    "concise": (
        "Summarize the following textbook chapter in a concise bullet-point format.\n"
        "Return your response in this exact structure:\n\n"
        "## Chapter Title\n"
        "Identify the chapter title and number if present.\n\n"
        "## Key Concepts\n"
        "- List each key concept as a short bullet point.\n\n"
        "## Definitions\n"
        "- **Term**: Brief definition (one sentence max).\n\n"
        "## Formulas & Equations\n"
        "- List any formulas or equations found. Write 'None found.' if there are none.\n\n"
        "## Summary\n"
        "A brief 3-5 sentence summary of the chapter.\n\n"
        "## Review Questions\n"
        "- Generate 3-5 short review questions based on the content.\n\n"
        "---\n"
        "Chapter text:\n\n{text}"
    ),
    "detailed": (
        "Provide a detailed, in-depth summary of the following textbook chapter.\n"
        "Return your response in this exact structure:\n\n"
        "## Chapter Title\n"
        "Identify the chapter title and number if present.\n\n"
        "## Key Concepts\n"
        "For each key concept, provide a full paragraph explanation with examples "
        "where relevant.\n\n"
        "## Definitions\n"
        "- **Term**: Full definition with context and usage examples.\n\n"
        "## Formulas & Equations\n"
        "- List any formulas or equations, explaining each variable and when to apply them. "
        "Write 'None found.' if there are none.\n\n"
        "## Summary\n"
        "A comprehensive summary covering all major points (8-12 sentences).\n\n"
        "## Review Questions\n"
        "- Generate 5-8 thought-provoking review questions, including both factual recall "
        "and critical thinking questions.\n\n"
        "---\n"
        "Chapter text:\n\n{text}"
    ),
    "study-guide": (
        "Create a study guide from the following textbook chapter in a flashcard-style "
        "question-and-answer format.\n"
        "Return your response in this exact structure:\n\n"
        "## Chapter Title\n"
        "Identify the chapter title and number if present.\n\n"
        "## Key Concepts (Q&A)\n"
        "For each key concept:\n"
        "- **Q:** A question about the concept.\n"
        "- **A:** A clear, concise answer.\n\n"
        "## Definitions (Flashcards)\n"
        "For each important term:\n"
        "- **Q:** What is [term]?\n"
        "- **A:** Definition and brief explanation.\n\n"
        "## Formulas & Equations\n"
        "- **Q:** What formula is used for [purpose]?\n"
        "- **A:** The formula with variable explanations. "
        "Write 'None found.' if there are none.\n\n"
        "## Summary\n"
        "A concise chapter summary suitable for quick review (4-6 sentences).\n\n"
        "## Practice Questions\n"
        "- 5-8 practice questions with answers, ranging from easy to challenging.\n\n"
        "---\n"
        "Chapter text:\n\n{text}"
    ),
}

SYSTEM_PROMPT = (
    "You are an expert academic tutor and textbook summarizer. "
    "You produce clear, accurate, and well-structured summaries that help "
    "students understand and review textbook material efficiently. "
    "Always preserve technical accuracy, especially for formulas and definitions."
)


def read_chapter_file(filepath: str) -> str:
    """Read and return the contents of a textbook chapter file.

    Args:
        filepath: Path to the text file containing the chapter.

    Returns:
        The chapter text as a string.

    Raises:
        FileNotFoundError: If the file does not exist.
        IOError: If the file cannot be read.
    """
    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")

    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()


def detect_chapter_info(text: str) -> str:
    """Attempt to detect chapter number and title from the text.

    Searches for common chapter heading patterns at the start of the text.

    Args:
        text: The raw chapter text.

    Returns:
        Detected chapter heading or 'Unknown Chapter'.
    """
    patterns = [
        r"(?i)^(chapter\s+\d+[\s:.\-]+.+)$",
        r"(?i)^(chapter\s+\d+)$",
        r"(?i)^(ch\.?\s*\d+[\s:.\-]+.+)$",
        r"(?i)^(unit\s+\d+[\s:.\-]+.+)$",
        r"(?i)^(lesson\s+\d+[\s:.\-]+.+)$",
    ]
    for line in text.strip().splitlines()[:10]:
        stripped = line.strip()
        for pattern in patterns:
            match = re.match(pattern, stripped)
            if match:
                return match.group(1).strip()
    return "Unknown Chapter"


def summarize_chapter(text: str, style: str = "concise") -> str:
    """Generate a structured summary of a textbook chapter using the LLM.

    Args:
        text: The full text of the textbook chapter.
        style: Summary style — 'concise', 'detailed', or 'study-guide'.

    Returns:
        The LLM-generated summary as a string.

    Raises:
        ValueError: If an invalid style is provided.
    """
    if style not in STYLE_PROMPTS:
        raise ValueError(
            f"Invalid style '{style}'. Choose from: {', '.join(STYLE_PROMPTS)}"
        )

    prompt = STYLE_PROMPTS[style].format(text=text)

    response = generate(
        prompt=prompt,
        system_prompt=SYSTEM_PROMPT,
        temperature=0.4,
        max_tokens=4096,
    )
    return response


def display_summary(summary: str, chapter_info: str, style: str) -> None:
    """Display the formatted summary in the terminal using Rich.

    Args:
        summary: The generated summary text (Markdown).
        chapter_info: Detected chapter title/number.
        style: The summary style used.
    """
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
    "--file",
    "filepath",
    required=True,
    type=click.Path(exists=True),
    help="Path to the textbook chapter text file.",
)
@click.option(
    "--style",
    type=click.Choice(["concise", "detailed", "study-guide"], case_sensitive=False),
    default="concise",
    show_default=True,
    help="Summary style: concise (bullets), detailed (full), or study-guide (Q&A).",
)
def main(filepath: str, style: str) -> None:
    """📚 Textbook Chapter Summarizer

    Generate structured summaries of textbook chapters with key concepts,
    definitions, formulas, and review questions.
    """
    console.print("[bold blue]📚 Textbook Chapter Summarizer[/bold blue]\n")

    # Check Ollama is running
    with console.status("[yellow]Checking Ollama connection...[/yellow]"):
        if not check_ollama_running():
            console.print(
                "[bold red]Error:[/bold red] Ollama is not running. "
                "Please start Ollama first with: [cyan]ollama serve[/cyan]"
            )
            sys.exit(1)
    console.print("[green]✓[/green] Ollama is running.\n")

    # Read chapter file
    try:
        text = read_chapter_file(filepath)
    except (FileNotFoundError, IOError) as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)

    if not text.strip():
        console.print("[bold red]Error:[/bold red] The file is empty.")
        sys.exit(1)

    word_count = len(text.split())
    console.print(f"[green]✓[/green] Loaded [cyan]{filepath}[/cyan] ({word_count:,} words)\n")

    # Detect chapter info
    chapter_info = detect_chapter_info(text)
    if chapter_info != "Unknown Chapter":
        console.print(f"[green]✓[/green] Detected: [cyan]{chapter_info}[/cyan]\n")

    # Generate summary
    with console.status(f"[yellow]Generating {style} summary...[/yellow]"):
        try:
            summary = summarize_chapter(text, style)
        except Exception as e:
            console.print(f"[bold red]Error generating summary:[/bold red] {e}")
            sys.exit(1)

    # Display results
    display_summary(summary, chapter_info, style)
    console.print("[dim]Summary complete.[/dim]")


if __name__ == "__main__":
    main()
