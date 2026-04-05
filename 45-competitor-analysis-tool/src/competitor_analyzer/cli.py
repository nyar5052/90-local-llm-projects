"""CLI interface for Competitor Analysis Tool."""

import sys
import json
import logging

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown
from rich.columns import Columns

from .core import (
    load_config,
    generate_swot,
    generate_feature_matrix,
    generate_pricing_comparison,
    generate_market_positioning,
    generate_comparison,
    generate_action_items,
    generate_recommendations,
    get_llm_client,
)

console = Console()
logger = logging.getLogger(__name__)


def setup_logging(verbose: bool = False):
    """Configure logging based on verbosity."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def display_swot(swot: dict, company: str) -> None:
    """Display the SWOT analysis in a formatted grid."""
    def make_panel(title: str, items: list, color: str, emoji: str) -> Panel:
        content = "\n".join(f"• {item}" for item in items)
        return Panel(content, title=f"{emoji} {title}", border_style=color, width=45)

    strengths_panel = make_panel("Strengths", swot.get("strengths", []), "green", "💪")
    weaknesses_panel = make_panel("Weaknesses", swot.get("weaknesses", []), "red", "⚠️")
    opportunities_panel = make_panel("Opportunities", swot.get("opportunities", []), "blue", "🎯")
    threats_panel = make_panel("Threats", swot.get("threats", []), "yellow", "🔥")

    console.print(f"\n[bold]SWOT Analysis for [cyan]{company}[/cyan][/bold]\n")
    console.print(Columns([strengths_panel, weaknesses_panel], equal=True))
    console.print(Columns([opportunities_panel, threats_panel], equal=True))


def display_feature_matrix(features: dict) -> None:
    """Display feature comparison matrix."""
    if not features.get("features") or not features.get("matrix"):
        return
    table = Table(title="📋 Feature Comparison Matrix", show_lines=True)
    table.add_column("Feature", style="cyan bold")

    companies = list(features["matrix"].keys())
    for company in companies:
        table.add_column(company, justify="center")

    for feat in features["features"]:
        row = [feat]
        for company in companies:
            val = features["matrix"].get(company, {}).get(feat, "N/A")
            emoji = {"yes": "✅", "no": "❌", "partial": "🔶"}.get(str(val).lower(), val)
            row.append(str(emoji))
        table.add_row(*row)

    console.print(table)
    if features.get("summary"):
        console.print(f"\n[dim]{features['summary']}[/dim]")


def display_pricing(pricing: dict) -> None:
    """Display pricing comparison."""
    if not pricing.get("companies"):
        return
    table = Table(title="💰 Pricing Comparison", show_lines=True)
    table.add_column("Company", style="cyan bold")
    table.add_column("Model")
    table.add_column("Price Range", justify="center")
    table.add_column("Tier", justify="center")
    table.add_column("Value Proposition", max_width=35, overflow="fold")

    tier_colors = {"budget": "green", "mid-range": "yellow", "premium": "red"}

    for c in pricing["companies"]:
        tier = c.get("tier", "mid-range")
        color = tier_colors.get(tier, "white")
        table.add_row(
            c.get("name", "N/A"),
            c.get("pricing_model", "N/A"),
            c.get("price_range", "N/A"),
            f"[{color}]{tier.title()}[/{color}]",
            c.get("value_proposition", "N/A")[:80],
        )
    console.print(table)

    if pricing.get("recommendation"):
        console.print(f"\n💡 [bold]Recommendation:[/bold] {pricing['recommendation']}")


def display_action_items(items: list) -> None:
    """Display prioritized action items."""
    if not items:
        return
    table = Table(title="🎯 Action Items", show_lines=True)
    table.add_column("#", style="dim", width=4)
    table.add_column("Title", style="cyan bold", min_width=20)
    table.add_column("Priority", justify="center", width=10)
    table.add_column("Timeline", justify="center", width=12)
    table.add_column("Category", justify="center", width=12)
    table.add_column("Outcome", max_width=35, overflow="fold")

    priority_colors = {"critical": "red bold", "high": "red", "medium": "yellow", "low": "green"}

    for i, item in enumerate(items, 1):
        priority = item.get("priority", "medium")
        color = priority_colors.get(priority, "white")
        table.add_row(
            str(i),
            item.get("title", "N/A"),
            f"[{color}]{priority.upper()}[/{color}]",
            item.get("timeline", "N/A").title(),
            item.get("category", "N/A").title(),
            item.get("expected_outcome", "N/A")[:80],
        )
    console.print(table)


@click.command()
@click.option("--company", "-c", required=True, help="Your company/product name.")
@click.option("--competitors", "-comp", required=True, help="Comma-separated competitor names.")
@click.option("--industry", "-i", required=True, help="Industry sector.")
@click.option("--full-report/--swot-only", default=True, help="Generate full report or SWOT only.")
@click.option("--show-features/--no-features", default=True, help="Show feature matrix.")
@click.option("--show-pricing/--no-pricing", default=True, help="Show pricing comparison.")
@click.option("--show-actions/--no-actions", default=True, help="Show action items.")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging.")
def main(company: str, competitors: str, industry: str, full_report: bool,
         show_features: bool, show_pricing: bool, show_actions: bool, verbose: bool) -> None:
    """Competitor Analysis Tool - SWOT analysis and competitive comparison."""
    setup_logging(verbose)
    load_config()

    competitor_list = [c.strip() for c in competitors.split(",") if c.strip()]

    console.print(Panel("🏢 [bold blue]Competitor Analysis Tool[/bold blue]", expand=False))
    console.print(f"[bold]Company:[/bold] {company}")
    console.print(f"[bold]Competitors:[/bold] {', '.join(competitor_list)}")
    console.print(f"[bold]Industry:[/bold] {industry}\n")

    _, check_ollama_running = get_llm_client()
    if not check_ollama_running():
        console.print("[red]Error:[/red] Ollama is not running. Start it with: ollama serve")
        sys.exit(1)

    if not competitor_list:
        console.print("[red]Error:[/red] At least one competitor is required.")
        sys.exit(1)

    with console.status("[bold green]Generating SWOT analysis..."):
        swot = generate_swot(company, competitor_list, industry)

    display_swot(swot, company)

    if show_features:
        console.print()
        with console.status("[bold green]Generating feature matrix..."):
            features = generate_feature_matrix(company, competitor_list, industry)
        display_feature_matrix(features)

    if show_pricing:
        console.print()
        with console.status("[bold green]Generating pricing comparison..."):
            pricing = generate_pricing_comparison(company, competitor_list, industry)
        display_pricing(pricing)

    if show_actions:
        console.print()
        with console.status("[bold green]Generating action items..."):
            actions = generate_action_items(company, competitor_list, industry, swot)
        display_action_items(actions)

    if full_report:
        console.print()
        with console.status("[bold green]Generating competitive comparison..."):
            comparison = generate_comparison(company, competitor_list, industry)
        console.print(Panel(Markdown(comparison), title="📊 Competitive Comparison", border_style="blue"))

        console.print()
        with console.status("[bold green]Generating strategic recommendations..."):
            recs = generate_recommendations(company, competitor_list, industry, swot)
        console.print(Panel(Markdown(recs), title="🎯 Strategic Recommendations", border_style="green"))


if __name__ == "__main__":
    main()
