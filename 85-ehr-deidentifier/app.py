"""
EHR De-Identifier - Removes PII from medical records using LLM + regex.

╔══════════════════════════════════════════════════════════════════════╗
║  DISCLAIMER: This tool is for EDUCATIONAL and RESEARCH purposes    ║
║  only. It is NOT certified for HIPAA compliance. Do NOT rely on    ║
║  this tool for actual medical record de-identification in           ║
║  clinical or production settings. Always use certified,            ║
║  validated de-identification tools for real patient data.           ║
║  This is NOT medical or legal advice.                              ║
╚══════════════════════════════════════════════════════════════════════╝
"""

import sys
import os
import re

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from common.llm_client import generate, check_ollama_running

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

console = Console()

DISCLAIMER = (
    "[bold red]⚠ DISCLAIMER:[/bold red] This tool is for [bold]EDUCATIONAL and RESEARCH "
    "purposes ONLY[/bold]. It is [bold]NOT[/bold] certified for HIPAA compliance and must "
    "[bold]NOT[/bold] be used for actual patient data de-identification in clinical or "
    "production environments. This is [bold]NOT[/bold] medical or legal advice."
)

SYSTEM_PROMPT = """You are a medical record de-identification specialist. Your task is to
identify and replace ALL Protected Health Information (PHI) and Personally Identifiable
Information (PII) in the provided text.

Replace each instance with a bracketed placeholder:
- Patient/doctor/staff names → [NAME_1], [NAME_2], etc.
- Dates (DOB, visit dates, etc.) → [DATE_1], [DATE_2], etc.
- Social Security Numbers → [SSN_1], [SSN_2], etc.
- Phone numbers → [PHONE_1], [PHONE_2], etc.
- Addresses/locations → [ADDRESS_1], [ADDRESS_2], etc.
- Medical Record Numbers → [MRN_1], [MRN_2], etc.
- Email addresses → [EMAIL_1], [EMAIL_2], etc.
- Ages over 89 → [AGE]
- Any other identifying information → [ID_1], [ID_2], etc.

IMPORTANT RULES:
1. Replace ALL PII consistently (same name gets same placeholder throughout).
2. Do NOT alter medical terminology, diagnoses, procedures, or medications.
3. Return ONLY the de-identified text with no additional commentary.
4. Preserve the original formatting and structure of the document.
"""


# --- Regex Pre-Processing ---

def regex_preprocess(text: str) -> tuple[str, list[dict]]:
    """Apply regex-based PII detection before LLM processing.

    Returns the partially de-identified text and a log of replacements made.
    """
    replacements = []
    counters = {"SSN": 0, "PHONE": 0, "EMAIL": 0, "DATE": 0}

    patterns = [
        # SSN: 123-45-6789 or 123 45 6789
        (r'\b\d{3}[-\s]\d{2}[-\s]\d{4}\b', "SSN"),
        # Phone: (123) 456-7890, 123-456-7890, 123.456.7890
        (r'\(?\d{3}\)?[-.\s]\d{3}[-.\s]\d{4}\b', "PHONE"),
        # Email
        (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', "EMAIL"),
        # Dates: MM/DD/YYYY, MM-DD-YYYY, Month DD YYYY
        (r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b', "DATE"),
        (r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*'
         r'\s+\d{1,2},?\s+\d{2,4}\b', "DATE"),
    ]

    for pattern, pii_type in patterns:
        def _replacer(match, pii_type=pii_type):
            counters[pii_type] += 1
            placeholder = f"[{pii_type}_{counters[pii_type]}]"
            replacements.append({
                "original": match.group(),
                "placeholder": placeholder,
                "type": pii_type,
            })
            return placeholder

        text = re.sub(pattern, _replacer, text, flags=re.IGNORECASE)

    return text, replacements


def deidentify_text(text: str) -> dict:
    """De-identify text using regex pre-processing followed by LLM analysis.

    Returns a dict with original text, regex-processed text, final result,
    and replacement logs.
    """
    original = text

    # Step 1: Regex pre-processing
    regex_processed, regex_replacements = regex_preprocess(text)

    # Step 2: LLM-based de-identification for remaining PII
    prompt = f"De-identify the following medical text:\n\n{regex_processed}"

    try:
        llm_result = generate(
            prompt=prompt,
            system_prompt=SYSTEM_PROMPT,
            temperature=0.1,
            max_tokens=4096,
        )
    except Exception as e:
        console.print(f"[red]LLM processing failed: {e}[/red]")
        console.print("[yellow]Returning regex-only de-identification.[/yellow]")
        llm_result = regex_processed

    return {
        "original": original,
        "regex_processed": regex_processed,
        "final": llm_result,
        "regex_replacements": regex_replacements,
    }


def display_results(result: dict) -> None:
    """Display de-identification results with rich formatting."""
    console.print()
    console.print(Panel(DISCLAIMER, title="⚕ Important Notice", border_style="red"))
    console.print()

    # Original text
    console.print(Panel(result["original"], title="📄 Original Text", border_style="yellow"))

    # Regex replacements table
    if result["regex_replacements"]:
        table = Table(title="🔍 Regex-Detected PII", show_lines=True)
        table.add_column("Type", style="cyan", width=10)
        table.add_column("Original Value", style="red")
        table.add_column("Placeholder", style="green")
        for r in result["regex_replacements"]:
            table.add_row(r["type"], r["original"], r["placeholder"])
        console.print(table)
        console.print()

    # Final de-identified text
    console.print(
        Panel(result["final"], title="🛡 De-Identified Text", border_style="green")
    )
    console.print()


def read_file(file_path: str) -> str:
    """Read text content from a file."""
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def write_file(file_path: str, content: str) -> None:
    """Write text content to a file."""
    os.makedirs(os.path.dirname(file_path) or ".", exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)


# --- CLI ---

@click.group()
def cli():
    """EHR De-Identifier - Remove PII from medical records.

    ⚠ EDUCATIONAL USE ONLY. Not certified for HIPAA compliance.
    """
    pass


@cli.command()
@click.option("--file", "file_path", required=True, help="Path to the medical record file.")
@click.option("--output", "output_path", default=None, help="Output file path (default: stdout).")
def deidentify(file_path: str, output_path: str):
    """De-identify a medical record file."""
    if not check_ollama_running():
        console.print("[red]Error: Ollama is not running. Please start it first.[/red]")
        raise SystemExit(1)

    try:
        text = read_file(file_path)
    except FileNotFoundError as e:
        console.print(f"[red]Error: {e}[/red]")
        raise SystemExit(1)
    except Exception as e:
        console.print(f"[red]Error reading file: {e}[/red]")
        raise SystemExit(1)

    with console.status("[cyan]De-identifying medical record...[/cyan]"):
        result = deidentify_text(text)

    display_results(result)

    if output_path:
        try:
            write_file(output_path, result["final"])
            console.print(f"[green]✓ De-identified text saved to: {output_path}[/green]")
        except Exception as e:
            console.print(f"[red]Error writing output: {e}[/red]")
            raise SystemExit(1)


@cli.command()
@click.option("--input", "input_text", required=True, help="Text string to de-identify.")
def text(input_text: str):
    """De-identify a text string directly."""
    if not check_ollama_running():
        console.print("[red]Error: Ollama is not running. Please start it first.[/red]")
        raise SystemExit(1)

    with console.status("[cyan]De-identifying text...[/cyan]"):
        result = deidentify_text(input_text)

    display_results(result)


if __name__ == "__main__":
    cli()
