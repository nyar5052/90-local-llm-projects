"""
First Aid Guide Bot - Command-line interface.

🚨 EMERGENCY DISCLAIMER: This tool is NOT a substitute for emergency medical services.
If someone is seriously injured or in a life-threatening situation, CALL 911 IMMEDIATELY.
This is NOT medical advice. Always seek professional medical help for injuries and illness.
"""

import click
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

from first_aid.core import (
    COMMON_SCENARIOS,
    EMERGENCY_DISCLAIMER,
    SYSTEM_PROMPT,
    EmergencyContact,
    EmergencyContactManager,
    chat,
    check_ollama_running,
    evaluate_emergency,
    generate,
    get_cpr_steps,
    get_severity_style,
    get_supply_checklist,
    show_disclaimer,
)

console = Console()

# Module-level contact manager for the CLI session
_contact_manager = EmergencyContactManager()


@click.group()
def cli():
    """🏥 First Aid Guide Bot - Emergency first aid information.

    \b
    🚨 EMERGENCY DISCLAIMER: This is NOT a substitute for emergency medical services.
    This is NOT medical advice. For emergencies, CALL 911.
    """
    pass


# -------------------------------------------------------------------
# guide command
# -------------------------------------------------------------------
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


# -------------------------------------------------------------------
# chat command
# -------------------------------------------------------------------
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


# -------------------------------------------------------------------
# list command
# -------------------------------------------------------------------
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
        "[dim]Use [bold]first-aid guide --situation \"scenario name\"[/bold] "
        "for detailed first aid instructions.[/dim]"
    )
    console.print()
    console.print(Panel(
        "[bold red]🚨 For ANY life-threatening emergency, CALL 911 FIRST.[/bold red]",
        border_style="red",
    ))


# -------------------------------------------------------------------
# triage command
# -------------------------------------------------------------------
@cli.command()
@click.option("--conscious/--unconscious", default=True, help="Is the person conscious?")
@click.option("--breathing/--not-breathing", default=True, help="Is the person breathing?")
@click.option("--bleeding", is_flag=True, default=False, help="Is there severe bleeding?")
def triage(conscious, breathing, bleeding):
    """🔀 Emergency triage - quick situation assessment using decision tree."""
    show_disclaimer()

    console.print(Panel(
        "[bold red]🚨 EMERGENCY TRIAGE ASSESSMENT[/bold red]\n\n"
        "This is a quick triage tool. For ANY life-threatening emergency,\n"
        "[bold red]CALL 911 IMMEDIATELY.[/bold red]",
        border_style="red",
        title="🔀 Triage",
    ))

    result = evaluate_emergency(conscious, breathing, bleeding)

    # Status display
    status_table = Table(show_header=False, border_style="blue", show_lines=True)
    status_table.add_column("Check", style="bold", width=20)
    status_table.add_column("Status", width=30)
    status_table.add_row("Conscious", "✅ Yes" if conscious else "❌ No")
    status_table.add_row("Breathing", "✅ Yes" if breathing else "❌ No")
    status_table.add_row("Severe Bleeding", "🩸 Yes" if bleeding else "No")
    console.print(status_table)
    console.print()

    # Severity styling
    sev = result["severity"]
    if sev == "critical":
        sev_style = "bold white on red"
    elif sev == "high":
        sev_style = "bold red"
    elif sev == "low":
        sev_style = "green"
    else:
        sev_style = "bold yellow"

    console.print(Panel(
        f"[bold]Action:[/bold] {result['action']}\n"
        f"[bold]Severity:[/bold] [{sev_style}]{sev.upper()}[/{sev_style}]\n"
        f"[bold]Call 911:[/bold] {'[bold red]YES - CALL NOW[/bold red]' if result['call_911'] else '[green]Monitor situation[/green]'}",
        border_style="red" if result["call_911"] else "yellow",
        title="📋 Assessment Result",
    ))

    console.print()
    console.print("[bold]Instructions:[/bold]")
    for i, instruction in enumerate(result["instructions"], 1):
        console.print(f"  {i}. {instruction}")

    console.print()
    console.print(Panel(
        "[bold red]🚨 When in doubt, ALWAYS call 911.[/bold red]",
        border_style="red",
    ))


# -------------------------------------------------------------------
# supplies command
# -------------------------------------------------------------------
@cli.command()
@click.option(
    "--priority", "-p",
    type=click.Choice(["essential", "recommended", "optional", "all"], case_sensitive=False),
    default="all",
    help="Filter supplies by priority level.",
)
def supplies(priority):
    """📦 Display first aid supply checklist."""
    show_disclaimer()

    items = get_supply_checklist(priority)

    table = Table(
        title=f"📦 First Aid Supply Checklist ({priority.title()})",
        show_header=True,
        header_style="bold blue",
        border_style="blue",
        show_lines=True,
    )
    table.add_column("#", style="dim", width=4, justify="right")
    table.add_column("Item", style="bold", min_width=30)
    table.add_column("Qty", width=10, justify="center")
    table.add_column("Purpose", min_width=30)
    table.add_column("Priority", justify="center", width=14)

    for i, item in enumerate(items, 1):
        p = item["priority"]
        if p == "essential":
            pstyle = "bold red"
        elif p == "recommended":
            pstyle = "bold yellow"
        else:
            pstyle = "dim"
        table.add_row(
            str(i),
            item["item"],
            item["quantity"],
            item["purpose"],
            f"[{pstyle}]{p.title()}[/{pstyle}]",
        )

    console.print(table)
    console.print()

    essential_count = len([s for s in items if s["priority"] == "essential"])
    recommended_count = len([s for s in items if s["priority"] == "recommended"])
    optional_count = len([s for s in items if s["priority"] == "optional"])
    console.print(
        f"[bold]Total:[/bold] {len(items)} items "
        f"([red]{essential_count} essential[/red], "
        f"[yellow]{recommended_count} recommended[/yellow], "
        f"[dim]{optional_count} optional[/dim])"
    )


# -------------------------------------------------------------------
# cpr command
# -------------------------------------------------------------------
@cli.command()
def cpr():
    """❤️ Display CPR steps with timing information."""
    show_disclaimer()

    console.print(Panel(
        "[bold red]❤️ CPR (Cardiopulmonary Resuscitation) Guide[/bold red]\n\n"
        "For adults. If you are not trained in CPR, perform\n"
        "[bold]Hands-Only CPR[/bold] (compressions without breaths).\n\n"
        "[bold red]🚨 ALWAYS CALL 911 FIRST.[/bold red]",
        border_style="red",
        title="❤️ CPR Guide",
    ))

    steps = get_cpr_steps()

    for step in steps:
        duration = step["duration_seconds"]
        timing = f"⏱️  ~{duration}s" if duration > 0 else "🔄 Repeat continuously"
        console.print(Panel(
            f"[bold]{step['action']}[/bold]\n\n"
            f"{step['details']}\n\n"
            f"[dim]{timing}[/dim]",
            border_style="blue",
            title=f"Step {step['step_number']}",
        ))

    console.print()
    console.print(Panel(
        "[bold]Remember:[/bold]\n"
        "• Push hard and fast (100-120 compressions per minute)\n"
        "• Allow full chest recoil between compressions\n"
        "• Minimize interruptions in compressions\n"
        "• Use an AED as soon as one is available\n\n"
        "[bold red]🚨 Continue until professional help arrives.[/bold red]",
        border_style="red",
        title="⚠️ Key Points",
    ))


# -------------------------------------------------------------------
# contacts command
# -------------------------------------------------------------------
@cli.command()
@click.option("--add", "action", flag_value="add", help="Add a new emergency contact.")
@click.option("--remove", "action", flag_value="remove", help="Remove an emergency contact.")
@click.option("--list", "action", flag_value="list", default=True, help="List emergency contacts.")
def contacts(action):
    """📞 Manage emergency contacts."""
    show_disclaimer()

    if action == "add":
        name = Prompt.ask("[bold]Contact name[/bold]")
        number = Prompt.ask("[bold]Phone number[/bold]")
        relationship = Prompt.ask("[bold]Relationship[/bold]")
        is_default = Prompt.ask("[bold]Set as default? (y/n)[/bold]", default="n").lower() == "y"

        contact = EmergencyContact(
            name=name,
            number=number,
            relationship=relationship,
            is_default=is_default,
        )
        _contact_manager.add_contact(contact)
        console.print(f"\n[green]✅ Added contact: {name} ({number})[/green]")

    elif action == "remove":
        name = Prompt.ask("[bold]Contact name to remove[/bold]")
        if _contact_manager.remove_contact(name):
            console.print(f"\n[green]✅ Removed contact: {name}[/green]")
        else:
            console.print(f"\n[yellow]Contact '{name}' not found.[/yellow]")

    else:  # list
        all_contacts = _contact_manager.get_contacts()

        console.print(Panel(
            "[bold]📞 Built-in Emergency Numbers[/bold]\n\n"
            "• Emergency Services: [bold red]911[/bold red]\n"
            "• Poison Control: [bold]1-800-222-1222[/bold]\n"
            "• Crisis Lifeline: [bold]988[/bold]",
            border_style="red",
            title="📞 Emergency Numbers",
        ))

        if all_contacts:
            table = Table(
                title="📞 Your Emergency Contacts",
                show_header=True,
                header_style="bold blue",
                border_style="blue",
                show_lines=True,
            )
            table.add_column("Name", style="bold", min_width=15)
            table.add_column("Number", min_width=15)
            table.add_column("Relationship", min_width=15)
            table.add_column("Default", justify="center", width=8)

            for c in all_contacts:
                table.add_row(
                    c.name,
                    c.number,
                    c.relationship,
                    "⭐" if c.is_default else "",
                )
            console.print(table)
        else:
            console.print("\n[dim]No personal emergency contacts saved. Use --add to add one.[/dim]")


# -------------------------------------------------------------------
# Entry point
# -------------------------------------------------------------------
def main():
    """Entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
