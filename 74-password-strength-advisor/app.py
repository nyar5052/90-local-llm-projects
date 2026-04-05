#!/usr/bin/env python3
"""Password Strength Advisor - Analyzes password policies and generates secure passwords."""

import sys
import os
import string
import secrets

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown
from common.llm_client import chat, check_ollama_running

console = Console()

SYSTEM_PROMPT = """You are a cybersecurity expert specializing in password security and 
authentication best practices. You provide:
1. Password policy analysis with NIST SP 800-63B compliance checks
2. Strength assessment and vulnerability identification
3. Improvement recommendations following industry best practices
4. Explanation of common attack vectors (brute force, dictionary, rainbow tables)

Always reference current security standards (NIST, OWASP) in your recommendations.
Format your response using markdown."""


def analyze_policy(policy_text: str) -> str:
    """Analyze a password policy for security issues.

    Args:
        policy_text: The password policy text to analyze.

    Returns:
        Analysis results with recommendations.
    """
    prompt = f"""Analyze this password policy against NIST SP 800-63B and OWASP guidelines.
Identify weaknesses, compliance gaps, and provide specific improvement recommendations.

PASSWORD POLICY:
{policy_text}

Rate each aspect: STRONG ✅, ADEQUATE ⚠️, WEAK ❌
Include: minimum length, complexity requirements, rotation policy, MFA, breach checking."""

    return chat(
        messages=[{"role": "user", "content": prompt}],
        system_prompt=SYSTEM_PROMPT,
        temperature=0.3,
        max_tokens=2048,
    )


def analyze_password(password: str) -> str:
    """Analyze a specific password for strength.

    Args:
        password: The password to analyze (handled securely).

    Returns:
        Strength analysis and recommendations.
    """
    length = len(password)
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in string.punctuation for c in password)
    char_types = sum([has_upper, has_lower, has_digit, has_special])

    # Mask the password for LLM analysis
    prompt = f"""Analyze a password with these characteristics (actual password NOT shown for security):
- Length: {length} characters
- Contains uppercase: {has_upper}
- Contains lowercase: {has_lower}
- Contains digits: {has_digit}
- Contains special characters: {has_special}
- Character types used: {char_types}/4

Estimate entropy, time to crack, and provide recommendations."""

    return chat(
        messages=[{"role": "user", "content": prompt}],
        system_prompt=SYSTEM_PROMPT,
        temperature=0.3,
        max_tokens=1024,
    )


def generate_password(length: int = 16, requirements: str = "upper,lower,digits,special") -> str:
    """Generate a cryptographically secure password.

    Args:
        length: Desired password length.
        requirements: Comma-separated character type requirements.

    Returns:
        Generated secure password.
    """
    reqs = [r.strip().lower() for r in requirements.split(",")]
    charset = ""
    mandatory = []

    if "upper" in reqs:
        charset += string.ascii_uppercase
        mandatory.append(secrets.choice(string.ascii_uppercase))
    if "lower" in reqs:
        charset += string.ascii_lowercase
        mandatory.append(secrets.choice(string.ascii_lowercase))
    if "digits" in reqs:
        charset += string.digits
        mandatory.append(secrets.choice(string.digits))
    if "special" in reqs:
        charset += string.punctuation
        mandatory.append(secrets.choice(string.punctuation))

    if not charset:
        charset = string.ascii_letters + string.digits + string.punctuation
        mandatory = [
            secrets.choice(string.ascii_uppercase),
            secrets.choice(string.ascii_lowercase),
            secrets.choice(string.digits),
            secrets.choice(string.punctuation),
        ]

    remaining = length - len(mandatory)
    if remaining < 0:
        remaining = 0

    password_chars = mandatory + [secrets.choice(charset) for _ in range(remaining)]
    # Shuffle using Fisher-Yates via secrets
    password_list = list(password_chars)
    for i in range(len(password_list) - 1, 0, -1):
        j = secrets.randbelow(i + 1)
        password_list[i], password_list[j] = password_list[j], password_list[i]

    return "".join(password_list)


@click.group(invoke_without_command=True)
@click.pass_context
@click.option("--policy", type=click.Path(exists=True), default=None, help="Policy file to analyze.")
@click.option("--analyze", is_flag=True, help="Analyze the password policy.")
@click.option("--password", type=str, default=None, help="Password to check strength.")
def main(ctx, policy, analyze, password):
    """Analyze password policies and generate secure passwords."""
    if ctx.invoked_subcommand is not None:
        return

    console.print(
        Panel(
            "[bold cyan]🔑 Password Strength Advisor[/bold cyan]",
            subtitle="Powered by Local LLM",
        )
    )

    if password:
        if not check_ollama_running():
            console.print("[bold red]Error:[/bold red] Ollama is not running.")
            sys.exit(1)
        with console.status("[bold green]Analyzing password strength..."):
            result = analyze_password(password)
        console.print(Panel(Markdown(result), title="[bold]Password Analysis[/bold]", border_style="yellow"))
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
            result = analyze_policy(policy_text)
        console.print(Panel(Markdown(result), title="[bold]Policy Analysis[/bold]", border_style="blue"))
        return

    if not policy and not password:
        console.print("[yellow]Use --policy with --analyze, --password, or 'generate' subcommand.[/yellow]")
        console.print(ctx.get_help())


@main.command()
@click.option("--length", type=int, default=16, help="Password length.")
@click.option("--requirements", type=str, default="upper,lower,digits,special", help="Character requirements.")
@click.option("--count", type=int, default=5, help="Number of passwords to generate.")
def generate(length, requirements, count):
    """Generate secure passwords."""
    console.print(
        Panel("[bold cyan]🔑 Password Generator[/bold cyan]", subtitle="Cryptographically Secure")
    )

    if length < 8:
        console.print("[bold red]Warning:[/bold red] Minimum recommended length is 8.")
        length = 8

    table = Table(title=f"Generated Passwords (length={length})")
    table.add_column("#", style="dim", width=4)
    table.add_column("Password", style="bold green")
    table.add_column("Length", justify="center")

    for i in range(count):
        pwd = generate_password(length, requirements)
        table.add_row(str(i + 1), pwd, str(len(pwd)))

    console.print(table)
    console.print(f"\n[dim]Requirements: {requirements}[/dim]")


if __name__ == "__main__":
    main()
