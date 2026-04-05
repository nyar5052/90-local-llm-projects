"""Click CLI interface for IT Helpdesk Bot."""

import sys
import logging

import click
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from rich.progress import Progress, SpinnerColumn, TextColumn

from .config import load_config, setup_logging
from .core import check_ollama_running, get_response, CATEGORIES
from .utils import save_ticket, load_tickets, search_knowledge_base, get_solution_template

logger = logging.getLogger(__name__)
console = Console()


def display_categories():
    lines = []
    for key, (name, desc) in CATEGORIES.items():
        lines.append(f"  [bold]{key}[/bold]. {name} — [dim]{desc}[/dim]")
    console.print(Panel("\n".join(lines), title="[bold cyan]Support Categories[/bold cyan]", border_style="cyan"))


@click.command()
@click.option("--category", type=click.Choice([str(i) for i in range(1, 8)]), help="Issue category (1-7)")
@click.option("--config", "config_path", default=None, type=click.Path(), help="Path to config.yaml")
def main(category: str | None, config_path: str | None):
    """IT Helpdesk Bot - Your AI-powered IT support assistant."""
    cfg = load_config(config_path)
    setup_logging(cfg)
    model_cfg = cfg.get("model", {})
    ticket_cfg = cfg.get("tickets", {})

    console.print(
        Panel.fit("[bold cyan]🖥️ IT Helpdesk Bot[/bold cyan]\nYour AI-powered IT support assistant", border_style="cyan")
    )

    if not check_ollama_running():
        console.print("[red]❌ Ollama is not running. Start it with: ollama serve[/red]")
        sys.exit(1)

    console.print("[green]✅ Connected to Ollama[/green]\n")

    history: list[dict] = []

    if not category:
        display_categories()
        category = Prompt.ask("[bold yellow]Select a category[/bold yellow]", choices=[str(i) for i in range(1, 8)], default="7")

    cat_name, cat_desc = CATEGORIES[category]
    console.print(f"\n[bold]Selected: {cat_name}[/bold]")
    console.print("[dim]Commands: 'quit' | 'new' | 'ticket' | 'kb <query>' | 'history'[/dim]\n")

    history.append({"role": "user", "content": f"I need help with a {cat_desc} issue."})
    intro = (f"I'd be happy to help with your {cat_desc.split(',')[0]} issue. "
             "Could you please describe the problem in detail? "
             "Include any error messages, when it started, and what you've already tried.")
    history.append({"role": "assistant", "content": intro})
    console.print(Panel(intro, title=f"[bold green]{cat_name} Support[/bold green]", border_style="green"))

    while True:
        try:
            user_input = Prompt.ask("\n[bold yellow]You[/bold yellow]")
        except (KeyboardInterrupt, EOFError):
            break

        cmd = user_input.lower().strip()
        if cmd in ("quit", "exit", "q"):
            break
        if cmd == "new":
            history.clear()
            display_categories()
            category = Prompt.ask("[bold yellow]Select a category[/bold yellow]", choices=[str(i) for i in range(1, 8)], default="7")
            cat_name, cat_desc = CATEGORIES[category]
            console.print(f"\n[bold]Selected: {cat_name}[/bold]\n")
            continue
        if cmd == "ticket":
            desc = Prompt.ask("[bold yellow]Ticket description[/bold yellow]")
            ticket = save_ticket(cat_name, desc, storage_file=ticket_cfg.get("storage_file", "tickets.json"))
            console.print(f"[green]✅ Ticket {ticket['id']} created.[/green]")
            continue
        if cmd.startswith("kb "):
            query = cmd[3:].strip()
            results = search_knowledge_base(query)
            if results:
                for r in results:
                    console.print(Panel(Markdown(r["solution"]), title=f"[bold blue]📖 {r['topic']}[/bold blue]", border_style="blue"))
            else:
                console.print("[yellow]No knowledge-base matches found.[/yellow]")
            continue
        if cmd == "history":
            tickets = load_tickets(ticket_cfg.get("storage_file", "tickets.json"))
            if tickets:
                for t in tickets[-10:]:
                    console.print(f"  [{t['status'].upper()}] {t['id']} — {t['category']} — {t['description'][:60]}")
            else:
                console.print("[dim]No tickets yet.[/dim]")
            continue
        if not user_input.strip():
            continue

        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as prog:
            prog.add_task("Diagnosing issue...", total=None)
            response = get_response(user_input, history, model=model_cfg.get("name", "gemma4"), temperature=model_cfg.get("temperature", 0.7))

        history.append({"role": "user", "content": user_input})
        history.append({"role": "assistant", "content": response})

        console.print()
        console.print(Panel(Markdown(response), title="[bold green]🤖 IT Support[/bold green]", border_style="green"))

    console.print("\n[bold cyan]👋 Thank you for contacting IT Support! Goodbye![/bold cyan]")


if __name__ == "__main__":
    main()
