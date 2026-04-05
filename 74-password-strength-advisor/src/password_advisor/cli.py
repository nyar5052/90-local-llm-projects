"""CLI interface for Password Strength Advisor."""

import sys
import os
import logging

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown

from common.llm_client import check_ollama_running
from src.password_advisor.core import (
    calculate_entropy,
    check_breach_database,
    generate_policy,
    analyze_password_llm,
    analyze_policy_llm,
    generate_password,
    bulk_analyze,
    StrengthLevel,
)
from src.password_advisor.config import load_config

console = Console()
logger = logging.getLogger(__name__)


def _setup_logging(verbose: bool = False) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


STRENGTH_COLORS = {
    StrengthLevel.VERY_STRONG: "bold green",
    StrengthLevel.STRONG: "green",
    StrengthLevel.FAIR: "yellow",
    StrengthLevel.WEAK: "red",
    StrengthLevel.VERY_WEAK: "bold red",
}


@click.group(invoke_without_command=True)
@click.pass_context
@click.option("--password", type=str, default=None, help="Password to analyze.")
@click.option("--policy", type=click.Path(exists=True), default=None, help="Policy file to analyze.")
@click.option("--analyze", is_flag=True, help="Analyze with LLM.")
@click.option("--entropy", is_flag=True, help="Show entropy calculation only.")
@click.option("--breach-check", is_flag=True, help="Check against breach database.")
@click.option("--verbose", is_flag=True, help="Enable verbose logging.")
def main(ctx, password, policy, analyze, entropy, breach_check, verbose):
    """🔑 Analyze password policies and generate secure passwords."""
    if ctx.invoked_subcommand is not None:
        return

    _setup_logging(verbose)
    config = load_config()

    console.print(
        Panel(
            "[bold cyan]🔑 Password Strength Advisor[/bold cyan]\n"
            "[dim]Entropy Analysis, Breach Detection & Policy Generation[/dim]",
            subtitle="v1.0.0",
        )
    )

    if password:
        # Entropy calculation (no LLM)
        ent = calculate_entropy(password)
        color = STRENGTH_COLORS.get(ent.strength, "dim")

        table = Table(title="Password Entropy Analysis")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="bold")
        table.add_row("Entropy", f"{ent.entropy_bits:.1f} bits")
        table.add_row("Strength", f"[{color}]{ent.strength.value.replace('_', ' ').title()}[/{color}]")
        table.add_row("Charset Size", str(ent.charset_size))
        table.add_row("Effective Length", str(ent.effective_length))
        table.add_row("Time to Crack", ent.time_to_crack)
        table.add_row("Char Types", f"{ent.details.get('char_types', 0)}/4")
        console.print(table)

        # Breach check
        if breach_check:
            breach = check_breach_database(password)
            if breach.is_compromised:
                console.print(f"\n[bold red]⚠️ BREACH DETECTED:[/bold red] {breach.recommendation}")
            else:
                console.print(f"\n[green]✅ Not found in breach database.[/green] {breach.recommendation}")

        # LLM analysis
        if analyze:
            if not check_ollama_running():
                console.print("[bold red]Error:[/bold red] Ollama is not running.")
                sys.exit(1)
            with console.status("[bold green]Analyzing password strength..."):
                result = analyze_password_llm(password)
            console.print(Panel(Markdown(result), title="[bold]AI Analysis[/bold]", border_style="yellow"))
        return

    if policy and analyze:
        if not check_ollama_running():
            console.print("[bold red]Error:[/bold red] Ollama is not running.")
            sys.exit(1)
        with open(policy, "r", encoding="utf-8") as f:
            policy_text = f.read()
        if not policy_text.strip():
            console.print("[bold red]Error:[/bold red] Policy file is empty.")
            sys.exit(1)
        with console.status("[bold green]Analyzing password policy..."):
            result = analyze_policy_llm(policy_text)
        console.print(Panel(Markdown(result), title="[bold]Policy Analysis[/bold]", border_style="blue"))
        return

    if not policy and not password:
        console.print("[yellow]Use --password, --policy with --analyze, or 'generate'/'policy'/'bulk' subcommand.[/yellow]")
        console.print(ctx.get_help())


@main.command()
@click.option("--length", type=int, default=16, help="Password length.")
@click.option("--requirements", type=str, default="upper,lower,digits,special", help="Character requirements.")
@click.option("--count", type=int, default=5, help="Number of passwords to generate.")
def generate(length, requirements, count):
    """Generate secure passwords."""
    if length < 8:
        console.print("[bold red]Warning:[/bold red] Minimum recommended length is 8.")
        length = 8

    table = Table(title=f"Generated Passwords (length={length})")
    table.add_column("#", style="dim", width=4)
    table.add_column("Password", style="bold green")
    table.add_column("Entropy", justify="center")
    table.add_column("Strength", justify="center")

    for i in range(count):
        pwd = generate_password(length, requirements)
        ent = calculate_entropy(pwd)
        color = STRENGTH_COLORS.get(ent.strength, "dim")
        table.add_row(str(i + 1), pwd, f"{ent.entropy_bits:.0f}b", f"[{color}]{ent.strength.value}[/{color}]")

    console.print(table)


@main.command()
def policy():
    """Show NIST SP 800-63B compliant policy."""
    rules = generate_policy()
    table = Table(title="Recommended Password Policy (NIST SP 800-63B)")
    table.add_column("Rule", style="cyan")
    table.add_column("Description", max_width=60)
    table.add_column("Enabled", justify="center")
    for rule in rules:
        table.add_row(rule.name, rule.description, "✅" if rule.enabled else "❌")
    console.print(table)


@main.command()
@click.option("--file", "filepath", type=click.Path(exists=True), required=True, help="File with passwords (one per line).")
def bulk(filepath):
    """Bulk analyze passwords from file."""
    with open(filepath, "r") as f:
        passwords = [line.strip() for line in f if line.strip()]

    results = bulk_analyze(passwords)
    table = Table(title=f"Bulk Password Analysis ({len(results)} passwords)")
    table.add_column("#", style="dim", width=4)
    table.add_column("Masked", width=20)
    table.add_column("Entropy", justify="center")
    table.add_column("Strength", justify="center")
    table.add_column("Issues")

    for r in results:
        color = STRENGTH_COLORS.get(r.strength, "dim")
        table.add_row(
            str(r.index + 1), r.masked, f"{r.entropy:.0f}b",
            f"[{color}]{r.strength.value}[/{color}]",
            ", ".join(r.issues) if r.issues else "✅",
        )
    console.print(table)


if __name__ == "__main__":
    main()
