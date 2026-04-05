"""Click CLI interface for Travel Itinerary Bot."""

import sys
import logging

import click
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from rich.progress import Progress, SpinnerColumn, TextColumn

from .config import load_config, setup_logging
from .core import (
    check_ollama_running,
    generate_itinerary,
    generate_multi_destination_itinerary,
    get_place_details,
    generate_budget_breakdown,
    generate_packing_list,
    BUDGETS,
)
from .utils import parse_destinations, save_itinerary

logger = logging.getLogger(__name__)
console = Console()


@click.command()
@click.option("--destination", required=True, help="Travel destination(s), comma-separated for multi-dest")
@click.option("--days", type=click.IntRange(1, 30), default=5, help="Number of days (per destination if multi)")
@click.option("--budget", type=click.Choice(BUDGETS, case_sensitive=False), default="moderate", help="Budget level")
@click.option("--interests", type=str, default=None, help="Interests (comma-separated)")
@click.option("--travelers", type=click.IntRange(1, 20), default=1, help="Number of travelers")
@click.option("--config", "config_path", default=None, type=click.Path(), help="Path to config.yaml")
def main(destination: str, days: int, budget: str, interests: str | None, travelers: int, config_path: str | None):
    """Travel Itinerary Bot - Plan your perfect vacation with AI."""
    cfg = load_config(config_path)
    setup_logging(cfg)
    model_cfg = cfg.get("model", {})
    storage_cfg = cfg.get("storage", {})

    console.print(Panel.fit("[bold cyan]✈️ Travel Itinerary Bot[/bold cyan]\nAI-powered vacation planning", border_style="cyan"))

    if not check_ollama_running():
        console.print("[red]❌ Ollama is not running. Start it with: ollama serve[/red]")
        sys.exit(1)

    destinations = parse_destinations(destination)
    is_multi = len(destinations) > 1

    console.print(f"[bold]Destination(s):[/bold] {' → '.join(destinations)}")
    console.print(f"[bold]Duration:[/bold] {days} days" + (" each" if is_multi else ""))
    console.print(f"[bold]Budget:[/bold] {budget.capitalize()}")
    console.print(f"[bold]Travelers:[/bold] {travelers}")
    if interests:
        console.print(f"[bold]Interests:[/bold] {interests}")
    console.print()

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as prog:
        prog.add_task(f"Planning your trip...", total=None)
        if is_multi:
            itinerary = generate_multi_destination_itinerary(
                destinations, days, budget, interests, travelers,
                model=model_cfg.get("name", "gemma4"), temperature=model_cfg.get("temperature", 0.7),
            )
        else:
            itinerary = generate_itinerary(
                destinations[0], days, budget, interests, travelers,
                model=model_cfg.get("name", "gemma4"), temperature=model_cfg.get("temperature", 0.7),
            )

    title_dest = " → ".join(destinations)
    console.print(Panel(Markdown(itinerary), title=f"[bold green]🗺️ {title_dest} — {days}-Day Itinerary[/bold green]", border_style="green"))

    save_itinerary(title_dest, days, budget, itinerary, storage_cfg.get("itineraries_file", "saved_itineraries.json"))

    console.print("\n[dim]Commands: place name → details | 'budget' | 'pack' | 'quit'[/dim]\n")

    while True:
        try:
            cmd = Prompt.ask("[bold yellow]📍 Command[/bold yellow]")
        except (KeyboardInterrupt, EOFError):
            break

        stripped = cmd.lower().strip()
        if stripped in ("quit", "exit", "q"):
            break
        if stripped == "budget":
            with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as prog:
                prog.add_task("Calculating budget...", total=None)
                bd = generate_budget_breakdown(itinerary, budget, travelers, model=model_cfg.get("name", "gemma4"))
            console.print(Panel(Markdown(bd), title="[bold green]💰 Budget Breakdown[/bold green]", border_style="green"))
            continue
        if stripped == "pack":
            with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as prog:
                prog.add_task("Creating packing list...", total=None)
                pl = generate_packing_list(title_dest, days, interests, model=model_cfg.get("name", "gemma4"))
            console.print(Panel(Markdown(pl), title="[bold green]🎒 Packing List[/bold green]", border_style="green"))
            continue
        if not cmd.strip():
            continue

        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as prog:
            prog.add_task(f"Looking up {cmd}...", total=None)
            details = get_place_details(cmd, destinations[0], model=model_cfg.get("name", "gemma4"))

        console.print()
        console.print(Panel(Markdown(details), title=f"[bold green]📍 {cmd}[/bold green]", border_style="green"))
        console.print()

    console.print("[bold cyan]✈️ Have a wonderful trip! Bon voyage![/bold cyan]")


if __name__ == "__main__":
    main()
