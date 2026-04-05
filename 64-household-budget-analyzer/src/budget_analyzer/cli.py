#!/usr/bin/env python3
"""Click CLI for the Household Budget Analyzer."""

import sys
import os

# LLM client integration
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from common.llm_client import check_ollama_running

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown

from budget_analyzer.core import (
    load_expenses,
    filter_by_month,
    compute_category_breakdown,
    compute_total,
    display_breakdown,
    analyze_budget,
    compare_months,
    categorize_expense,
    compare_budget_vs_actual,
    SavingsGoal,
    detect_recurring,
    compute_monthly_trends,
    get_top_expenses,
    get_config,
    setup_logging,
)

console = Console()


def _ensure_ollama() -> None:
    """Exit if Ollama is not running."""
    if not check_ollama_running():
        console.print("[red]Error:[/red] Ollama is not running. Start with: [bold]ollama serve[/bold]")
        sys.exit(1)


@click.group()
@click.option('--config', '-C', 'config_path', default=None, type=click.Path(), help='Path to config.yaml')
@click.pass_context
def cli(ctx, config_path):
    """💰 Household Budget Analyzer - AI-powered expense analysis."""
    ctx.ensure_object(dict)
    setup_logging()
    if config_path:
        from budget_analyzer.core import load_config, _CONFIG
        ctx.obj['config'] = load_config(config_path)
    else:
        ctx.obj['config'] = get_config()


# -----------------------------------------------------------------------
# Original commands (restructured)
# -----------------------------------------------------------------------


@cli.command()
@click.option('--file', '-f', 'file_path', required=True, type=click.Path(exists=True), help='Expenses CSV file')
@click.option('--month', '-m', default=None, help='Filter month (e.g. "March 2024")')
@click.pass_context
def analyze(ctx, file_path, month):
    """Get AI-powered budget analysis."""
    _ensure_ollama()
    expenses = load_expenses(file_path)
    if month:
        expenses = filter_by_month(expenses, month)
        if not expenses:
            console.print(f"[yellow]No expenses found for {month}[/yellow]")
            return

    categories = compute_category_breakdown(expenses)
    total = compute_total(expenses)

    display_breakdown(categories, total)
    console.print(f"\n[dim]Transactions: {len(expenses)} | Period: {month or 'All time'}[/dim]\n")

    with console.status("[bold green]Analyzing your budget..."):
        result = analyze_budget(expenses, categories, total, month)
    console.print(Panel(Markdown(result), title="📊 Budget Analysis", border_style="green"))


@cli.command()
@click.option('--file', '-f', 'file_path', required=True, type=click.Path(exists=True), help='Expenses CSV file')
@click.option('--month', '-m', default=None, help='Filter month')
def breakdown(file_path, month):
    """Show category breakdown."""
    expenses = load_expenses(file_path)
    if month:
        expenses = filter_by_month(expenses, month)
    categories = compute_category_breakdown(expenses)
    total = compute_total(expenses)
    display_breakdown(categories, total)
    console.print(f"\n[dim]Transactions: {len(expenses)} | Period: {month or 'All time'}[/dim]")


@cli.command()
@click.option('--file', '-f', 'file_path', required=True, type=click.Path(exists=True), help='Expenses CSV file')
def compare(file_path):
    """Compare spending across months."""
    _ensure_ollama()
    expenses = load_expenses(file_path)
    with console.status("[bold green]Comparing monthly trends..."):
        result = compare_months(expenses)
    console.print(Panel(Markdown(result), title="📈 Monthly Comparison", border_style="cyan"))


# -----------------------------------------------------------------------
# New commands
# -----------------------------------------------------------------------


@cli.command()
@click.option('--file', '-f', 'file_path', required=True, type=click.Path(exists=True), help='Expenses CSV file')
@click.option('--month', '-m', default=None, help='Filter month')
@click.pass_context
def categorize(ctx, file_path, month):
    """Auto-categorize expenses using keyword rules."""
    config = ctx.obj.get('config', get_config())
    expenses = load_expenses(file_path)
    if month:
        expenses = filter_by_month(expenses, month)

    table = Table(title="🏷️  Auto-Categorization Results", show_lines=True)
    table.add_column("Date", style="dim", min_width=12)
    table.add_column("Description", style="white", min_width=25)
    table.add_column("Original Category", style="cyan", min_width=15)
    table.add_column("Auto Category", style="green", min_width=15)
    table.add_column("Amount", style="yellow", justify="right", min_width=10)

    for exp in expenses:
        desc = exp.get("description", exp.get("Description", ""))
        original = exp.get("category", exp.get("Category", ""))
        auto = categorize_expense(desc, config)
        amount = exp.get("amount", exp.get("Amount", "0"))
        date = exp.get("date", exp.get("Date", ""))
        match_style = "green" if auto == original else "red"
        table.add_row(date, desc, original, f"[{match_style}]{auto}[/{match_style}]", f"${float(str(amount).replace('$','').replace(',','')):,.2f}")

    console.print(table)


@cli.command("budget-check")
@click.option('--file', '-f', 'file_path', required=True, type=click.Path(exists=True), help='Expenses CSV file')
@click.option('--month', '-m', default=None, help='Filter month')
@click.pass_context
def budget_check(ctx, file_path, month):
    """Compare spending against budget limits."""
    config = ctx.obj.get('config', get_config())
    expenses = load_expenses(file_path)
    if month:
        expenses = filter_by_month(expenses, month)

    categories = compute_category_breakdown(expenses)
    results = compare_budget_vs_actual(categories, config)

    table = Table(title="📋 Budget vs Actual", show_lines=True)
    table.add_column("Category", style="cyan", min_width=15)
    table.add_column("Budget", style="blue", justify="right", min_width=10)
    table.add_column("Actual", style="white", justify="right", min_width=10)
    table.add_column("Difference", justify="right", min_width=12)
    table.add_column("Status", min_width=8)

    for r in results:
        diff_style = "green" if r['status'] == 'under' else "red"
        status_icon = "✅" if r['status'] == 'under' else "⚠️"
        table.add_row(
            r['category'],
            f"${r['budget']:,.2f}",
            f"${r['actual']:,.2f}",
            f"[{diff_style}]${r['difference']:,.2f}[/{diff_style}]",
            f"{status_icon} {r['status'].upper()}",
        )

    console.print(table)
    total_budget = sum(r['budget'] for r in results)
    total_actual = sum(r['actual'] for r in results)
    console.print(f"\n[bold]Total Budget:[/bold] ${total_budget:,.2f}  |  "
                  f"[bold]Total Spent:[/bold] ${total_actual:,.2f}  |  "
                  f"[bold]Remaining:[/bold] ${total_budget - total_actual:,.2f}")


@cli.command()
@click.option('--name', '-n', required=True, help='Goal name')
@click.option('--target', '-t', required=True, type=float, help='Target amount')
@click.option('--current', '-c', default=0.0, type=float, help='Current saved amount')
@click.option('--monthly', '-m', default=0.0, type=float, help='Monthly contribution')
def savings(name, target, current, monthly):
    """Track savings goal progress."""
    goal = SavingsGoal(name=name, target_amount=target, current_amount=current, monthly_contribution=monthly)
    progress = goal.track_progress()
    est = goal.estimate_completion()

    console.print(Panel(
        f"[bold]{progress['name']}[/bold]\n\n"
        f"🎯 Target:    ${progress['target']:,.2f}\n"
        f"💵 Current:   ${progress['current']:,.2f}\n"
        f"📉 Remaining: ${progress['remaining']:,.2f}\n"
        f"📊 Progress:  {progress['percent_complete']}%\n"
        f"📅 Est. Date: {est or 'N/A (set monthly contribution)'}",
        title="🐷 Savings Goal",
        border_style="magenta",
    ))

    # Visual progress bar
    pct = int(progress['percent_complete'])
    bar = "█" * (pct // 2) + "░" * (50 - pct // 2)
    console.print(f"\n  [{bar}] {pct}%")


@cli.command()
@click.option('--file', '-f', 'file_path', required=True, type=click.Path(exists=True), help='Expenses CSV file')
def recurring(file_path):
    """Detect recurring monthly expenses."""
    expenses = load_expenses(file_path)
    results = detect_recurring(expenses)

    if not results:
        console.print("[yellow]No recurring expenses detected.[/yellow]")
        return

    table = Table(title="🔄 Recurring Expenses", show_lines=True)
    table.add_column("Description", style="cyan", min_width=25)
    table.add_column("Avg Amount", style="green", justify="right", min_width=12)
    table.add_column("Occurrences", style="yellow", justify="center", min_width=12)
    table.add_column("Months", style="dim", min_width=20)

    for r in results:
        table.add_row(
            r['description'],
            f"${r['avg_amount']:,.2f}",
            str(r['occurrences']),
            ", ".join(r['months']),
        )

    console.print(table)
    total_recurring = sum(r['avg_amount'] for r in results)
    console.print(f"\n[bold]Estimated monthly recurring total:[/bold] ${total_recurring:,.2f}")


@cli.command()
@click.option('--file', '-f', 'file_path', required=True, type=click.Path(exists=True), help='Expenses CSV file')
@click.option('--top', '-n', default=10, type=int, help='Number of top expenses')
def trends(file_path, top):
    """Show monthly spending trends and top expenses."""
    expenses = load_expenses(file_path)

    # Monthly trends
    monthly = compute_monthly_trends(expenses)
    if monthly:
        table = Table(title="📈 Monthly Spending Trends", show_lines=True)
        table.add_column("Month", style="cyan", min_width=10)
        table.add_column("Total", style="green", justify="right", min_width=12)
        table.add_column("Trend", min_width=30)

        values = list(monthly.values())
        max_val = max(values) if values else 1
        prev = None
        for month_key, amount in monthly.items():
            bar_len = int((amount / max_val) * 25) if max_val else 0
            bar = "█" * bar_len
            arrow = ""
            if prev is not None:
                diff = amount - prev
                arrow = f" [green]▲ +${diff:,.0f}[/green]" if diff > 0 else f" [red]▼ -${abs(diff):,.0f}[/red]" if diff < 0 else " ━"
            prev = amount
            table.add_row(month_key, f"${amount:,.2f}", f"{bar}{arrow}")
        console.print(table)

    # Top expenses
    top_expenses = get_top_expenses(expenses, n=top)
    if top_expenses:
        table2 = Table(title=f"💸 Top {top} Expenses", show_lines=True)
        table2.add_column("#", style="dim", min_width=3)
        table2.add_column("Date", style="dim", min_width=12)
        table2.add_column("Description", style="white", min_width=25)
        table2.add_column("Category", style="cyan", min_width=15)
        table2.add_column("Amount", style="red", justify="right", min_width=12)

        for i, exp in enumerate(top_expenses, 1):
            table2.add_row(str(i), exp['date'], exp['description'], exp['category'], f"${exp['amount']:,.2f}")
        console.print(table2)


def main():
    """Entry point."""
    cli()


if __name__ == '__main__':
    main()
