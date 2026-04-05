"""
IT Helpdesk Bot - AI-powered IT support chatbot for common tech issues.

Provides troubleshooting guidance for hardware, software, network,
and security issues using a local Gemma 4 LLM via Ollama.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import click
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from rich.progress import Progress, SpinnerColumn, TextColumn
from common.llm_client import chat, check_ollama_running

console = Console()

SYSTEM_PROMPT = """You are an expert IT Helpdesk Support Agent. Your role is to:
1. Diagnose technical issues based on user descriptions
2. Provide step-by-step troubleshooting instructions
3. Suggest solutions for hardware, software, network, and security problems
4. Escalate complex issues by recommending the user contact senior support
5. Always be patient, clear, and professional

Guidelines:
- Ask clarifying questions when the issue is unclear
- Provide numbered steps for solutions
- Mention the operating system or platform when relevant
- Warn users before suggesting actions that could cause data loss
- If you're unsure, say so and recommend professional help"""

CATEGORIES = {
    "1": ("🖥️ Hardware Issues", "computer hardware, peripherals, monitors, keyboards"),
    "2": ("💾 Software Issues", "application errors, installations, updates, crashes"),
    "3": ("🌐 Network Issues", "WiFi, ethernet, VPN, internet connectivity"),
    "4": ("🔒 Security Issues", "passwords, malware, phishing, account access"),
    "5": ("📧 Email Issues", "email setup, sending/receiving problems, spam"),
    "6": ("🖨️ Printer Issues", "printer setup, print jobs, drivers"),
    "7": ("💬 General Question", "any other IT-related question"),
}


def display_categories():
    """Display available support categories."""
    lines = []
    for key, (name, desc) in CATEGORIES.items():
        lines.append(f"  [bold]{key}[/bold]. {name} — [dim]{desc}[/dim]")
    console.print(
        Panel(
            "\n".join(lines),
            title="[bold cyan]Support Categories[/bold cyan]",
            border_style="cyan",
        )
    )


def get_response(user_message: str, history: list[dict]) -> str:
    """Get a response from the IT helpdesk bot."""
    messages = history + [{"role": "user", "content": user_message}]
    return chat(messages, system_prompt=SYSTEM_PROMPT)


@click.command()
@click.option("--category", type=click.Choice([str(i) for i in range(1, 8)]), help="Issue category (1-7)")
def main(category: str | None):
    """IT Helpdesk Bot - Your AI-powered IT support assistant."""
    console.print(
        Panel.fit(
            "[bold cyan]🖥️ IT Helpdesk Bot[/bold cyan]\n"
            "Your AI-powered IT support assistant",
            border_style="cyan",
        )
    )

    if not check_ollama_running():
        console.print("[red]❌ Ollama is not running. Start it with: ollama serve[/red]")
        sys.exit(1)

    console.print("[green]✅ Connected to Ollama[/green]\n")

    history: list[dict] = []

    if not category:
        display_categories()
        category = Prompt.ask(
            "[bold yellow]Select a category[/bold yellow]",
            choices=[str(i) for i in range(1, 8)],
            default="7",
        )

    cat_name, cat_desc = CATEGORIES[category]
    console.print(f"\n[bold]Selected: {cat_name}[/bold]")
    console.print("[dim]Type 'quit' to exit, 'new' for a new issue.[/dim]\n")

    # Prime the conversation with category context
    history.append({
        "role": "user",
        "content": f"I need help with a {cat_desc} issue.",
    })
    history.append({
        "role": "assistant",
        "content": f"I'd be happy to help with your {cat_desc.split(',')[0]} issue. "
                   "Could you please describe the problem in detail? "
                   "Include any error messages, when it started, and what you've already tried.",
    })
    console.print(
        Panel(
            f"I'd be happy to help with your {cat_desc.split(',')[0]} issue. "
            "Could you please describe the problem in detail?\n"
            "Include any error messages, when it started, and what you've already tried.",
            title=f"[bold green]{cat_name} Support[/bold green]",
            border_style="green",
        )
    )

    while True:
        try:
            user_input = Prompt.ask("\n[bold yellow]You[/bold yellow]")
        except (KeyboardInterrupt, EOFError):
            break

        if user_input.lower().strip() in ("quit", "exit", "q"):
            break

        if user_input.lower().strip() == "new":
            history.clear()
            display_categories()
            category = Prompt.ask(
                "[bold yellow]Select a category[/bold yellow]",
                choices=[str(i) for i in range(1, 8)],
                default="7",
            )
            cat_name, cat_desc = CATEGORIES[category]
            console.print(f"\n[bold]Selected: {cat_name}[/bold]\n")
            continue

        if not user_input.strip():
            continue

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            progress.add_task("Diagnosing issue...", total=None)
            response = get_response(user_input, history)

        history.append({"role": "user", "content": user_input})
        history.append({"role": "assistant", "content": response})

        console.print()
        console.print(
            Panel(Markdown(response), title="[bold green]🤖 IT Support[/bold green]", border_style="green")
        )

    console.print("\n[bold cyan]👋 Thank you for contacting IT Support! Goodbye![/bold cyan]")


if __name__ == "__main__":
    main()
