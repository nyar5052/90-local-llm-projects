"""
Symptom Checker Bot - AI-powered symptom analysis tool.

⚠️ DISCLAIMER: This tool is for EDUCATIONAL and INFORMATIONAL purposes only.
It is NOT a substitute for professional medical advice, diagnosis, or treatment.
Always seek the advice of a qualified healthcare provider.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from common.llm_client import chat, generate, check_ollama_running

import click
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

console = Console()

DISCLAIMER = (
    "⚠️  MEDICAL DISCLAIMER ⚠️\n\n"
    "This symptom checker is for EDUCATIONAL and INFORMATIONAL purposes ONLY.\n"
    "It is NOT a substitute for professional medical advice, diagnosis, or treatment.\n\n"
    "• Do NOT use this tool to make medical decisions.\n"
    "• ALWAYS consult a qualified healthcare provider for any health concerns.\n"
    "• If you are experiencing a medical emergency, call emergency services immediately.\n\n"
    "By using this tool, you acknowledge that the information provided is NOT medical advice."
)

SYSTEM_PROMPT = (
    "You are a symptom information assistant for EDUCATIONAL purposes only. "
    "You MUST begin EVERY response with a clear disclaimer that you are NOT a doctor "
    "and this is NOT medical advice. "
    "When a user describes symptoms, you may discuss possible conditions that are "
    "commonly associated with those symptoms in general medical literature, but you MUST: "
    "1. Clearly state this is not a diagnosis. "
    "2. Strongly recommend the user consult a qualified healthcare professional. "
    "3. Never prescribe medications or specific treatments. "
    "4. Advise seeking emergency care if symptoms sound serious. "
    "5. Present information in a clear, organized manner. "
    "Keep responses helpful but always emphasize professional medical consultation."
)


def display_disclaimer():
    """Display the medical disclaimer prominently."""
    console.print(Panel(
        DISCLAIMER,
        title="[bold red]IMPORTANT MEDICAL DISCLAIMER[/bold red]",
        border_style="red",
        padding=(1, 2),
    ))


def check_symptoms(symptoms: str, conversation_history: list | None = None) -> tuple[str, list]:
    """
    Send symptoms to the LLM and return the response with updated history.

    Args:
        symptoms: User-described symptoms.
        conversation_history: Previous conversation messages.

    Returns:
        Tuple of (response text, updated conversation history).
    """
    if conversation_history is None:
        conversation_history = []

    conversation_history.append({"role": "user", "content": symptoms})

    response = chat(
        messages=conversation_history,
        system_prompt=SYSTEM_PROMPT,
        temperature=0.3,
        max_tokens=1024,
    )

    conversation_history.append({"role": "assistant", "content": response})
    return response, conversation_history


@click.group()
def cli():
    """Symptom Checker Bot - Educational symptom information tool."""
    pass


@cli.command()
@click.option(
    '--symptoms', '-s',
    required=True,
    help='Describe your symptoms (e.g., "headache, fever, sore throat").',
)
def check(symptoms: str):
    """Check symptoms with a single query (non-interactive)."""
    display_disclaimer()

    if not check_ollama_running():
        console.print("[bold red]Error:[/bold red] Ollama is not running. Please start Ollama first.")
        raise SystemExit(1)

    console.print(f"\n[bold cyan]Analyzing symptoms:[/bold cyan] {symptoms}\n")

    try:
        response, _ = check_symptoms(symptoms)
        console.print(Panel(
            Markdown(response),
            title="[bold green]Symptom Information[/bold green]",
            border_style="green",
            padding=(1, 2),
        ))
    except Exception as e:
        console.print(f"[bold red]Error communicating with LLM:[/bold red] {e}")
        raise SystemExit(1)


@cli.command()
def chat_mode():
    """Start an interactive symptom checking session."""
    display_disclaimer()

    if not check_ollama_running():
        console.print("[bold red]Error:[/bold red] Ollama is not running. Please start Ollama first.")
        raise SystemExit(1)

    console.print(Panel(
        "Describe your symptoms and I will provide general educational information.\n"
        "Type [bold]quit[/bold] or [bold]exit[/bold] to end the session.",
        title="[bold cyan]Interactive Symptom Checker[/bold cyan]",
        border_style="cyan",
    ))

    conversation_history = []

    while True:
        try:
            user_input = console.input("\n[bold yellow]Your symptoms > [/bold yellow]")
        except (EOFError, KeyboardInterrupt):
            console.print("\n[dim]Session ended.[/dim]")
            break

        if user_input.strip().lower() in ("quit", "exit", "q"):
            console.print("[dim]Session ended. Remember to consult a healthcare professional.[/dim]")
            break

        if not user_input.strip():
            console.print("[dim]Please describe your symptoms.[/dim]")
            continue

        try:
            with console.status("[cyan]Analyzing symptoms...[/cyan]"):
                response, conversation_history = check_symptoms(
                    user_input, conversation_history
                )
            console.print(Panel(
                Markdown(response),
                title="[bold green]Information[/bold green]",
                border_style="green",
                padding=(1, 2),
            ))
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {e}")


# Register 'chat' as an alias for chat_mode
cli.add_command(chat_mode, name='chat')


if __name__ == '__main__':
    cli()
