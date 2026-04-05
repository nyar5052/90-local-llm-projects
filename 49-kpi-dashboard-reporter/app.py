#!/usr/bin/env python3
"""
KPI Dashboard Reporter - Generate narrative KPI reports from metrics data.

Reads KPI data from CSV, compares periods, highlights trends, and generates
professional narrative reports using a local Gemma 4 LLM.
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


def load_kpi_data(file_path: str) -> list[dict]:
    """Load KPI data from a CSV file."""
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


def safe_float(val) -> float:
    """Safely convert a value to float."""
    try:
        return float(str(val).replace(",", "").replace("$", "").replace("%", ""))
    except (ValueError, TypeError):
        return 0.0


def compute_kpi_trends(data: list[dict]) -> dict:
    """Compute trends and changes for each KPI column."""
    if len(data) < 2:
        return {}

    trends = {}
    period_col = None
    for candidate in ["period", "month", "date", "week", "quarter", "year"]:
        for col in data[0].keys():
            if candidate in col.lower():
                period_col = col
                break
        if period_col:
            break

    if not period_col:
        period_col = list(data[0].keys())[0]

    for col in data[0].keys():
        if col == period_col:
            continue
        values = [safe_float(row.get(col, 0)) for row in data]
        if not any(v != 0 for v in values):
            continue

        latest = values[-1]
        previous = values[-2] if len(values) >= 2 else latest
        change = latest - previous
        change_pct = (change / previous * 100) if previous != 0 else 0
        avg = sum(values) / len(values)
        trend = "↑" if change > 0 else ("↓" if change < 0 else "→")

        trends[col] = {
            "latest": latest,
            "previous": previous,
            "change": change,
            "change_pct": change_pct,
            "average": avg,
            "min": min(values),
            "max": max(values),
            "trend": trend,
            "periods": [row.get(period_col, "") for row in data],
            "values": values,
        }

    return trends


def display_kpi_dashboard(trends: dict) -> None:
    """Display KPI trends in a formatted table."""
    table = Table(title="📊 KPI Dashboard", show_lines=True)
    table.add_column("KPI", style="cyan bold", min_width=18)
    table.add_column("Latest", justify="right", width=12)
    table.add_column("Previous", justify="right", width=12)
    table.add_column("Change", justify="right", width=12)
    table.add_column("Change %", justify="right", width=10)
    table.add_column("Trend", justify="center", width=7)
    table.add_column("Avg", justify="right", width=12)

    for kpi, data in trends.items():
        change_color = "green" if data["change"] >= 0 else "red"
        table.add_row(
            kpi,
            f"{data['latest']:,.2f}",
            f"{data['previous']:,.2f}",
            f"[{change_color}]{data['change']:+,.2f}[/{change_color}]",
            f"[{change_color}]{data['change_pct']:+.1f}%[/{change_color}]",
            f"[{change_color}]{data['trend']}[/{change_color}]",
            f"{data['average']:,.2f}",
        )

    console.print(table)


def generate_kpi_report(data: list[dict], trends: dict, period: str) -> str:
    """Generate a narrative KPI report using the LLM."""
    data_text = "\n".join(str(row) for row in data)
    trends_summary = {}
    for kpi, info in trends.items():
        trends_summary[kpi] = {
            "latest": info["latest"],
            "previous": info["previous"],
            "change_pct": f"{info['change_pct']:.1f}%",
            "trend": info["trend"],
            "average": info["average"],
        }
    trends_text = json.dumps(trends_summary, indent=2)

    system_prompt = (
        "You are a business intelligence analyst. Write a professional KPI narrative "
        "report. Highlight wins, flag concerns, and provide actionable insights. "
        "Use specific numbers. Format with markdown headings and bullet points."
    )

    messages = [{"role": "user", "content": (
        f"Generate a KPI narrative report for {period} reporting period.\n\n"
        f"Raw Data:\n{data_text}\n\n"
        f"KPI Trends:\n{trends_text}\n\n"
        "Include:\n"
        "1. Performance Highlights\n"
        "2. Areas of Concern\n"
        "3. Period-over-Period Analysis\n"
        "4. Key Takeaways & Recommendations"
    )}]

    return chat(messages, system_prompt=system_prompt, temperature=0.3, max_tokens=3500)


def generate_alert_summary(trends: dict) -> str:
    """Generate alerts for KPIs with significant changes."""
    alerts = []
    for kpi, data in trends.items():
        if abs(data["change_pct"]) > 10:
            direction = "increased" if data["change_pct"] > 0 else "decreased"
            alerts.append(
                f"⚠️ **{kpi}** {direction} by {abs(data['change_pct']):.1f}% "
                f"({data['previous']:,.2f} → {data['latest']:,.2f})"
            )

    if alerts:
        return "## 🔔 Alerts\n\n" + "\n".join(alerts)
    return "## ✅ No Significant Alerts\n\nAll KPIs within normal range."


@click.command()
@click.option("--file", "-f", required=True, help="Path to KPI data CSV.")
@click.option("--period", "-p", default="monthly", help="Reporting period label (e.g., monthly, Q1-2024).")
@click.option("--alerts/--no-alerts", default=True, help="Show alert summary for significant changes.")
def main(file: str, period: str, alerts: bool) -> None:
    """KPI Dashboard Reporter - Generate narrative KPI reports from metrics data."""
    console.print(Panel(f"📊 [bold blue]KPI Dashboard Reporter - {period}[/bold blue]", expand=False))

    if not check_ollama_running():
        console.print("[red]Error:[/red] Ollama is not running. Start it with: ollama serve")
        sys.exit(1)

    with console.status("[bold green]Loading KPI data..."):
        data = load_kpi_data(file)

    console.print(f"[green]✓[/green] Loaded [bold]{len(data)}[/bold] periods from [bold]{file}[/bold]\n")

    with console.status("[bold green]Computing KPI trends..."):
        trends = compute_kpi_trends(data)

    if not trends:
        console.print("[yellow]Warning:[/yellow] No numeric KPI columns found in the data.")
        sys.exit(1)

    display_kpi_dashboard(trends)
    console.print()

    if alerts:
        alert_text = generate_alert_summary(trends)
        console.print(Panel(Markdown(alert_text), title="🔔 Alerts", border_style="yellow"))
        console.print()

    with console.status("[bold green]Generating narrative report..."):
        report = generate_kpi_report(data, trends, period)

    console.print(Panel(Markdown(report), title=f"📋 KPI Report - {period}", border_style="green"))


if __name__ == "__main__":
    main()
