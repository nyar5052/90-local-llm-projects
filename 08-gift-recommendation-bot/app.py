"""
Gift Recommendation Bot - Personalized gift suggestion engine.

Suggests thoughtful gifts based on occasion, relationship, budget,
and recipient interests using Gemma 4 via Ollama.
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
from rich.table import Table
from common.llm_client import chat, check_ollama_running

console = Console()

SYSTEM_PROMPT = """You are a creative gift recommendation expert. Your role is to:
1. Suggest thoughtful, personalized gift ideas based on the recipient's profile
2. Consider budget constraints and provide options at different price points
3. Include both physical and experience-based gift ideas
4. Explain WHY each gift would be meaningful for the recipient
5. Suggest where to purchase each gift
6. Include creative wrapping or presentation ideas

Format each recommendation with:
- Gift name and brief description
- Estimated price range
- Why it's a good fit
- Where to buy it"""

OCCASIONS = [
    "birthday", "christmas", "anniversary", "wedding", "graduation",
    "baby-shower", "housewarming", "valentines", "mothers-day",
    "fathers-day", "retirement", "thank-you", "get-well", "other",
]

RELATIONSHIPS = [
    "partner", "parent", "sibling", "friend", "colleague",
    "child", "grandparent", "teacher", "boss", "neighbor",
]


def generate_recommendations(
    occasion: str,
    relationship: str,
    budget: int,
    interests: str | None = None,
    age: str | None = None,
    gender: str | None = None,
) -> str:
    """Generate gift recommendations based on parameters."""
    prompt_parts = [
        f"Suggest 5-7 gift ideas for a {occasion} gift.",
        f"Recipient: {relationship}.",
        f"Budget: up to ${budget}.",
    ]
    if interests:
        prompt_parts.append(f"Recipient's interests: {interests}.")
    if age:
        prompt_parts.append(f"Recipient's age: {age}.")
    if gender:
        prompt_parts.append(f"Recipient's gender: {gender}.")
    prompt_parts.append(
        "Include a mix of practical, fun, and sentimental options. "
        "For each gift, provide: name, price range, why it's great, and where to buy."
    )

    messages = [{"role": "user", "content": " ".join(prompt_parts)}]
    return chat(messages, system_prompt=SYSTEM_PROMPT, max_tokens=3072)


def get_gift_details(gift_name: str, budget: int) -> str:
    """Get detailed information about a specific gift idea."""
    messages = [
        {
            "role": "user",
            "content": (
                f"Give me more details about this gift idea: {gift_name}\n"
                f"Budget: up to ${budget}\n"
                "Include: specific product recommendations, where to buy, "
                "creative presentation ideas, and any DIY alternatives."
            ),
        }
    ]
    return chat(messages, system_prompt=SYSTEM_PROMPT, max_tokens=1024)


@click.command()
@click.option("--occasion", type=click.Choice(OCCASIONS, case_sensitive=False), required=True, help="Gift occasion")
@click.option("--relationship", type=click.Choice(RELATIONSHIPS, case_sensitive=False), default="friend", help="Relationship to recipient")
@click.option("--budget", type=click.IntRange(5, 10000), default=50, help="Budget in dollars")
@click.option("--interests", type=str, default=None, help="Recipient interests (comma-separated)")
@click.option("--age", type=str, default=None, help="Recipient's age or age range")
def main(occasion: str, relationship: str, budget: int, interests: str | None, age: str | None):
    """Gift Recommendation Bot - Find the perfect gift with AI help."""
    console.print(
        Panel.fit(
            "[bold cyan]🎁 Gift Recommendation Bot[/bold cyan]\n"
            "Find the perfect gift with AI",
            border_style="cyan",
        )
    )

    if not check_ollama_running():
        console.print("[red]❌ Ollama is not running. Start it with: ollama serve[/red]")
        sys.exit(1)

    # Display search parameters
    table = Table(title="Gift Search Parameters", border_style="cyan")
    table.add_column("Parameter", style="bold")
    table.add_column("Value")
    table.add_row("Occasion", occasion.replace("-", " ").title())
    table.add_row("Recipient", relationship.capitalize())
    table.add_row("Budget", f"${budget}")
    if interests:
        table.add_row("Interests", interests)
    if age:
        table.add_row("Age", age)
    console.print(table)
    console.print()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        progress.add_task("Finding perfect gifts...", total=None)
        recommendations = generate_recommendations(
            occasion, relationship, budget, interests, age
        )

    console.print(
        Panel(
            Markdown(recommendations),
            title="[bold green]🎁 Gift Recommendations[/bold green]",
            border_style="green",
        )
    )

    console.print("\n[dim]Want more details? Type a gift name, or 'quit' to exit.[/dim]\n")

    while True:
        try:
            gift = Prompt.ask("[bold yellow]🔍 More about[/bold yellow]")
        except (KeyboardInterrupt, EOFError):
            break

        if gift.lower().strip() in ("quit", "exit", "q"):
            break
        if not gift.strip():
            continue

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            progress.add_task("Getting details...", total=None)
            details = get_gift_details(gift, budget)

        console.print()
        console.print(
            Panel(Markdown(details), title=f"[bold green]🎁 {gift}[/bold green]", border_style="green")
        )
        console.print()

    console.print("[bold cyan]🎁 Happy gifting! Goodbye![/bold cyan]")


if __name__ == "__main__":
    main()
