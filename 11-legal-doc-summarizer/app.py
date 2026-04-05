"""
Legal Document Summarizer
Summarizes legal documents, contracts, and agreements.
Extracts key clauses, obligations, dates, parties, and more using a local LLM.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from common.llm_client import chat, generate, check_ollama_running

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown
from rich.text import Text

console = Console()

LEGAL_SYSTEM_PROMPT = """You are an expert legal document analyst. Your task is to analyze legal documents
and extract structured information. Be precise, thorough, and use plain language to explain legal terms.

When analyzing a document, always extract and organize the following sections:

1. **Parties Involved** - List all parties mentioned with their roles (e.g., Buyer, Seller, Licensor).
2. **Key Clauses** - Summarize each major clause or section of the document.
3. **Obligations** - List obligations for each party, clearly stating who must do what.
4. **Important Dates** - Extract all dates including effective date, deadlines, renewal dates, expiration.
5. **Termination Conditions** - How and when can the agreement be terminated by either party.
6. **Penalties & Liabilities** - Any penalties, damages, indemnification, or liability limitations.

If a section has no relevant information in the document, state "Not specified in the document."
Use clear headings and organize the output logically."""


FORMAT_INSTRUCTIONS = {
    "bullet": "Format your response using bullet points for each section. Use markdown headings (##) for section titles.",
    "narrative": "Format your response as a flowing narrative summary, using paragraphs. Use markdown headings (##) for section titles.",
    "detailed": (
        "Format your response with maximum detail. Include direct quotes from the document where relevant. "
        "Use markdown headings (##) for section titles and sub-headings (###) for subsections. "
        "Add a risk assessment note at the end highlighting any concerning clauses."
    ),
}


def read_text_file(filepath: str) -> str:
    """Read and return contents of a plain text file.

    Args:
        filepath: Path to the text file.

    Returns:
        The text content of the file.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file is empty.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    if not content.strip():
        raise ValueError(f"File is empty: {filepath}")

    return content


def read_pdf_file(filepath: str) -> str:
    """Extract text from a PDF file using PyPDF2.

    Args:
        filepath: Path to the PDF file.

    Returns:
        The extracted text content.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If no text could be extracted.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")

    try:
        from PyPDF2 import PdfReader
    except ImportError:
        raise ImportError("PyPDF2 is required for PDF files. Install with: pip install PyPDF2")

    reader = PdfReader(filepath)
    text_parts = []
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text_parts.append(page_text)

    content = "\n".join(text_parts)

    if not content.strip():
        raise ValueError(f"Could not extract text from PDF: {filepath}")

    return content


def read_document(filepath: str) -> str:
    """Read a document file, supporting .txt and .pdf formats.

    Args:
        filepath: Path to the document file.

    Returns:
        The text content extracted from the document.

    Raises:
        ValueError: If the file format is unsupported.
    """
    ext = os.path.splitext(filepath)[1].lower()

    if ext == ".pdf":
        return read_pdf_file(filepath)
    elif ext in (".txt", ".text", ".md"):
        return read_text_file(filepath)
    else:
        # Attempt to read as text
        return read_text_file(filepath)


def summarize_document(text: str, output_format: str = "bullet") -> str:
    """Send document text to the LLM for analysis and summarization.

    Args:
        text: The document text to analyze.
        output_format: One of 'bullet', 'narrative', or 'detailed'.

    Returns:
        The LLM-generated summary string.
    """
    format_instruction = FORMAT_INSTRUCTIONS.get(output_format, FORMAT_INSTRUCTIONS["bullet"])

    # Truncate very long documents to fit within context window
    max_chars = 12000
    if len(text) > max_chars:
        text = text[:max_chars] + "\n\n[... Document truncated for analysis ...]"

    messages = [
        {
            "role": "user",
            "content": (
                f"Analyze the following legal document and extract all key information.\n\n"
                f"{format_instruction}\n\n"
                f"--- DOCUMENT START ---\n{text}\n--- DOCUMENT END ---"
            ),
        }
    ]

    response = chat(
        messages=messages,
        system_prompt=LEGAL_SYSTEM_PROMPT,
        temperature=0.3,
        max_tokens=4096,
    )

    return response


def display_summary(summary: str, filepath: str, output_format: str) -> None:
    """Display the summary using Rich formatting.

    Args:
        summary: The generated summary text.
        filepath: Original file path (for display).
        output_format: The format used for generation.
    """
    filename = os.path.basename(filepath)

    # Header panel
    header = Text()
    header.append("📜 Legal Document Summary\n", style="bold cyan")
    header.append(f"File: ", style="dim")
    header.append(filename, style="bold white")
    header.append(f"\nFormat: ", style="dim")
    header.append(output_format.capitalize(), style="bold yellow")

    console.print()
    console.print(Panel(header, border_style="cyan", padding=(1, 2)))

    # Summary content
    console.print()
    console.print(Panel(
        Markdown(summary),
        title="[bold green]Analysis Results[/bold green]",
        border_style="green",
        padding=(1, 2),
    ))

    # Footer info
    info_table = Table(show_header=False, box=None, padding=(0, 2))
    info_table.add_column("Key", style="dim")
    info_table.add_column("Value", style="white")
    info_table.add_row("Model", "gemma4 (local via Ollama)")
    info_table.add_row("Temperature", "0.3")

    console.print()
    console.print(Panel(info_table, title="[dim]Generation Info[/dim]", border_style="dim"))
    console.print()


@click.command()
@click.option(
    "--file", "-f",
    required=True,
    type=click.Path(),
    help="Path to the legal document (PDF or text file).",
)
@click.option(
    "--format", "-fmt", "output_format",
    type=click.Choice(["bullet", "narrative", "detailed"], case_sensitive=False),
    default="bullet",
    show_default=True,
    help="Output format for the summary.",
)
def main(file: str, output_format: str):
    """📜 Legal Document Summarizer

    Analyze legal documents, contracts, and agreements.
    Extracts key clauses, obligations, dates, parties, and more.
    """
    # Check Ollama is running
    if not check_ollama_running():
        console.print(
            Panel(
                "[bold red]Error:[/bold red] Ollama is not running.\n"
                "Please start Ollama first: [cyan]ollama serve[/cyan]",
                border_style="red",
            )
        )
        sys.exit(1)

    # Read the document
    try:
        console.print(f"\n[dim]Reading document:[/dim] {file}")
        text = read_document(file)
        console.print(f"[dim]Extracted [bold]{len(text)}[/bold] characters of text.[/dim]")
    except FileNotFoundError as e:
        console.print(f"\n[bold red]Error:[/bold red] {e}")
        sys.exit(1)
    except ValueError as e:
        console.print(f"\n[bold red]Error:[/bold red] {e}")
        sys.exit(1)
    except ImportError as e:
        console.print(f"\n[bold red]Error:[/bold red] {e}")
        sys.exit(1)

    # Summarize
    with console.status("[bold cyan]Analyzing document with LLM...[/bold cyan]", spinner="dots"):
        summary = summarize_document(text, output_format)

    # Display results
    display_summary(summary, file, output_format)


if __name__ == "__main__":
    main()
