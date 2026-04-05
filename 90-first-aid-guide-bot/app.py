"""
First Aid Guide Bot - Step-by-step first aid instructions for common situations.

🚨 EMERGENCY DISCLAIMER: This tool is NOT a substitute for emergency medical services.
If someone is seriously injured or in a life-threatening situation, CALL 911 IMMEDIATELY.
This is NOT medical advice. Always seek professional medical help for injuries and illness.
"""

import sys
import os

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown
from rich.prompt import Prompt
from rich.text import Text

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from common.llm_client import chat, generate, check_ollama_running

console = Console()

EMERGENCY_DISCLAIMER = (
    "[bold red]🚨 EMERGENCY DISCLAIMER[/bold red]\n\n"
    "[bold]This tool is NOT a substitute for emergency medical services.[/bold]\n"
    "[bold]This is NOT medical advice.[/bold]\n\n"
    "• For life-threatening emergencies, [bold red]CALL 911[/bold red] immediately.\n"
    "• For poison control, call [bold]1-800-222-1222[/bold].\n"
    "• Always seek professional medical evaluation for injuries.\n"
    "• This tool provides general first aid information only."
)

SYSTEM_PROMPT = (
    "You are a first aid information assistant. You provide general first aid "
    "guidance based on widely recognized first aid practices.\n\n"
    "CRITICAL RULES:\n"
    "1. ALWAYS start responses for serious or potentially serious situations with "
    "'⚠️ CALL 911/EMERGENCY SERVICES IMMEDIATELY IF...' followed by the specific "
    "warning signs that require emergency care.\n"
    "2. Provide clear, numbered step-by-step first aid instructions.\n"
    "3. Include a 'What NOT to Do' section listing common mistakes.\n"
    "4. End with 'When to Seek Professional Medical Help' guidance.\n"
    "5. NEVER diagnose conditions. Only provide general first aid information.\n"
    "6. ALWAYS remind the user that this is NOT medical advice and they should "
    "seek professional medical help.\n"
    "7. Use simple, clear language that anyone can follow in a stressful situation.\n"
    "8. If the situation sounds life-threatening, prioritize calling 911 above all else."
)

COMMON_SCENARIOS = [
    ("Minor Burns", "Small burns from cooking, hot surfaces, etc.", "🔥", "Moderate"),
    ("Cuts & Scrapes", "Minor wounds, lacerations, and abrasions", "🩹", "Low"),
    ("Choking (Adult)", "Airway obstruction in adults", "🫁", "High"),
    ("Choking (Infant)", "Airway obstruction in infants under 1 year", "👶", "High"),
    ("Sprains & Strains", "Twisted ankles, pulled muscles", "🦵", "Low-Moderate"),
    ("Allergic Reactions", "Mild to severe allergic reactions", "⚠️", "Moderate-High"),
    ("Nosebleed", "Bleeding from the nose", "👃", "Low"),
    ("Bee Stings", "Insect stings and bites", "🐝", "Low-Moderate"),
    ("Heat Exhaustion", "Overheating and heat-related illness", "🌡️", "Moderate-High"),
    ("Hypothermia", "Dangerously low body temperature", "🥶", "High"),
    ("Fractures", "Suspected broken bones", "🦴", "Moderate-High"),
    ("Seizures", "Epileptic or other seizures", "⚡", "High"),
    ("Fainting", "Loss of consciousness", "😵", "Moderate"),
    ("Eye Injuries", "Foreign objects, chemicals in eyes", "👁️", "Moderate-High"),
    ("Poisoning", "Ingestion of harmful substances", "☠️", "High"),
]


def show_disclaimer():
    """Display the emergency disclaimer prominently."""
    console.print(Panel(EMERGENCY_DISCLAIMER, border_style="red", title="🚨 Disclaimer"))
    console.print()


def get_severity_style(severity: str) -> str:
    """Return a rich style string based on severity level."""
    severity_lower = severity.lower()
    if "high" in severity_lower:
        return "bold red"
    elif "moderate" in severity_lower:
        return "bold yellow"
    return "green"


@click.group()
def cli():
    """🏥 First Aid Guide Bot - Emergency first aid information.

    \b
    🚨 EMERGENCY DISCLAIMER: This is NOT a substitute for emergency medical services.
    This is NOT medical advice. For emergencies, CALL 911.
    """
    pass


@cli.command()
@click.option(
    "--situation", "-s",
    required=True,
    type=str,
    help="Describe the first aid situation (e.g., 'minor burn', 'choking adult').",
)
def guide(situation):
    """Get step-by-step first aid instructions for a specific situation."""
    show_disclaimer()

    if not check_ollama_running():
        console.print("[red]Error: Ollama is not running. Please start it first.[/red]")
        raise SystemExit(1)

    console.print(Panel(
        f"[bold blue]First Aid Guide: {situation.title()}[/bold blue]",
        border_style="blue",
        title="🏥 First Aid",
    ))

    try:
        with console.status("[blue]Generating first aid instructions...[/blue]"):
            response = generate(
                prompt=(
                    f"Provide comprehensive first aid instructions for: {situation}\n\n"
                    f"Format your response with:\n"
                    f"1. Emergency warning signs (when to call 911)\n"
                    f"2. Step-by-step first aid instructions (numbered)\n"
                    f"3. What NOT to do (common mistakes)\n"
                    f"4. When to seek professional medical help\n\n"
                    f"Remember: This is for general information only, not medical advice."
                ),
                system_prompt=SYSTEM_PROMPT,
                temperature=0.3,
                max_tokens=1500,
            )
        guide_text = response.get("response", "")
        if guide_text:
            console.print(Panel(
                Markdown(guide_text),
                border_style="green",
                title=f"📋 First Aid: {situation.title()}",
            ))
        else:
            console.print("[yellow]No response received. Please try again.[/yellow]")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")

    console.print()
    console.print(Panel(
        "[bold]Remember:[/bold] This information is for general reference only.\n"
        "Always seek professional medical evaluation for any injury or illness.",
        border_style="yellow",
        title="⚠️ Reminder",
    ))


@cli.command("chat")
def chat_cmd():
    """Interactive first aid assistant for follow-up questions."""
    show_disclaimer()

    if not check_ollama_running():
        console.print("[red]Error: Ollama is not running. Please start it first.[/red]")
        raise SystemExit(1)

    console.print(Panel(
        "[bold blue]Interactive First Aid Assistant[/bold blue]\n\n"
        "Ask questions about first aid procedures and I'll provide\n"
        "step-by-step guidance based on standard first aid practices.\n\n"
        "[bold red]For emergencies, CALL 911 FIRST.[/bold red]\n\n"
        "[dim]Type 'quit' or 'exit' to end the session.[/dim]",
        border_style="blue",
        title="🏥 First Aid Chat",
    ))

    messages = []

    while True:
        console.print()
        user_input = Prompt.ask("[bold green]You[/bold green]")

        if user_input.lower().strip() in ("quit", "exit", "q"):
            console.print("\n[blue]Stay safe! Remember: for emergencies, always call 911. 🏥[/blue]")
            break

        messages.append({"role": "user", "content": user_input})

        try:
            with console.status("[blue]Thinking...[/blue]"):
                response = chat(
                    messages=messages,
                    system_prompt=SYSTEM_PROMPT,
                    temperature=0.3,
                    max_tokens=1500,
                )
            assistant_msg = response.get("message", {}).get("content", "")
            if not assistant_msg:
                console.print("[yellow]No response received. Please try again.[/yellow]")
                messages.pop()
                continue

            messages.append({"role": "assistant", "content": assistant_msg})
            console.print(Panel(
                Markdown(assistant_msg),
                border_style="blue",
                title="🏥 First Aid Assistant",
            ))
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            messages.pop()


@cli.command("list")
def list_scenarios():
    """List common first aid scenarios with severity levels."""
    show_disclaimer()

    table = Table(
        title="🏥 Common First Aid Scenarios",
        show_header=True,
        header_style="bold blue",
        border_style="blue",
        show_lines=True,
    )
    table.add_column("#", style="dim", width=4, justify="right")
    table.add_column("Icon", width=4, justify="center")
    table.add_column("Scenario", style="bold", min_width=20)
    table.add_column("Description", min_width=30)
    table.add_column("Severity", justify="center", min_width=12)

    for i, (name, desc, icon, severity) in enumerate(COMMON_SCENARIOS, 1):
        severity_style = get_severity_style(severity)
        table.add_row(
            str(i),
            icon,
            name,
            desc,
            f"[{severity_style}]{severity}[/{severity_style}]",
        )

    console.print(table)
    console.print()
    console.print(
        "[dim]Use [bold]python app.py guide --situation \"scenario name\"[/bold] "
        "for detailed first aid instructions.[/dim]"
    )
    console.print()
    console.print(Panel(
        "[bold red]🚨 For ANY life-threatening emergency, CALL 911 FIRST.[/bold red]",
        border_style="red",
    ))


if __name__ == "__main__":
    cli()
