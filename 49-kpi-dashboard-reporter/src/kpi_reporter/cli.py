"""
KPI Dashboard Reporter - CLI interface.

Provides Click-based commands for generating KPI reports, dashboards,
goal tracking, and anomaly detection.
"""

import sys

import click
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.progress import BarColumn, Progress, TextColumn
from rich.table import Table

from common.llm_client import check_ollama_running
from src.kpi_reporter.core import (
    compute_kpi_trends,
    detect_anomalies,
    generate_alert_summary,
    generate_executive_summary,
    generate_kpi_report,
    load_config,
    load_kpi_data,
    setup_logging,
    track_goals,
)

console = Console()


def _display_kpi_dashboard(trends: dict) -> None:
    """Display KPI trends in a formatted Rich table."""
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


@click.group()
@click.option("--config", "-c", default="config.yaml", help="Path to config file.")
@click.pass_context
def main(ctx: click.Context, config: str) -> None:
    """📊 KPI Dashboard Reporter - Production-grade KPI reporting system."""
    ctx.ensure_object(dict)
    cfg = load_config(config)
    setup_logging(cfg)
    ctx.obj["config"] = cfg


@main.command()
@click.option("--file", "-f", required=True, help="Path to KPI data CSV.")
@click.option("--period", "-p", default="monthly", help="Reporting period label.")
@click.option("--alerts/--no-alerts", default=True, help="Show alert summary.")
@click.pass_context
def report(ctx: click.Context, file: str, period: str, alerts: bool) -> None:
    """Generate a full narrative KPI report."""
    cfg = ctx.obj["config"]

    console.print(
        Panel(f"📊 [bold blue]KPI Dashboard Reporter - {period}[/bold blue]", expand=False)
    )

    if not check_ollama_running():
        console.print("[red]Error:[/red] Ollama is not running. Start it with: ollama serve")
        sys.exit(1)

    with console.status("[bold green]Loading KPI data..."):
        data = load_kpi_data(file)

    console.print(
        f"[green]✓[/green] Loaded [bold]{len(data)}[/bold] periods from [bold]{file}[/bold]\n"
    )

    with console.status("[bold green]Computing KPI trends..."):
        trends = compute_kpi_trends(data)

    if not trends:
        console.print("[yellow]Warning:[/yellow] No numeric KPI columns found in the data.")
        sys.exit(1)

    _display_kpi_dashboard(trends)
    console.print()

    if alerts:
        threshold = cfg.get("alert_threshold_pct", 10)
        alert_text = generate_alert_summary(trends, threshold_pct=threshold)
        console.print(
            Panel(Markdown(alert_text), title="🔔 Alerts", border_style="yellow")
        )
        console.print()

    with console.status("[bold green]Generating narrative report..."):
        report_text = generate_kpi_report(data, trends, period)

    console.print(
        Panel(Markdown(report_text), title=f"📋 KPI Report - {period}", border_style="green")
    )


@main.command()
@click.option("--file", "-f", required=True, help="Path to KPI data CSV.")
@click.pass_context
def dashboard(ctx: click.Context, file: str) -> None:
    """Display an interactive KPI dashboard table."""
    with console.status("[bold green]Loading KPI data..."):
        data = load_kpi_data(file)

    console.print(
        f"[green]✓[/green] Loaded [bold]{len(data)}[/bold] periods from [bold]{file}[/bold]\n"
    )

    trends = compute_kpi_trends(data)
    if not trends:
        console.print("[yellow]Warning:[/yellow] No numeric KPI columns found.")
        return

    _display_kpi_dashboard(trends)


@main.command()
@click.option("--file", "-f", required=True, help="Path to KPI data CSV.")
@click.pass_context
def goals(ctx: click.Context, file: str) -> None:
    """Show goal tracking progress for each KPI."""
    cfg = ctx.obj["config"]
    targets = cfg.get("targets", {})

    if not targets:
        console.print("[yellow]Warning:[/yellow] No targets defined in config.yaml.")
        return

    with console.status("[bold green]Loading KPI data..."):
        data = load_kpi_data(file)

    trends = compute_kpi_trends(data)
    goal_results = track_goals(trends, targets)

    if not goal_results:
        console.print("[yellow]Warning:[/yellow] No matching KPIs found for targets.")
        return

    table = Table(title="🎯 Goal Tracking", show_lines=True)
    table.add_column("KPI", style="cyan bold", min_width=18)
    table.add_column("Actual", justify="right", width=12)
    table.add_column("Target", justify="right", width=12)
    table.add_column("% of Goal", justify="right", width=12)
    table.add_column("Status", justify="center", width=12)

    status_styles = {
        "achieved": "[bold green]✅ Achieved[/bold green]",
        "on_track": "[green]📈 On Track[/green]",
        "at_risk": "[yellow]⚠️ At Risk[/yellow]",
        "behind": "[red]🔴 Behind[/red]",
    }

    for kpi, info in goal_results.items():
        table.add_row(
            kpi,
            f"{info['actual']:,.2f}",
            f"{info['target']:,.2f}",
            f"{info['pct_of_goal']:.1f}%",
            status_styles.get(info["status"], info["status"]),
        )

    console.print(table)
    console.print()

    # Progress bars
    with Progress(
        TextColumn("[bold]{task.description}"),
        BarColumn(bar_width=40),
        TextColumn("{task.percentage:.0f}%"),
        console=console,
    ) as progress:
        for kpi, info in goal_results.items():
            pct = min(info["pct_of_goal"], 100)
            task = progress.add_task(kpi, total=100)
            progress.update(task, completed=pct)


@main.command()
@click.option("--file", "-f", required=True, help="Path to KPI data CSV.")
@click.option("--threshold", "-t", default=None, type=float, help="Std dev threshold.")
@click.pass_context
def anomalies(ctx: click.Context, file: str, threshold: float | None) -> None:
    """Detect and display anomalous KPI values."""
    cfg = ctx.obj["config"]
    anom_cfg = cfg.get("anomaly_detection", {})

    if not anom_cfg.get("enabled", True):
        console.print("[yellow]Anomaly detection is disabled in config.[/yellow]")
        return

    if threshold is None:
        threshold = anom_cfg.get("threshold", 2.0)

    with console.status("[bold green]Loading KPI data..."):
        data = load_kpi_data(file)

    trends = compute_kpi_trends(data)
    detected = detect_anomalies(trends, threshold=threshold)

    if not detected:
        console.print(
            Panel(
                "✅ No anomalies detected.",
                title="🔍 Anomaly Detection",
                border_style="green",
            )
        )
        return

    table = Table(title="🔍 Anomaly Detection", show_lines=True)
    table.add_column("KPI", style="cyan bold", min_width=15)
    table.add_column("Period", width=12)
    table.add_column("Value", justify="right", width=12)
    table.add_column("Mean", justify="right", width=12)
    table.add_column("Std Dev", justify="right", width=12)
    table.add_column("σ Deviation", justify="right", width=12)

    for a in detected:
        table.add_row(
            a["kpi"],
            str(a["period"]),
            f"{a['value']:,.2f}",
            f"{a['mean']:,.2f}",
            f"{a['std_dev']:,.2f}",
            f"[red]{a['deviation']:.1f}σ[/red]",
        )

    console.print(table)


if __name__ == "__main__":
    main()
