"""
Travel Itinerary Bot - AI-powered vacation planner.

Plans detailed travel itineraries based on destination, duration,
budget, and interests using Gemma 4 via Ollama.
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

SYSTEM_PROMPT = """You are an expert travel planner with extensive knowledge of destinations worldwide. Your role is to:
1. Create detailed, day-by-day travel itineraries
2. Recommend attractions, restaurants, and activities
3. Consider budget constraints and suggest cost-saving tips
4. Include practical travel tips (transportation, timing, local customs)
5. Suggest alternative plans for bad weather

For each day include:
- Morning, afternoon, and evening activities
- Restaurant/food recommendations
- Estimated costs
- Travel tips and logistics
- Time estimates for each activity"""

BUDGETS = ["budget", "moderate", "luxury"]
INTERESTS_EXAMPLES = "culture, food, nature, adventure, shopping, history, nightlife, relaxation"


def generate_itinerary(
    destination: str,
    days: int,
    budget: str,
    interests: str | None = None,
    travelers: int = 1,
) -> str:
    """Generate a travel itinerary."""
    prompt_parts = [
        f"Create a detailed {days}-day travel itinerary for {destination}.",
        f"Budget level: {budget}.",
        f"Number of travelers: {travelers}.",
    ]
    if interests:
        prompt_parts.append(f"Interests and preferences: {interests}.")
    prompt_parts.append(
        "For each day, provide a complete schedule with morning, afternoon, "
        "and evening activities, food recommendations, and estimated costs."
    )

    messages = [{"role": "user", "content": " ".join(prompt_parts)}]
    return chat(messages, system_prompt=SYSTEM_PROMPT, max_tokens=4096)


def get_place_details(place: str, destination: str) -> str:
    """Get detailed information about a specific place or attraction."""
    messages = [
        {
            "role": "user",
            "content": (
                f"Tell me more about: {place} in {destination}\n"
                "Include: description, best time to visit, entry fees, "
                "how to get there, tips, and nearby attractions."
            ),
        }
    ]
    return chat(messages, system_prompt=SYSTEM_PROMPT, max_tokens=1024)


@click.command()
@click.option("--destination", required=True, help="Travel destination")
@click.option("--days", type=click.IntRange(1, 30), default=5, help="Number of days")
@click.option("--budget", type=click.Choice(BUDGETS, case_sensitive=False), default="moderate", help="Budget level")
@click.option("--interests", type=str, default=None, help="Interests (comma-separated)")
@click.option("--travelers", type=click.IntRange(1, 20), default=1, help="Number of travelers")
def main(destination: str, days: int, budget: str, interests: str | None, travelers: int):
    """Travel Itinerary Bot - Plan your perfect vacation with AI."""
    console.print(
        Panel.fit(
            "[bold cyan]✈️ Travel Itinerary Bot[/bold cyan]\n"
            "AI-powered vacation planning",
            border_style="cyan",
        )
    )

    if not check_ollama_running():
        console.print("[red]❌ Ollama is not running. Start it with: ollama serve[/red]")
        sys.exit(1)

    console.print(f"[bold]Destination:[/bold] {destination}")
    console.print(f"[bold]Duration:[/bold] {days} days")
    console.print(f"[bold]Budget:[/bold] {budget.capitalize()}")
    console.print(f"[bold]Travelers:[/bold] {travelers}")
    if interests:
        console.print(f"[bold]Interests:[/bold] {interests}")
    console.print()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        progress.add_task(f"Planning your {destination} trip...", total=None)
        itinerary = generate_itinerary(destination, days, budget, interests, travelers)

    console.print(
        Panel(
            Markdown(itinerary),
            title=f"[bold green]🗺️ {destination} — {days}-Day Itinerary[/bold green]",
            border_style="green",
        )
    )

    console.print("\n[dim]Want details about a place? Type its name, or 'quit' to exit.[/dim]\n")

    while True:
        try:
            place = Prompt.ask("[bold yellow]📍 Tell me about[/bold yellow]")
        except (KeyboardInterrupt, EOFError):
            break

        if place.lower().strip() in ("quit", "exit", "q"):
            break
        if not place.strip():
            continue

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            progress.add_task(f"Looking up {place}...", total=None)
            details = get_place_details(place, destination)

        console.print()
        console.print(
            Panel(Markdown(details), title=f"[bold green]📍 {place}[/bold green]", border_style="green")
        )
        console.print()

    console.print("[bold cyan]✈️ Have a wonderful trip! Bon voyage![/bold cyan]")


if __name__ == "__main__":
    main()
