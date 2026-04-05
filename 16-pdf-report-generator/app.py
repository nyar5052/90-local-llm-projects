"""
PDF Report Generator - Generate structured markdown reports from CSV data using LLM.

Takes a topic and CSV data file, produces a professionally formatted report
with executive summary, key findings, data analysis, recommendations, and conclusion.
"""

import sys
import os
import csv
import statistics
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from common.llm_client import chat, generate, check_ollama_running

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.markdown import Markdown
from rich.table import Table

console = Console()


def read_csv_data(filepath: str) -> tuple[list[str], list[dict]]:
    """
    Read CSV file and return headers and rows.

    Args:
        filepath: Path to the CSV file.

    Returns:
        Tuple of (column_names, list_of_row_dicts).

    Raises:
        FileNotFoundError: If the CSV file does not exist.
        ValueError: If the CSV file is empty or malformed.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"CSV file not found: {filepath}")

    with open(filepath, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise ValueError("CSV file is empty or has no header row.")

        headers = list(reader.fieldnames)
        rows = list(reader)

    if not rows:
        raise ValueError("CSV file contains headers but no data rows.")

    return headers, rows


def summarize_data(headers: list[str], rows: list[dict]) -> str:
    """
    Build a statistical summary of the CSV data for LLM context.

    Args:
        headers: Column names from the CSV.
        rows: List of row dictionaries.

    Returns:
        A formatted string summarizing the dataset.
    """
    summary_parts = [
        f"Dataset Overview:",
        f"  - Total rows: {len(rows)}",
        f"  - Columns ({len(headers)}): {', '.join(headers)}",
        "",
    ]

    for col in headers:
        values = [row.get(col, "").strip() for row in rows if row.get(col, "").strip()]
        if not values:
            summary_parts.append(f"  [{col}]: all empty")
            continue

        # Try numeric analysis
        numeric_vals = []
        for v in values:
            try:
                numeric_vals.append(float(v.replace(",", "")))
            except (ValueError, AttributeError):
                pass

        if numeric_vals and len(numeric_vals) >= len(values) * 0.5:
            col_min = min(numeric_vals)
            col_max = max(numeric_vals)
            col_mean = statistics.mean(numeric_vals)
            col_sum = sum(numeric_vals)
            parts = [
                f"  [{col}] (numeric, {len(numeric_vals)} values):",
                f"    min={col_min:,.2f}, max={col_max:,.2f}, "
                f"mean={col_mean:,.2f}, sum={col_sum:,.2f}",
            ]
            if len(numeric_vals) >= 2:
                col_stdev = statistics.stdev(numeric_vals)
                col_median = statistics.median(numeric_vals)
                parts.append(f"    median={col_median:,.2f}, stdev={col_stdev:,.2f}")
            summary_parts.extend(parts)
        else:
            # Categorical analysis
            unique = set(values)
            summary_parts.append(
                f"  [{col}] (text, {len(values)} values, {len(unique)} unique):"
            )
            if len(unique) <= 10:
                from collections import Counter

                counts = Counter(values).most_common(10)
                for val, cnt in counts:
                    summary_parts.append(f"    '{val}': {cnt}")
            else:
                summary_parts.append(f"    sample: {', '.join(list(unique)[:5])} ...")

    return "\n".join(summary_parts)


def generate_report(topic: str, data_summary: str) -> str:
    """
    Use the LLM to generate a structured markdown report.

    Args:
        topic: The report topic / title.
        data_summary: Statistical summary of the source data.

    Returns:
        Markdown-formatted report string.
    """
    system_prompt = (
        "You are an expert business analyst and report writer. "
        "Generate professional, data-driven reports in clean Markdown format. "
        "Use specific numbers from the data provided. Be concise but thorough."
    )

    user_message = (
        f"Generate a comprehensive report on the topic: **{topic}**\n\n"
        f"Here is the data summary:\n```\n{data_summary}\n```\n\n"
        "Structure the report with these sections:\n"
        "1. **Executive Summary** - Brief overview of findings\n"
        "2. **Key Findings** - Top insights from the data (use bullet points)\n"
        "3. **Data Analysis** - Detailed breakdown with specific numbers\n"
        "4. **Recommendations** - Actionable next steps based on the data\n"
        "5. **Conclusion** - Final summary\n\n"
        "Use markdown formatting: headers, bold, bullet points, and tables where appropriate. "
        "Reference actual numbers from the data summary."
    )

    messages = [{"role": "user", "content": user_message}]

    report = chat(
        messages=messages,
        system_prompt=system_prompt,
        temperature=0.5,
        max_tokens=4096,
    )

    return report


def save_report(content: str, output_path: str, topic: str) -> str:
    """
    Save the generated report to a markdown file with metadata header.

    Args:
        content: The markdown report body.
        output_path: Destination file path.
        topic: Report topic for the header.

    Returns:
        The absolute path of the saved file.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    header = (
        f"---\n"
        f"title: \"{topic}\"\n"
        f"generated: \"{timestamp}\"\n"
        f"generator: \"16-pdf-report-generator\"\n"
        f"---\n\n"
    )

    full_content = header + content

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(full_content)

    return os.path.abspath(output_path)


@click.command()
@click.option("--topic", required=True, type=str, help="Report topic or title.")
@click.option(
    "--data", required=True, type=click.Path(exists=True), help="Path to CSV data file."
)
@click.option(
    "--output",
    default="report.md",
    type=click.Path(),
    help="Output markdown file path (default: report.md).",
)
def main(topic: str, data: str, output: str):
    """📊 Generate a structured report from CSV data using a local LLM."""
    console.print(
        Panel(
            f"[bold cyan]📊 Report Generator[/bold cyan]\n"
            f"Topic: [yellow]{topic}[/yellow]",
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
    preview_table = Table(title=f"Data Preview (first 5 of {len(rows)} rows)")
    for h in headers:
        preview_table.add_column(h, style="cyan")
    for row in rows[:5]:
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
        task = progress.add_task("Generating report with LLM...", total=None)
        report_content = generate_report(topic, data_summary)
        progress.update(task, description="[green]✓ Report generated[/green]")

    # Save
    saved_path = save_report(report_content, output, topic)
    console.print(f"\n[bold green]✓ Report saved to:[/bold green] {saved_path}")

    # Preview
    console.print(Panel(Markdown(report_content[:2000]), title="Report Preview", border_style="green"))

    if len(report_content) > 2000:
        console.print(f"[dim]... ({len(report_content)} chars total, showing first 2000)[/dim]")


if __name__ == "__main__":
    main()
