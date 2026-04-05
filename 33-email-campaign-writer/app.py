#!/usr/bin/env python3
"""Email Campaign Writer - Generate marketing email sequences using a local LLM."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import click
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, TextColumn
from common.llm_client import chat, check_ollama_running

console = Console()

CAMPAIGN_TYPES = ["welcome", "promotional", "nurture", "re-engagement", "product-launch"]


def build_prompt(product: str, audience: str, num_emails: int, campaign_type: str) -> str:
    """Build the email campaign generation prompt."""
    return (
        f"Create a {num_emails}-email marketing campaign sequence for:\n\n"
        f"Product/Service: {product}\n"
        f"Target Audience: {audience}\n"
        f"Campaign Type: {campaign_type}\n\n"
        f"For EACH email in the sequence, provide:\n"
        f"1. **Email Number** and **Subject Line** (with 2 A/B variants)\n"
        f"2. **Preview Text** (the snippet shown in inbox)\n"
        f"3. **Body** (full email copy with personalization placeholders like {{{{first_name}}}})\n"
        f"4. **Call to Action** (button text and purpose)\n"
        f"5. **Send Timing** (suggested day/time relative to previous email)\n\n"
        f"Make each email build on the previous one to create a cohesive journey.\n"
        f"Use proven copywriting frameworks (AIDA, PAS, etc.).\n"
        f"Include compelling subject lines with high open-rate potential.\n"
    )


def generate_campaign(product: str, audience: str, num_emails: int, campaign_type: str) -> str:
    """Generate an email campaign using the LLM."""
    system_prompt = (
        "You are an expert email marketing copywriter with deep knowledge of "
        "conversion optimization, A/B testing, and customer journey mapping. "
        "You write compelling emails that drive engagement and conversions."
    )
    user_prompt = build_prompt(product, audience, num_emails, campaign_type)
    messages = [{"role": "user", "content": user_prompt}]
    return chat(messages, system_prompt=system_prompt, temperature=0.7, max_tokens=4096)


@click.command()
@click.option("--product", required=True, help="Product or service name.")
@click.option("--audience", required=True, help="Target audience description.")
@click.option("--emails", default=3, type=int, help="Number of emails in sequence.")
@click.option(
    "--type",
    "campaign_type",
    type=click.Choice(CAMPAIGN_TYPES, case_sensitive=False),
    default="promotional",
    help="Campaign type.",
)
@click.option("--output", "-o", default=None, help="Save output to file.")
def main(product: str, audience: str, emails: int, campaign_type: str, output: str):
    """Generate marketing email campaign sequences."""
    console.print(Panel.fit("[bold yellow]Email Campaign Writer[/bold yellow]", border_style="yellow"))

    if not check_ollama_running():
        console.print("[red]Error: Ollama is not running. Start it with: ollama serve[/red]")
        sys.exit(1)

    console.print(f"[cyan]Product:[/cyan] {product}")
    console.print(f"[cyan]Audience:[/cyan] {audience}")
    console.print(f"[cyan]Emails:[/cyan] {emails}")
    console.print(f"[cyan]Campaign Type:[/cyan] {campaign_type}")
    console.print()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        progress.add_task(f"Generating {emails}-email campaign...", total=None)
        result = generate_campaign(product, audience, emails, campaign_type)

    console.print(Panel(Markdown(result), title="Email Campaign", border_style="green"))

    if output:
        with open(output, "w", encoding="utf-8") as f:
            f.write(result)
        console.print(f"[green]Saved to {output}[/green]")


if __name__ == "__main__":
    main()
