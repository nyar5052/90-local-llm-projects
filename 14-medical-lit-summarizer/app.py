"""
Medical Literature Summarizer

Summarizes medical/scientific papers by extracting methodology,
findings, conclusions, and other key sections using a local LLM.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from common.llm_client import chat, generate, check_ollama_running

import click
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.text import Text

console = Console()

DETAIL_PROMPTS = {
    "brief": "Provide a concise 1-2 sentence summary for each section. Focus only on the most critical points.",
    "standard": "Provide a clear and thorough summary for each section with moderate detail.",
    "comprehensive": "Provide an in-depth, detailed analysis for each section. Include specific data points, nuances, and context.",
}

SECTIONS = [
    ("title_authors", "Title & Authors", "Extract the paper title and list of authors. Format as:\nTitle: <title>\nAuthors: <authors>"),
    ("abstract_summary", "Abstract Summary", "Summarize the abstract of this paper in a clear paragraph."),
    ("methodology", "Methodology", "Describe the research methodology including study design, participants/samples, procedures, and tools used."),
    ("key_findings", "Key Findings", "List the key findings and results of this research."),
    ("statistical_results", "Statistical Results", "Extract and summarize any statistical results, p-values, confidence intervals, effect sizes, or quantitative outcomes."),
    ("conclusions", "Conclusions", "Summarize the main conclusions drawn by the authors."),
    ("limitations", "Limitations", "Identify the limitations of the study as noted by the authors or apparent from the methodology."),
    ("future_work", "Future Work", "Describe any future research directions or recommendations suggested by the authors."),
]


def read_paper(file_path: str) -> str:
    """Read a paper from a text file and return its contents.

    Args:
        file_path: Path to the paper text file.

    Returns:
        The full text of the paper.

    Raises:
        FileNotFoundError: If the file does not exist.
        IOError: If the file cannot be read.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Paper file not found: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    if not content.strip():
        raise ValueError("Paper file is empty.")

    return content


def extract_section(paper_text: str, section_key: str, section_prompt: str, detail_level: str) -> str:
    """Extract a specific section from a paper using the LLM.

    Args:
        paper_text: The full text of the paper.
        section_key: Internal key for the section.
        section_prompt: Prompt describing what to extract.
        detail_level: One of brief, standard, comprehensive.

    Returns:
        The extracted section text from the LLM.
    """
    detail_instruction = DETAIL_PROMPTS[detail_level]

    system_prompt = (
        "You are an expert medical and scientific literature analyst. "
        "You carefully read research papers and extract structured information. "
        "Be accurate and faithful to the source material. "
        f"{detail_instruction}"
    )

    messages = [
        {
            "role": "user",
            "content": (
                f"Analyze the following medical/scientific paper and {section_prompt}\n\n"
                f"--- PAPER START ---\n{paper_text}\n--- PAPER END ---"
            ),
        }
    ]

    return chat(messages, system_prompt=system_prompt, temperature=0.3, max_tokens=1024)


def summarize_paper(paper_text: str, detail_level: str = "standard") -> dict:
    """Summarize a medical/scientific paper into structured sections.

    Args:
        paper_text: The full text of the paper.
        detail_level: Level of detail (brief, standard, comprehensive).

    Returns:
        Dictionary mapping section keys to extracted text.
    """
    results = {}

    for section_key, section_title, section_prompt in SECTIONS:
        console.print(f"  [dim]Extracting {section_title}...[/dim]")
        try:
            results[section_key] = extract_section(
                paper_text, section_key, section_prompt, detail_level
            )
        except Exception as e:
            results[section_key] = f"[Error extracting section: {e}]"

    return results


def format_output(results: dict) -> None:
    """Display the summarized paper results using Rich formatting.

    Args:
        results: Dictionary mapping section keys to extracted text.
    """
    console.print()
    console.print(
        Panel(
            "[bold cyan]Medical Literature Summary[/bold cyan]",
            border_style="bright_blue",
            expand=False,
        )
    )
    console.print()

    section_styles = {
        "title_authors": "bold white",
        "abstract_summary": "green",
        "methodology": "yellow",
        "key_findings": "bright_cyan",
        "statistical_results": "magenta",
        "conclusions": "bright_green",
        "limitations": "red",
        "future_work": "blue",
    }

    section_emojis = {
        "title_authors": "📄",
        "abstract_summary": "📋",
        "methodology": "🔬",
        "key_findings": "🔑",
        "statistical_results": "📊",
        "conclusions": "✅",
        "limitations": "⚠️",
        "future_work": "🔮",
    }

    for section_key, section_title, _ in SECTIONS:
        content = results.get(section_key, "No content extracted.")
        style = section_styles.get(section_key, "white")
        emoji = section_emojis.get(section_key, "📌")

        console.print(
            Panel(
                Markdown(content),
                title=f"{emoji} {section_title}",
                border_style=style,
                padding=(1, 2),
            )
        )
        console.print()


@click.command()
@click.option(
    "--paper",
    required=True,
    type=click.Path(),
    help="Path to the medical/scientific paper text file.",
)
@click.option(
    "--detail",
    type=click.Choice(["brief", "standard", "comprehensive"], case_sensitive=False),
    default="standard",
    show_default=True,
    help="Level of detail for the summary.",
)
def main(paper: str, detail: str):
    """🔬 Medical Literature Summarizer

    Summarizes medical and scientific papers by extracting key sections
    including methodology, findings, conclusions, and more.
    """
    console.print(
        Panel(
            "[bold bright_blue]🔬 Medical Literature Summarizer[/bold bright_blue]",
            border_style="bright_blue",
        )
    )

    # Verify Ollama is running
    console.print("[dim]Checking Ollama connection...[/dim]")
    if not check_ollama_running():
        console.print("[bold red]Error:[/bold red] Ollama is not running. Please start it first.")
        raise SystemExit(1)
    console.print("[green]✓[/green] Ollama is running.\n")

    # Read the paper
    try:
        console.print(f"[dim]Reading paper:[/dim] {paper}")
        paper_text = read_paper(paper)
        console.print(f"[green]✓[/green] Loaded paper ({len(paper_text):,} characters)\n")
    except (FileNotFoundError, ValueError) as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise SystemExit(1)

    # Summarize
    console.print(f"[dim]Detail level:[/dim] [bold]{detail}[/bold]\n")
    console.print("[bold]Analyzing paper...[/bold]")
    results = summarize_paper(paper_text, detail_level=detail)

    # Display results
    format_output(results)
    console.print("[bold green]Summary complete.[/bold green]\n")


if __name__ == "__main__":
    main()
