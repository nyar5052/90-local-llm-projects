"""
Drug Interaction Checker - CLI Interface

⚠️ DISCLAIMER: This tool is for EDUCATIONAL and INFORMATIONAL purposes only.
It is NOT a substitute for professional medical or pharmacological advice.
"""

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown

from .core import (
    DISCLAIMER,
    check_interactions,
    check_ollama_running,
    classify_severity,
    display_results,
    get_alternatives,
    get_dosage_notes,
    get_food_interactions,
    parse_medications,
    SEVERITY_LEVELS,
)

console = Console()


def display_disclaimer():
    """Display the medical disclaimer prominently."""
    console.print(Panel(
        DISCLAIMER,
        title="[bold red]IMPORTANT MEDICAL DISCLAIMER[/bold red]",
        border_style="red",
        padding=(1, 2),
    ))


@click.group()
def cli():
    """💊 Drug Interaction Checker - Educational medication interaction tool.

    ⚠️  This tool is for EDUCATIONAL and INFORMATIONAL purposes ONLY.
    ALWAYS consult a qualified healthcare provider or pharmacist.
    """
    pass


@cli.command()
@click.option(
    '--medications', '-m',
    required=True,
    help='Comma-separated list of medications (e.g., "aspirin,ibuprofen,lisinopril").',
)
def check(medications: str):
    """Check interactions for a list of medications."""
    display_disclaimer()

    if not check_ollama_running():
        console.print("[bold red]Error:[/bold red] Ollama is not running. Please start Ollama first.")
        raise SystemExit(1)

    med_list = parse_medications(medications)
    if len(med_list) < 2:
        console.print("[bold red]Error:[/bold red] Please provide at least two medications to check interactions.")
        raise SystemExit(1)

    console.print(f"\n[bold cyan]Checking interactions for {len(med_list)} medications...[/bold cyan]\n")

    try:
        response = check_interactions(med_list)
        display_results(med_list, response)
    except Exception as e:
        console.print(f"[bold red]Error communicating with LLM:[/bold red] {e}")
        raise SystemExit(1)


@cli.command()
@click.option(
    '--medication', '-m',
    required=True,
    help='Medication name to check food interactions for.',
)
def food(medication: str):
    """Check food interactions for a specific medication."""
    display_disclaimer()

    foods = get_food_interactions(medication)
    if not foods:
        console.print(
            f"\n[yellow]No food interactions found for '[bold]{medication}[/bold]' in our database.[/yellow]"
        )
        console.print("[dim]This does not mean there are no food interactions — consult a pharmacist.[/dim]")
        return

    table = Table(
        title=f"🍎 Food Interactions for {medication.title()}",
        show_header=True,
        header_style="bold yellow",
    )
    table.add_column("#", style="dim", width=4)
    table.add_column("Food / Substance", style="bold yellow")

    for i, item in enumerate(foods, 1):
        table.add_row(str(i), item)

    console.print()
    console.print(table)
    console.print(
        "\n[dim]⚠️  This is not exhaustive. ALWAYS consult a pharmacist for complete information.[/dim]"
    )


@cli.command()
@click.option(
    '--medication', '-m',
    required=True,
    help='Medication name to look up alternatives for.',
)
def alternatives(medication: str):
    """Show common alternatives for a medication."""
    display_disclaimer()

    alts = get_alternatives(medication)
    dosage = get_dosage_notes(medication)

    if not alts:
        console.print(
            f"\n[yellow]No alternatives found for '[bold]{medication}[/bold]' in our database.[/yellow]"
        )
        console.print("[dim]Consult your healthcare provider for alternative options.[/dim]")
        return

    table = Table(
        title=f"💡 Alternatives for {medication.title()}",
        show_header=True,
        header_style="bold blue",
    )
    table.add_column("#", style="dim", width=4)
    table.add_column("Alternative Medication", style="bold blue")

    for i, alt in enumerate(alts, 1):
        table.add_row(str(i), alt)

    console.print()
    if dosage:
        console.print(f"  📋 {medication.title()}: {dosage}\n")
    console.print(table)
    console.print(
        "\n[dim]⚠️  NEVER switch medications without consulting your healthcare provider.[/dim]"
    )


@cli.command()
def interactive():
    """Start an interactive drug interaction checking session."""
    display_disclaimer()

    if not check_ollama_running():
        console.print("[bold red]Error:[/bold red] Ollama is not running. Please start Ollama first.")
        raise SystemExit(1)

    console.print(Panel(
        "Enter medications as a comma-separated list to check for interactions.\n"
        "Type [bold]quit[/bold] or [bold]exit[/bold] to end the session.\n\n"
        "Commands:\n"
        "  [cyan]check[/cyan]  <med1, med2, ...>  — Check drug interactions\n"
        "  [cyan]food[/cyan]   <medication>        — Check food interactions\n"
        "  [cyan]alt[/cyan]    <medication>        — Show alternatives\n"
        "  [cyan]dose[/cyan]   <medication>        — Show dosage notes",
        title="[bold cyan]Interactive Drug Interaction Checker[/bold cyan]",
        border_style="cyan",
    ))

    while True:
        try:
            user_input = console.input("\n[bold yellow]💊 > [/bold yellow]").strip()
        except (EOFError, KeyboardInterrupt):
            console.print("\n[dim]Session ended.[/dim]")
            break

        if user_input.lower() in ("quit", "exit", "q"):
            console.print("[dim]Session ended. Always consult a pharmacist about drug interactions.[/dim]")
            break

        if not user_input:
            continue

        # Parse commands
        parts = user_input.split(maxsplit=1)
        command = parts[0].lower()
        arg = parts[1].strip() if len(parts) > 1 else ""

        if command == "food" and arg:
            foods = get_food_interactions(arg)
            if foods:
                console.print(f"\n🍎 Food interactions for [bold]{arg}[/bold]: {', '.join(foods)}")
            else:
                console.print(f"[yellow]No food interactions found for '{arg}' in database.[/yellow]")
            continue

        if command == "alt" and arg:
            alts = get_alternatives(arg)
            if alts:
                console.print(f"\n💡 Alternatives for [bold]{arg}[/bold]: {', '.join(alts)}")
            else:
                console.print(f"[yellow]No alternatives found for '{arg}' in database.[/yellow]")
            continue

        if command == "dose" and arg:
            dosage = get_dosage_notes(arg)
            if dosage:
                console.print(f"\n📋 {arg.title()}: {dosage}")
            else:
                console.print(f"[yellow]No dosage notes found for '{arg}' in database.[/yellow]")
            continue

        # Default: treat entire input as medication list for interaction check
        if command == "check" and arg:
            med_input = arg
        else:
            med_input = user_input

        med_list = parse_medications(med_input)
        if len(med_list) < 2:
            console.print("[yellow]Please enter at least two medications separated by commas.[/yellow]")
            continue

        try:
            with console.status("[cyan]Analysing interactions...[/cyan]"):
                response = check_interactions(med_list)
            display_results(med_list, response)
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {e}")


if __name__ == '__main__':
    cli()
