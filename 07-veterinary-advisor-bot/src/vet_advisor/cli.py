"""Click CLI interface for Veterinary Advisor Bot."""

import sys
import logging

import click
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

from .core import (
    format_pet_context, get_response, check_symptoms, get_breed_advice,
    get_nutrition_advice, add_pet_profile, get_pet_profile, load_pet_profiles,
    record_symptom, get_symptom_history_for_pet, check_ollama_running,
    PET_TYPES, MEDICAL_DISCLAIMER,
)
from .utils import setup_logging

logger = logging.getLogger(__name__)
console = Console()


def setup_pet_profile_interactive() -> dict:
    """Interactively set up a pet profile."""
    console.print(Panel("[bold]Let's set up your pet's profile:[/bold]",
                        title="[bold cyan]🐾 Pet Profile[/bold cyan]", border_style="cyan"))
    pet_type = Prompt.ask("[bold]Pet type[/bold]", choices=PET_TYPES, default="dog")
    name = Prompt.ask("[bold]Pet's name[/bold]", default="Buddy")
    breed = Prompt.ask("[bold]Breed[/bold] (or 'mixed'/'unknown')", default="unknown")
    age = Prompt.ask("[bold]Age[/bold] (e.g., '3 years', '6 months')", default="unknown")
    weight = Prompt.ask("[bold]Weight[/bold] (e.g., '25 lbs', '5 kg')", default="unknown")

    return {"type": pet_type, "name": name, "breed": breed, "age": age, "weight": weight}


@click.group()
@click.option("--log-level", default="WARNING", help="Logging level")
def cli(log_level: str):
    """🐾 Veterinary Advisor Bot - AI-powered pet health guidance."""
    setup_logging(log_level)


@cli.command()
@click.option("--pet-type", type=click.Choice(PET_TYPES, case_sensitive=False), default=None, help="Type of pet")
@click.option("--name", default=None, help="Pet's name")
@click.option("--breed", default=None, help="Pet's breed")
def chat_cmd(pet_type: str | None, name: str | None, breed: str | None):
    """Start an interactive chat about your pet's health."""
    console.print(Panel.fit("[bold cyan]🐾 Veterinary Advisor Bot[/bold cyan]\nAI-powered pet health guidance",
                            border_style="cyan"))

    if not check_ollama_running():
        console.print("[red]❌ Ollama is not running. Start it with: ollama serve[/red]")
        sys.exit(1)

    console.print()
    console.print(Panel(MEDICAL_DISCLAIMER, border_style="yellow"))
    console.print()

    if pet_type and name:
        pet_profile = {"type": pet_type, "name": name, "breed": breed or "unknown",
                       "age": "unknown", "weight": "unknown"}
    else:
        saved = load_pet_profiles()
        if saved:
            console.print("[bold]Saved pets:[/bold]")
            for p in saved:
                console.print(f"  • {p['name']} ({p['type']})")
            choice = Prompt.ask("[bold]Load a pet or type 'new'[/bold]", default="new")
            if choice.lower() != "new":
                pet_profile = get_pet_profile(choice)
                if not pet_profile:
                    console.print("[yellow]Pet not found, creating new profile.[/yellow]")
                    pet_profile = setup_pet_profile_interactive()
            else:
                pet_profile = setup_pet_profile_interactive()
        else:
            pet_profile = setup_pet_profile_interactive()

    save_choice = Prompt.ask("[bold]Save this profile?[/bold]", choices=["y", "n"], default="y")
    if save_choice == "y":
        add_pet_profile(pet_profile["name"], pet_profile["type"],
                        pet_profile.get("breed", "unknown"), pet_profile.get("age", "unknown"),
                        pet_profile.get("weight", "unknown"))

    console.print()
    console.print(Panel(format_pet_context(pet_profile),
                        title=f"[bold green]🐾 {pet_profile['name']}'s Profile[/bold green]", border_style="green"))
    console.print(
        "\n[bold]Commands:[/bold]\n"
        "  [cyan]/symptoms <description>[/cyan] — Analyze symptoms\n"
        "  [cyan]/breed[/cyan] — Get breed-specific advice\n"
        "  [cyan]/nutrition[/cyan] — Get nutrition advice\n"
        "  [cyan]/history[/cyan] — View symptom history\n"
        "  [cyan]quit[/cyan] — Exit\n"
        "  [dim]Or just describe your concern in natural language.[/dim]\n"
    )

    history: list[dict] = []

    while True:
        try:
            user_input = Prompt.ask(f"\n[bold yellow]🐾 About {pet_profile['name']}[/bold yellow]")
        except (KeyboardInterrupt, EOFError):
            break

        if user_input.lower().strip() in ("quit", "exit", "q"):
            break
        if not user_input.strip():
            continue

        if user_input.startswith("/symptoms "):
            symptoms = user_input[10:].strip()
            with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
                progress.add_task("Analyzing symptoms...", total=None)
                response = check_symptoms(symptoms, pet_profile)
            record_symptom(pet_profile["name"], symptoms)
        elif user_input.strip() == "/breed":
            with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
                progress.add_task("Getting breed advice...", total=None)
                response = get_breed_advice(pet_profile["type"], pet_profile.get("breed", "unknown"))
        elif user_input.strip() == "/nutrition":
            with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
                progress.add_task("Getting nutrition advice...", total=None)
                response = get_nutrition_advice(pet_profile)
        elif user_input.strip() == "/history":
            hist = get_symptom_history_for_pet(pet_profile["name"])
            if not hist:
                console.print("[yellow]No symptom history recorded.[/yellow]")
                continue
            table = Table(title=f"Symptom History — {pet_profile['name']}", border_style="cyan")
            table.add_column("Date", width=12)
            table.add_column("Symptoms", max_width=40)
            table.add_column("Severity", width=10)
            for h in hist[-10:]:
                table.add_row(h["date"][:10], h["symptoms"][:40], h.get("severity", "N/A"))
            console.print(table)
            continue
        else:
            with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
                progress.add_task("Consulting...", total=None)
                response = get_response(user_input, history, pet_profile)

        history.append({"role": "user", "content": user_input})
        history.append({"role": "assistant", "content": response})

        console.print()
        console.print(Panel(Markdown(response), title="[bold green]🩺 Vet Advisor[/bold green]", border_style="green"))

    console.print(f"\n[bold cyan]🐾 Take good care of {pet_profile['name']}! Goodbye![/bold cyan]")


@cli.command()
def list_pets():
    """List all saved pet profiles."""
    profiles = load_pet_profiles()
    if not profiles:
        console.print("[yellow]No saved pet profiles.[/yellow]")
        return
    table = Table(title="Saved Pet Profiles", border_style="cyan")
    table.add_column("Name", width=15)
    table.add_column("Type", width=10)
    table.add_column("Breed", width=15)
    table.add_column("Age", width=10)
    table.add_column("Weight", width=10)
    for p in profiles:
        table.add_row(p["name"], p["type"], p.get("breed", "N/A"),
                      p.get("age", "N/A"), p.get("weight", "N/A"))
    console.print(table)


def main():
    """Entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
