"""
EHR De-Identifier CLI - Command-line interface for PII removal.

⚠️ EDUCATIONAL and RESEARCH use ONLY. NOT certified for HIPAA compliance.
Do NOT use on real patient data.
"""

import os
import sys
import glob as globmod

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .core import (
    DISCLAIMER,
    DEFAULT_PII_RULES,
    HIPAA_IDENTIFIERS,
    AuditLog,
    ValidationReport,
    check_ollama_running,
    deidentify_text,
    configurable_regex_preprocess,
    batch_deidentify,
    read_file,
    write_file,
    display_results,
)

console = Console()

# Module-level audit log shared across CLI commands within a session
_audit = AuditLog()


def _print_disclaimer() -> None:
    """Print the HIPAA disclaimer prominently."""
    console.print()
    console.print(
        Panel(DISCLAIMER, title="⛔ CRITICAL DISCLAIMER ⛔", border_style="red bold")
    )
    console.print()


@click.group()
def cli():
    """🛡️ EHR De-Identifier - Remove PII from medical records.

    \b
    ⛔ EDUCATIONAL USE ONLY. NOT certified for HIPAA compliance.
    ⛔ Do NOT use on real patient data.
    ⛔ Always use certified tools for real PHI.
    """
    pass


@cli.command()
@click.option(
    "--file",
    "file_path",
    required=True,
    help="Path to the medical record file.",
)
@click.option(
    "--output",
    "output_path",
    default=None,
    help="Output file path (default: stdout).",
)
def deidentify(file_path: str, output_path: str):
    """De-identify a medical record file.

    ⚠️ NOT certified for HIPAA compliance.
    """
    _print_disclaimer()

    if not check_ollama_running():
        console.print(
            "[red bold]Error: Ollama is not running. Please start it first.[/red bold]"
        )
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

    _audit.log_operation(
        "deidentify_file", file_path, result["regex_replacements"], "success"
    )
    display_results(result)

    if output_path:
        try:
            write_file(output_path, result["final"])
            console.print(
                f"[green]✓ De-identified text saved to: {output_path}[/green]"
            )
        except Exception as e:
            console.print(f"[red]Error writing output: {e}[/red]")
            raise SystemExit(1)


@cli.command()
@click.option(
    "--input", "input_text", required=True, help="Text string to de-identify."
)
def text(input_text: str):
    """De-identify a text string directly.

    ⚠️ NOT certified for HIPAA compliance.
    """
    _print_disclaimer()

    if not check_ollama_running():
        console.print(
            "[red bold]Error: Ollama is not running. Please start it first.[/red bold]"
        )
        raise SystemExit(1)

    with console.status("[cyan]De-identifying text...[/cyan]"):
        result = deidentify_text(input_text)

    _audit.log_operation(
        "deidentify_text", "<inline>", result["regex_replacements"], "success"
    )
    display_results(result)


@cli.command()
@click.option(
    "--directory",
    required=True,
    help="Directory containing files to process.",
)
@click.option(
    "--output-dir",
    default=None,
    help="Output directory for de-identified files.",
)
@click.option(
    "--pattern",
    default="*.txt",
    help="Glob pattern for files to process (default: *.txt).",
)
def batch(directory: str, output_dir: str, pattern: str):
    """Batch de-identify multiple files in a directory.

    ⚠️ NOT certified for HIPAA compliance.
    """
    _print_disclaimer()

    if not check_ollama_running():
        console.print(
            "[red bold]Error: Ollama is not running. Please start it first.[/red bold]"
        )
        raise SystemExit(1)

    search_pattern = os.path.join(directory, pattern)
    file_paths = sorted(globmod.glob(search_pattern))

    if not file_paths:
        console.print(
            f"[yellow]No files matching '{pattern}' found in {directory}[/yellow]"
        )
        return

    console.print(f"[cyan]Found {len(file_paths)} file(s) to process.[/cyan]")

    with console.status("[cyan]Batch de-identifying...[/cyan]"):
        results = batch_deidentify(file_paths, output_dir, _audit)

    # Summary
    success = sum(1 for r in results if r.get("status") == "success")
    errors = sum(1 for r in results if r.get("status") == "error")

    table = Table(title="📦 Batch Processing Results", show_lines=True)
    table.add_column("File", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("PII Found", style="yellow")

    for r in results:
        status_str = (
            "✅ Success" if r.get("status") == "success" else f"❌ {r.get('error', 'Error')}"
        )
        pii_count = str(len(r.get("regex_replacements", [])))
        table.add_row(r.get("source_file", "?"), status_str, pii_count)

    console.print(table)
    console.print(
        f"\n[green]✓ {success} succeeded[/green], [red]{errors} failed[/red]"
    )

    console.print(
        Panel(
            "[bold red]⚠️ Batch output has NOT been validated for HIPAA compliance. "
            "Manual review is ALWAYS required.[/bold red]",
            border_style="red",
        )
    )


@cli.command()
def audit():
    """Display the audit log for this session.

    ⚠️ NOT a HIPAA-compliant audit trail.
    """
    _print_disclaimer()

    log = _audit.get_log()
    if not log:
        console.print("[yellow]No audit log entries yet.[/yellow]")
        return

    summary = _audit.get_summary()
    console.print(
        Panel(
            f"Total operations: {summary['total_operations']}\n"
            f"Total PII found: {summary.get('total_pii_found', 0)}\n"
            f"Successes: {summary.get('success_count', 0)}\n"
            f"Errors: {summary.get('error_count', 0)}",
            title="📋 Audit Summary",
            border_style="blue",
        )
    )

    table = Table(title="📋 Audit Log Entries", show_lines=True)
    table.add_column("Timestamp", style="dim")
    table.add_column("Operation", style="cyan")
    table.add_column("Source", style="yellow")
    table.add_column("PII Count", style="red")
    table.add_column("Status", style="green")

    for entry in log:
        table.add_row(
            entry["timestamp"],
            entry["operation"],
            entry["input_source"],
            str(entry["pii_count"]),
            entry["status"],
        )

    console.print(table)


@cli.command()
@click.option(
    "--file",
    "file_path",
    required=True,
    help="Path to file to validate.",
)
def validate(file_path: str):
    """Run a validation report on a de-identified file.

    ⚠️ Automated check only. Manual review is ALWAYS required.
    """
    _print_disclaimer()

    if not check_ollama_running():
        console.print(
            "[red bold]Error: Ollama is not running. Please start it first.[/red bold]"
        )
        raise SystemExit(1)

    try:
        text = read_file(file_path)
    except FileNotFoundError as e:
        console.print(f"[red]Error: {e}[/red]")
        raise SystemExit(1)

    with console.status("[cyan]Processing and validating...[/cyan]"):
        result = deidentify_text(text)
        report = ValidationReport(
            result["original"], result["final"], result["regex_replacements"]
        )

    console.print(report.generate_report())
    console.print()
    console.print(
        Panel(
            "[bold red]⚠️ This validation is NOT a substitute for manual review. "
            "This tool is NOT certified for HIPAA compliance.[/bold red]",
            border_style="red",
        )
    )


@cli.command()
def rules():
    """List all configured PII detection rules."""
    _print_disclaimer()

    table = Table(title="⚙️ PII Detection Rules", show_lines=True)
    table.add_column("Rule", style="cyan")
    table.add_column("Placeholder", style="green")
    table.add_column("Enabled", style="yellow")
    table.add_column("Description", style="white")

    for name, rule in DEFAULT_PII_RULES.items():
        enabled = "✅" if rule["enabled"] else "❌"
        table.add_row(name, rule["placeholder"], enabled, rule["description"])

    console.print(table)

    console.print()
    console.print(
        Panel(
            "[bold]HIPAA Safe Harbor – 18 Identifiers:[/bold]\n"
            + "\n".join(
                f"  {i + 1}. {ident}"
                for i, ident in enumerate(HIPAA_IDENTIFIERS)
            ),
            title="📋 HIPAA Reference",
            border_style="blue",
        )
    )


if __name__ == "__main__":
    cli()
