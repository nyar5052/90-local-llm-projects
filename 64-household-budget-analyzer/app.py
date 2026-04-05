#!/usr/bin/env python3
"""Household Budget Analyzer - Analyzes household expenses from CSV with AI insights."""

import sys
import os
import csv
import json
from datetime import datetime
from collections import defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from common.llm_client import chat, generate, check_ollama_running

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown

console = Console()


def load_expenses(file_path: str) -> list[dict]:
    """Load expenses from a CSV file."""
    if not os.path.exists(file_path):
        console.print(f"[red]Error:[/red] File '{file_path}' not found.")
        sys.exit(1)
    try:
        expenses = []
        with open(file_path, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                expenses.append(row)
        if not expenses:
            console.print("[yellow]Warning:[/yellow] No expenses found in file.")
        return expenses
    except Exception as e:
        console.print(f"[red]Error reading CSV:[/red] {e}")
        sys.exit(1)


def filter_by_month(expenses: list[dict], month_str: str) -> list[dict]:
    """Filter expenses by month string like 'March 2024'."""
    if not month_str:
        return expenses
    try:
        target = datetime.strptime(month_str, "%B %Y")
        filtered = []
        for exp in expenses:
            date_str = exp.get("date", exp.get("Date", ""))
            for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%Y/%m/%d"):
                try:
                    date = datetime.strptime(date_str, fmt)
                    if date.year == target.year and date.month == target.month:
                        filtered.append(exp)
                    break
                except ValueError:
                    continue
        return filtered
    except ValueError:
        console.print(f"[yellow]Warning:[/yellow] Could not parse month '{month_str}'. Showing all expenses.")
        return expenses


def compute_category_breakdown(expenses: list[dict]) -> dict:
    """Compute spending by category."""
    categories = defaultdict(float)
    for exp in expenses:
        category = exp.get("category", exp.get("Category", "Uncategorized"))
        amount_str = exp.get("amount", exp.get("Amount", "0"))
        try:
            amount = float(str(amount_str).replace("$", "").replace(",", ""))
        except ValueError:
            amount = 0.0
        categories[category] += amount
    return dict(sorted(categories.items(), key=lambda x: x[1], reverse=True))


def compute_total(expenses: list[dict]) -> float:
    """Compute total spending."""
    total = 0.0
    for exp in expenses:
        amount_str = exp.get("amount", exp.get("Amount", "0"))
        try:
            total += float(str(amount_str).replace("$", "").replace(",", ""))
        except ValueError:
            continue
    return total


def display_breakdown(categories: dict, total: float) -> None:
    """Display category breakdown in a table."""
    table = Table(title="💰 Expense Breakdown", show_lines=True)
    table.add_column("Category", style="cyan", min_width=18)
    table.add_column("Amount", style="green", justify="right", min_width=12)
    table.add_column("Percentage", style="yellow", justify="right", min_width=10)

    for category, amount in categories.items():
        pct = (amount / total * 100) if total > 0 else 0
        bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
        table.add_row(category, f"${amount:,.2f}", f"{pct:.1f}% {bar}")

    table.add_row("[bold]TOTAL[/bold]", f"[bold]${total:,.2f}[/bold]", "100%", style="bold")
    console.print(table)


def analyze_budget(expenses: list[dict], categories: dict, total: float, month: str) -> str:
    """Use AI to analyze budget and provide savings suggestions."""
    expense_summary = json.dumps({
        "total": total,
        "categories": categories,
        "num_transactions": len(expenses),
        "period": month or "all time",
    }, indent=2)

    prompt = f"""Analyze this household budget:

{expense_summary}

Please provide:
1. **Spending Analysis**: Overall assessment of spending patterns
2. **Top Expense Areas**: Where most money is going and if amounts seem reasonable
3. **Savings Opportunities**: Specific, actionable suggestions to reduce spending
4. **Budget Recommendations**: Suggested budget percentages per category
5. **Trend Insights**: Observations about spending habits
6. **Monthly Savings Goal**: Realistic savings target based on the data

Be specific with dollar amounts and percentages."""

    return generate(
        prompt=prompt,
        system_prompt="You are an expert financial advisor specializing in household budgets. Provide practical, actionable advice.",
        temperature=0.5,
    )


def compare_months(expenses: list[dict]) -> str:
    """Compare spending across months."""
    monthly = defaultdict(float)
    for exp in expenses:
        date_str = exp.get("date", exp.get("Date", ""))
        for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y"):
            try:
                date = datetime.strptime(date_str, fmt)
                key = date.strftime("%B %Y")
                amount_str = exp.get("amount", exp.get("Amount", "0"))
                monthly[key] += float(str(amount_str).replace("$", "").replace(",", ""))
                break
            except ValueError:
                continue

    if not monthly:
        return "No monthly data available for comparison."

    prompt = f"""Compare monthly spending trends:

{json.dumps(dict(monthly), indent=2)}

Provide:
1. **Month-over-Month Change**: How spending changed
2. **Highest/Lowest Months**: Peak and trough spending
3. **Trend Direction**: Is spending increasing or decreasing?
4. **Recommendations**: How to maintain budget discipline"""

    return generate(
        prompt=prompt,
        system_prompt="You are a household budget trend analyst.",
        temperature=0.5,
    )


@click.command()
@click.option('--file', '-f', 'file_path', required=True, type=click.Path(), help='Path to expenses CSV file')
@click.option('--month', '-m', default=None, help='Filter by month (e.g., "March 2024")')
@click.option('--analyze', '-a', is_flag=True, help='Get AI budget analysis')
@click.option('--compare', '-c', is_flag=True, help='Compare spending across months')
@click.option('--breakdown', '-b', is_flag=True, help='Show category breakdown only')
def main(file_path, month, analyze, compare, breakdown):
    """Household Budget Analyzer - AI-powered expense analysis."""
    console.print(Panel(
        "[bold blue]💰 Household Budget Analyzer[/bold blue]\n"
        "[dim]AI-powered expense analysis and savings suggestions[/dim]",
        border_style="blue",
    ))

    expenses = load_expenses(file_path)

    if month:
        expenses = filter_by_month(expenses, month)
        if not expenses:
            console.print(f"[yellow]No expenses found for {month}[/yellow]")
            return
        console.print(f"[dim]Showing expenses for: {month}[/dim]\n")

    categories = compute_category_breakdown(expenses)
    total = compute_total(expenses)

    display_breakdown(categories, total)
    console.print(f"\n[dim]Transactions: {len(expenses)} | Period: {month or 'All time'}[/dim]\n")

    if analyze or (not compare and not breakdown):
        if not check_ollama_running():
            console.print("[red]Error:[/red] Ollama is not running. Start it with: [bold]ollama serve[/bold]")
            sys.exit(1)

        with console.status("[bold green]Analyzing your budget..."):
            result = analyze_budget(expenses, categories, total, month)
        console.print(Panel(Markdown(result), title="📊 Budget Analysis", border_style="green"))

    if compare:
        if not check_ollama_running():
            console.print("[red]Error:[/red] Ollama is not running.")
            sys.exit(1)

        with console.status("[bold green]Comparing monthly trends..."):
            result = compare_months(load_expenses(file_path))
        console.print(Panel(Markdown(result), title="📈 Monthly Comparison", border_style="cyan"))


if __name__ == '__main__':
    main()
