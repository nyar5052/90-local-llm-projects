"""
Veterinary Advisor Bot - Pet health advice chatbot.

Provides pet health guidance based on pet type, breed, and symptoms
using Gemma 4 via Ollama. Includes important medical disclaimers.
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

SYSTEM_PROMPT = """You are a knowledgeable veterinary advisor AI assistant. Your role is to:
1. Provide general pet health information and guidance
2. Help identify potential issues based on described symptoms
3. Suggest when veterinary care is urgently needed
4. Offer general care tips for different pet types and breeds
5. Discuss nutrition, exercise, and preventive care

CRITICAL GUIDELINES:
- ALWAYS include a disclaimer that you are an AI and not a licensed veterinarian
- ALWAYS recommend consulting a real veterinarian for serious concerns
- Flag emergency symptoms clearly (e.g., difficulty breathing, seizures, poisoning)
- Never prescribe specific medications or dosages
- Be empathetic and supportive to worried pet owners
- If symptoms sound urgent, strongly recommend immediate vet visit"""

MEDICAL_DISCLAIMER = (
    "⚕️ **Disclaimer:** This is AI-generated advice for informational purposes only. "
    "It is NOT a substitute for professional veterinary care. Always consult a licensed "
    "veterinarian for your pet's health concerns, especially in emergencies."
)

PET_TYPES = ["dog", "cat", "bird", "fish", "rabbit", "hamster", "reptile", "other"]


def setup_pet_profile() -> dict:
    """Interactively set up a pet profile."""
    console.print(
        Panel(
            "[bold]Let's set up your pet's profile:[/bold]",
            title="[bold cyan]🐾 Pet Profile[/bold cyan]",
            border_style="cyan",
        )
    )

    pet_type = Prompt.ask(
        "[bold]Pet type[/bold]",
        choices=PET_TYPES,
        default="dog",
    )

    name = Prompt.ask("[bold]Pet's name[/bold]", default="Buddy")
    breed = Prompt.ask("[bold]Breed[/bold] (or 'mixed'/'unknown')", default="unknown")
    age = Prompt.ask("[bold]Age[/bold] (e.g., '3 years', '6 months')", default="unknown")
    weight = Prompt.ask("[bold]Weight[/bold] (e.g., '25 lbs', '5 kg')", default="unknown")

    return {
        "type": pet_type,
        "name": name,
        "breed": breed,
        "age": age,
        "weight": weight,
    }


def format_pet_context(profile: dict) -> str:
    """Format pet profile into context string."""
    return (
        f"Pet: {profile['name']} ({profile['type'].capitalize()})\n"
        f"Breed: {profile['breed']}\n"
        f"Age: {profile['age']}\n"
        f"Weight: {profile['weight']}"
    )


def get_response(user_message: str, history: list[dict], pet_profile: dict) -> str:
    """Get a response from the vet advisor bot."""
    context = format_pet_context(pet_profile)
    full_message = f"Pet Profile:\n{context}\n\nQuestion: {user_message}"
    messages = history + [{"role": "user", "content": full_message}]
    return chat(messages, system_prompt=SYSTEM_PROMPT)


def check_symptoms(symptoms: str, pet_profile: dict) -> str:
    """Check symptoms and provide guidance."""
    context = format_pet_context(pet_profile)
    messages = [
        {
            "role": "user",
            "content": (
                f"Pet Profile:\n{context}\n\n"
                f"Symptoms: {symptoms}\n\n"
                "Please analyze these symptoms and provide:\n"
                "1. Possible causes (from most to least likely)\n"
                "2. Urgency level (Emergency/Urgent/Non-urgent)\n"
                "3. Recommended immediate actions\n"
                "4. When to see a vet\n"
                "Include the medical disclaimer."
            ),
        }
    ]
    return chat(messages, system_prompt=SYSTEM_PROMPT, max_tokens=2048)


@click.command()
@click.option("--pet-type", type=click.Choice(PET_TYPES, case_sensitive=False), default=None, help="Type of pet")
@click.option("--name", default=None, help="Pet's name")
@click.option("--breed", default=None, help="Pet's breed")
def main(pet_type: str | None, name: str | None, breed: str | None):
    """Veterinary Advisor Bot - AI-powered pet health guidance."""
    console.print(
        Panel.fit(
            "[bold cyan]🐾 Veterinary Advisor Bot[/bold cyan]\n"
            "AI-powered pet health guidance",
            border_style="cyan",
        )
    )

    if not check_ollama_running():
        console.print("[red]❌ Ollama is not running. Start it with: ollama serve[/red]")
        sys.exit(1)

    console.print()
    console.print(Panel(MEDICAL_DISCLAIMER, border_style="yellow"))
    console.print()

    # Set up pet profile
    if pet_type and name:
        pet_profile = {
            "type": pet_type,
            "name": name,
            "breed": breed or "unknown",
            "age": "unknown",
            "weight": "unknown",
        }
    else:
        pet_profile = setup_pet_profile()

    console.print()
    console.print(
        Panel(
            format_pet_context(pet_profile),
            title=f"[bold green]🐾 {pet_profile['name']}'s Profile[/bold green]",
            border_style="green",
        )
    )

    console.print(
        "\n[bold]Commands:[/bold]\n"
        "  [cyan]/symptoms <description>[/cyan] — Analyze symptoms\n"
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
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                progress.add_task("Analyzing symptoms...", total=None)
                response = check_symptoms(symptoms, pet_profile)
        else:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                progress.add_task("Consulting...", total=None)
                response = get_response(user_input, history, pet_profile)

        history.append({"role": "user", "content": user_input})
        history.append({"role": "assistant", "content": response})

        console.print()
        console.print(
            Panel(Markdown(response), title="[bold green]🩺 Vet Advisor[/bold green]", border_style="green")
        )

    console.print(f"\n[bold cyan]🐾 Take good care of {pet_profile['name']}! Goodbye![/bold cyan]")


if __name__ == "__main__":
    main()
