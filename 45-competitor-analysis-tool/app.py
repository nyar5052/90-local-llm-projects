#!/usr/bin/env python3
"""
Competitor Analysis Tool - Generate SWOT analysis and competitive comparisons.

Takes competitor information and generates comprehensive SWOT analysis,
feature comparisons, and market positioning insights using a local Gemma 4 LLM.
"""

import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown
from rich.columns import Columns

from common.llm_client import chat, check_ollama_running

console = Console()


def generate_swot(company: str, competitors: list[str], industry: str) -> dict:
    """Generate SWOT analysis for the company vs competitors."""
    system_prompt = (
        "You are a strategic business analyst. Generate a comprehensive SWOT analysis. "
        "Respond ONLY with valid JSON in this exact format:\n"
        '{"strengths": ["s1", "s2", "s3"], "weaknesses": ["w1", "w2", "w3"], '
        '"opportunities": ["o1", "o2", "o3"], "threats": ["t1", "t2", "t3"]}'
    )

    competitors_text = ", ".join(competitors)
    messages = [{"role": "user", "content": (
        f"Company: {company}\n"
        f"Competitors: {competitors_text}\n"
        f"Industry: {industry}\n\n"
        "Generate a detailed SWOT analysis for the company considering the competitive landscape."
    )}]

    response = chat(messages, system_prompt=system_prompt, temperature=0.4)

    try:
        start = response.find("{")
        end = response.rfind("}") + 1
        if start >= 0 and end > start:
            return json.loads(response[start:end])
    except (json.JSONDecodeError, ValueError):
        pass

    return {
        "strengths": ["Analysis unavailable"],
        "weaknesses": ["Analysis unavailable"],
        "opportunities": ["Analysis unavailable"],
        "threats": ["Analysis unavailable"],
    }


def generate_comparison(company: str, competitors: list[str], industry: str) -> str:
    """Generate a competitive comparison analysis."""
    system_prompt = (
        "You are a market research analyst. Create a detailed competitive comparison "
        "report. Use markdown formatting with tables where appropriate. "
        "Compare features, pricing strategy, market position, and differentiation."
    )

    competitors_text = ", ".join(competitors)
    messages = [{"role": "user", "content": (
        f"Compare {company} against these competitors in the {industry} industry: "
        f"{competitors_text}\n\n"
        "Provide analysis on:\n"
        "1. Feature Comparison\n"
        "2. Pricing & Value Proposition\n"
        "3. Market Position & Share\n"
        "4. Key Differentiators\n"
        "5. Strategic Recommendations"
    )}]

    return chat(messages, system_prompt=system_prompt, temperature=0.5, max_tokens=4000)


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


def generate_recommendations(company: str, competitors: list[str], industry: str, swot: dict) -> str:
    """Generate strategic recommendations based on the analysis."""
    system_prompt = (
        "You are a strategic business consultant. Based on the SWOT analysis provided, "
        "generate actionable strategic recommendations. Use markdown formatting."
    )

    swot_text = json.dumps(swot, indent=2)
    competitors_text = ", ".join(competitors)
    messages = [{"role": "user", "content": (
        f"Company: {company}\n"
        f"Competitors: {competitors_text}\n"
        f"Industry: {industry}\n\n"
        f"SWOT Analysis:\n{swot_text}\n\n"
        "Generate top 5 strategic recommendations with rationale and priority level."
    )}]

    return chat(messages, system_prompt=system_prompt, temperature=0.5, max_tokens=3000)


@click.command()
@click.option("--company", "-c", required=True, help="Your company/product name.")
@click.option("--competitors", "-comp", required=True, help="Comma-separated competitor names.")
@click.option("--industry", "-i", required=True, help="Industry sector.")
@click.option("--full-report/--swot-only", default=True, help="Generate full report or SWOT only.")
def main(company: str, competitors: str, industry: str, full_report: bool) -> None:
    """Competitor Analysis Tool - SWOT analysis and competitive comparison."""
    competitor_list = [c.strip() for c in competitors.split(",") if c.strip()]

    console.print(Panel("🏢 [bold blue]Competitor Analysis Tool[/bold blue]", expand=False))
    console.print(f"[bold]Company:[/bold] {company}")
    console.print(f"[bold]Competitors:[/bold] {', '.join(competitor_list)}")
    console.print(f"[bold]Industry:[/bold] {industry}\n")

    if not check_ollama_running():
        console.print("[red]Error:[/red] Ollama is not running. Start it with: ollama serve")
        sys.exit(1)

    if not competitor_list:
        console.print("[red]Error:[/red] At least one competitor is required.")
        sys.exit(1)

    with console.status("[bold green]Generating SWOT analysis..."):
        swot = generate_swot(company, competitor_list, industry)

    display_swot(swot, company)

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
