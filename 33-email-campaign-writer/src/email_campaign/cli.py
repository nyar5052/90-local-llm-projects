#!/usr/bin/env python3
"""CLI interface for Email Campaign Writer."""

import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))

import click
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from email_campaign.core import (
    CAMPAIGN_TYPES,
    build_email_sequence,
    calculate_sequence_timeline,
    estimate_campaign_metrics,
    extract_personalization_tokens,
    generate_campaign,
    generate_subject_variants,
    preview_html,
    render_email,
    setup_logging,
)
from common.llm_client import check_ollama_running  # noqa: E402

console = Console()


@click.command()
@click.option("--product", required=True, help="Product or service name.")
@click.option("--audience", required=True, help="Target audience description.")
@click.option("--emails", default=3, type=int, help="Number of emails in sequence (1-10).")
@click.option(
    "--type",
    "campaign_type",
    type=click.Choice(CAMPAIGN_TYPES, case_sensitive=False),
    default="promotional",
    help="Campaign type.",
)
@click.option("--output", "-o", default=None, help="Save output to file.")
@click.option("--subject-test", is_flag=True, default=False, help="Generate A/B subject line variants.")
@click.option("--html-preview", is_flag=True, default=False, help="Output HTML email preview.")
@click.option("--timeline", is_flag=True, default=False, help="Show campaign sequence timeline.")
@click.option("--personalize", default=None, help='JSON string of user data, e.g. \'{"first_name":"Jane"}\'.')
def main(
    product: str,
    audience: str,
    emails: int,
    campaign_type: str,
    output: str | None,
    subject_test: bool,
    html_preview: bool,
    timeline: bool,
    personalize: str | None,
) -> None:
    """Generate marketing email campaign sequences."""
    setup_logging()

    console.print(
        Panel.fit(
            "[bold yellow]📧 Email Campaign Writer[/bold yellow]",
            border_style="yellow",
        )
    )

    if not check_ollama_running():
        console.print("[red]Error: Ollama is not running. Start it with: ollama serve[/red]")
        sys.exit(1)

    emails = max(1, min(emails, 10))

    console.print(f"[cyan]Product:[/cyan]       {product}")
    console.print(f"[cyan]Audience:[/cyan]      {audience}")
    console.print(f"[cyan]Emails:[/cyan]        {emails}")
    console.print(f"[cyan]Campaign Type:[/cyan] {campaign_type}")
    console.print()

    # ---- Subject-line A/B testing ----
    if subject_test:
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as prog:
            prog.add_task("Generating subject line variants…", total=None)
            variants = generate_subject_variants(product, audience)

        table = Table(title="Subject Line A/B Variants", border_style="magenta")
        table.add_column("#", style="bold")
        table.add_column("Subject Line", style="cyan")
        for i, v in enumerate(variants, 1):
            table.add_row(str(i), v)
        console.print(table)
        console.print()

    # ---- Generate campaign ----
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as prog:
        prog.add_task(f"Generating {emails}-email campaign…", total=None)
        campaign = build_email_sequence(product, audience, emails, campaign_type)

    raw_body = campaign.emails[0].body if campaign.emails else ""

    # ---- Personalize ----
    if personalize:
        try:
            user_data = json.loads(personalize)
        except json.JSONDecodeError:
            console.print("[red]Error: --personalize must be valid JSON.[/red]")
            sys.exit(1)
        raw_body = render_email(campaign.emails[0], user_data) if campaign.emails else raw_body
        console.print("[green]✓ Personalization applied[/green]\n")

    # ---- Display campaign ----
    console.print(Panel(Markdown(raw_body), title="📧 Email Campaign", border_style="green"))

    # ---- Timeline ----
    if timeline:
        tl = calculate_sequence_timeline(campaign)
        tbl = Table(title="📅 Sequence Timeline", border_style="blue")
        tbl.add_column("Day", style="bold", justify="right")
        tbl.add_column("Email Subject", style="cyan")
        for day, subj in tl:
            tbl.add_row(str(day), subj)
        console.print(tbl)
        console.print()

        metrics = estimate_campaign_metrics(campaign)
        mtbl = Table(title="📊 Estimated Metrics", border_style="green")
        mtbl.add_column("Metric", style="bold")
        mtbl.add_column("Value", style="cyan", justify="right")
        mtbl.add_row("Campaign Type", metrics["campaign_type"])
        mtbl.add_row("Total Emails", str(metrics["num_emails"]))
        mtbl.add_row("Avg Open Rate", f"{metrics['avg_open_rate']:.1%}")
        mtbl.add_row("Avg Click Rate", f"{metrics['avg_click_rate']:.1%}")
        console.print(mtbl)
        console.print()

    # ---- HTML preview ----
    if html_preview:
        html = preview_html(raw_body)
        if output:
            html_path = output.rsplit(".", 1)[0] + ".html"
        else:
            html_path = "campaign_preview.html"
        with open(html_path, "w", encoding="utf-8") as fh:
            fh.write(html)
        console.print(f"[green]HTML preview saved to {html_path}[/green]")

    # ---- Save output ----
    if output:
        with open(output, "w", encoding="utf-8") as fh:
            fh.write(raw_body)
        console.print(f"[green]Campaign saved to {output}[/green]")


if __name__ == "__main__":
    main()
