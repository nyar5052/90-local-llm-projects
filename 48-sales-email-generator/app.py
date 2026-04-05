#!/usr/bin/env python3
"""
Sales Email Generator - Generate personalized sales outreach emails.

Takes prospect information and product details to generate professional,
personalized sales emails using a local Gemma 4 LLM.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import click
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt

from common.llm_client import chat, check_ollama_running

console = Console()

TONE_DESCRIPTIONS = {
    "professional": "Formal, business-appropriate, respectful",
    "casual": "Friendly, conversational, approachable",
    "persuasive": "Compelling, benefit-focused, action-oriented",
    "consultative": "Advisory, problem-solving, thought-leadership",
}


def generate_email(
    prospect: str,
    product: str,
    tone: str,
    context: str = "",
    follow_up: bool = False,
) -> dict:
    """Generate a personalized sales email."""
    tone_desc = TONE_DESCRIPTIONS.get(tone, TONE_DESCRIPTIONS["professional"])

    system_prompt = (
        f"You are an expert sales copywriter. Write a {tone} sales email. "
        f"Tone guidelines: {tone_desc}. "
        "The email should be concise (150-250 words), personalized, and include "
        "a clear call to action. "
        "Return the email with a subject line, greeting, body, and sign-off. "
        "Format: Start with 'Subject: ...' on the first line."
    )

    email_type = "follow-up" if follow_up else "initial outreach"
    context_text = f"\nAdditional context: {context}" if context else ""

    messages = [{"role": "user", "content": (
        f"Write a {email_type} sales email.\n\n"
        f"Prospect: {prospect}\n"
        f"Product/Service: {product}\n"
        f"Tone: {tone}{context_text}\n\n"
        "Make it personalized based on the prospect's role and company. "
        "Include a specific value proposition relevant to their situation."
    )}]

    response = chat(messages, system_prompt=system_prompt, temperature=0.7, max_tokens=2000)

    # Parse subject line from response
    lines = response.strip().split("\n")
    subject = ""
    body_start = 0
    for i, line in enumerate(lines):
        if line.lower().startswith("subject:"):
            subject = line.split(":", 1)[1].strip()
            body_start = i + 1
            break

    body = "\n".join(lines[body_start:]).strip()

    return {"subject": subject or "Follow Up", "body": body or response}


def generate_variants(prospect: str, product: str, tone: str, count: int = 3) -> list[dict]:
    """Generate multiple email variants for A/B testing."""
    variants = []
    for i in range(count):
        system_prompt = (
            f"You are a sales copywriter. Write variant #{i+1} of a sales email. "
            f"Each variant should use a different angle/hook but same {tone} tone. "
            "Start with 'Subject: ...' on the first line. Keep it 100-200 words."
        )

        messages = [{"role": "user", "content": (
            f"Prospect: {prospect}\nProduct: {product}\n"
            f"Write a unique email variant #{i+1} with a different approach."
        )}]

        response = chat(messages, system_prompt=system_prompt, temperature=0.8)

        lines = response.strip().split("\n")
        subject = ""
        body_start = 0
        for j, line in enumerate(lines):
            if line.lower().startswith("subject:"):
                subject = line.split(":", 1)[1].strip()
                body_start = j + 1
                break

        body = "\n".join(lines[body_start:]).strip()
        variants.append({"subject": subject or f"Variant {i+1}", "body": body or response})

    return variants


def display_email(email: dict, title: str = "Generated Email") -> None:
    """Display an email in a formatted panel."""
    content = f"**Subject:** {email['subject']}\n\n---\n\n{email['body']}"
    console.print(Panel(Markdown(content), title=f"✉️ {title}", border_style="green"))


@click.command()
@click.option("--prospect", "-p", required=True, help="Prospect description (e.g., 'CTO at startup').")
@click.option("--product", "-pr", required=True, help="Product/service being offered.")
@click.option("--tone", "-t", type=click.Choice(["professional", "casual", "persuasive", "consultative"]),
              default="professional", help="Email tone.")
@click.option("--context", "-c", default="", help="Additional context about the prospect.")
@click.option("--follow-up", is_flag=True, help="Generate a follow-up email instead.")
@click.option("--variants", "-v", type=int, default=0, help="Generate N variants for A/B testing.")
def main(prospect: str, product: str, tone: str, context: str, follow_up: bool, variants: int) -> None:
    """Sales Email Generator - Create personalized sales outreach emails."""
    console.print(Panel("✉️ [bold blue]Sales Email Generator[/bold blue]", expand=False))

    if not check_ollama_running():
        console.print("[red]Error:[/red] Ollama is not running. Start it with: ollama serve")
        sys.exit(1)

    console.print(f"[bold]Prospect:[/bold] {prospect}")
    console.print(f"[bold]Product:[/bold] {product}")
    console.print(f"[bold]Tone:[/bold] {tone}")
    if context:
        console.print(f"[bold]Context:[/bold] {context}")
    if follow_up:
        console.print("[bold]Type:[/bold] Follow-up email")
    console.print()

    if variants > 0:
        with console.status(f"[bold green]Generating {variants} email variants..."):
            email_variants = generate_variants(prospect, product, tone, variants)

        for i, email in enumerate(email_variants, 1):
            display_email(email, title=f"Variant {i}")
            console.print()
    else:
        with console.status("[bold green]Generating email..."):
            email = generate_email(prospect, product, tone, context, follow_up)

        display_email(email)


if __name__ == "__main__":
    main()
