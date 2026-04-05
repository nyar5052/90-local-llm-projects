#!/usr/bin/env python3
"""
Financial Report Generator - Generate narrative financial reports from data.

Reads financial data from CSV and generates professional narrative reports
covering income statements, balance sheets, and key financial ratios
using a local Gemma 4 LLM.
"""

import sys
import os
import csv
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown

from common.llm_client import chat, check_ollama_running

console = Console()


def load_financial_data(file_path: str) -> list[dict]:
    """Load financial data from a CSV file."""
    if not os.path.exists(file_path):
        console.print(f"[red]Error:[/red] File '{file_path}' not found.")
        sys.exit(1)
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        if not rows:
            console.print("[red]Error:[/red] CSV file is empty.")
            sys.exit(1)
        return rows
    except Exception as e:
        console.print(f"[red]Error reading CSV:[/red] {e}")
        sys.exit(1)


def compute_financial_metrics(data: list[dict]) -> dict:
    """Compute key financial metrics from the data."""
    metrics = {}

    def safe_float(val):
        try:
            return float(str(val).replace(",", "").replace("$", "").replace("%", ""))
        except (ValueError, TypeError):
            return 0.0

    numeric_cols = {}
    for col in data[0].keys():
        values = [safe_float(row.get(col, 0)) for row in data]
        if any(v != 0 for v in values):
            try:
                float(str(data[0][col]).replace(",", "").replace("$", "").replace("%", ""))
                numeric_cols[col] = values
            except (ValueError, TypeError):
                continue

    for col, values in numeric_cols.items():
        metrics[col] = {
            "total": sum(values),
            "average": sum(values) / len(values) if values else 0,
            "min": min(values),
            "max": max(values),
            "latest": values[-1],
        }

    return metrics


def display_financial_summary(data: list[dict], metrics: dict) -> None:
    """Display a summary table of financial data."""
    table = Table(title="💰 Financial Data Summary", show_lines=True)
    table.add_column("Metric", style="cyan bold", min_width=18)
    table.add_column("Total", justify="right", width=14)
    table.add_column("Average", justify="right", width=14)
    table.add_column("Latest", justify="right", width=14)

    for col, vals in metrics.items():
        table.add_row(
            col,
            f"${vals['total']:,.2f}",
            f"${vals['average']:,.2f}",
            f"${vals['latest']:,.2f}",
        )

    console.print(table)


def generate_financial_report(data: list[dict], metrics: dict, period: str) -> str:
    """Generate a narrative financial report using the LLM."""
    data_text = "\n".join(str(row) for row in data[:20])
    metrics_text = json.dumps(metrics, indent=2, default=str)

    system_prompt = (
        "You are a senior financial analyst and CPA. Write a professional narrative "
        "financial report suitable for board presentation. Use proper financial "
        "terminology, include specific numbers, and provide insights on performance. "
        "Format with markdown headings, bullet points, and emphasis."
    )

    messages = [{"role": "user", "content": (
        f"Generate a financial report for period: {period}\n\n"
        f"Financial Data:\n{data_text}\n\n"
        f"Computed Metrics:\n{metrics_text}\n\n"
        "Include these sections:\n"
        "1. Executive Summary\n"
        "2. Revenue & Income Analysis\n"
        "3. Expense Analysis\n"
        "4. Key Financial Ratios & Indicators\n"
        "5. Period-over-Period Comparison\n"
        "6. Outlook & Recommendations"
    )}]

    return chat(messages, system_prompt=system_prompt, temperature=0.3, max_tokens=4000)


def generate_executive_summary(metrics: dict, period: str) -> str:
    """Generate a brief executive summary."""
    metrics_text = json.dumps(metrics, indent=2, default=str)

    system_prompt = (
        "You are a CFO writing a brief executive summary. Be concise but insightful. "
        "Highlight key figures and trends. Use markdown formatting."
    )

    messages = [{"role": "user", "content": (
        f"Write a 3-paragraph executive summary for {period}:\n\n"
        f"Key Metrics:\n{metrics_text}"
    )}]

    return chat(messages, system_prompt=system_prompt, temperature=0.3, max_tokens=1500)


@click.command()
@click.option("--file", "-f", required=True, help="Path to financial data CSV.")
@click.option("--period", "-p", required=True, help="Reporting period (e.g., Q4-2024).")
@click.option("--full/--summary", default=True, help="Full report or executive summary only.")
def main(file: str, period: str, full: bool) -> None:
    """Financial Report Generator - Generate narrative financial reports."""
    console.print(Panel(f"💰 [bold blue]Financial Report Generator - {period}[/bold blue]", expand=False))

    if not check_ollama_running():
        console.print("[red]Error:[/red] Ollama is not running. Start it with: ollama serve")
        sys.exit(1)

    with console.status("[bold green]Loading financial data..."):
        data = load_financial_data(file)

    console.print(f"[green]✓[/green] Loaded [bold]{len(data)}[/bold] records from [bold]{file}[/bold]\n")

    with console.status("[bold green]Computing financial metrics..."):
        metrics = compute_financial_metrics(data)

    display_financial_summary(data, metrics)
    console.print()

    if full:
        with console.status("[bold green]Generating financial report..."):
            report = generate_financial_report(data, metrics, period)
        console.print(Panel(Markdown(report), title=f"📋 Financial Report - {period}", border_style="green"))
    else:
        with console.status("[bold green]Generating executive summary..."):
            summary = generate_executive_summary(metrics, period)
        console.print(Panel(Markdown(summary), title=f"📋 Executive Summary - {period}", border_style="green"))


if __name__ == "__main__":
    main()
