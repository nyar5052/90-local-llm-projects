#!/usr/bin/env python3
"""Cover Letter Generator - Generate personalized cover letters using a local LLM."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import click
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, TextColumn
from common.llm_client import chat, check_ollama_running

console = Console()

TONES = ["professional", "enthusiastic", "confident", "conversational"]


def read_file(filepath: str, label: str) -> str:
    """Read content from a text file."""
    if not os.path.exists(filepath):
        console.print(f"[red]Error: {label} file not found: {filepath}[/red]")
        sys.exit(1)
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()


def build_prompt(
    resume: str, job_description: str, company: str, tone: str, name: str | None
) -> str:
    """Build the cover letter generation prompt."""
    name_str = f"Applicant Name: {name}\n" if name else ""
    return (
        f"Write a personalized cover letter for the following job application.\n\n"
        f"{name_str}"
        f"Company: {company}\n"
        f"Tone: {tone}\n\n"
        f"## Resume/Background:\n{resume}\n\n"
        f"## Job Description:\n{job_description}\n\n"
        f"Requirements:\n"
        f"1. Match specific resume highlights to job requirements\n"
        f"2. Show knowledge of the company and its values\n"
        f"3. Highlight 2-3 most relevant achievements with metrics\n"
        f"4. Explain why this role is a perfect fit\n"
        f"5. Include a strong opening hook (not 'I am writing to apply...')\n"
        f"6. End with a confident call to action\n"
        f"7. Keep it under 400 words\n"
        f"8. Use proper business letter format\n"
        f"9. Tone should be {tone}\n"
    )


def generate_cover_letter(
    resume: str, job_description: str, company: str, tone: str, name: str | None
) -> str:
    """Generate a cover letter using the LLM."""
    system_prompt = (
        "You are a professional career coach and expert cover letter writer. "
        "You craft compelling, personalized cover letters that highlight the perfect "
        "match between a candidate's experience and a job's requirements. "
        "Your letters get interviews."
    )
    user_prompt = build_prompt(resume, job_description, company, tone, name)
    messages = [{"role": "user", "content": user_prompt}]
    return chat(messages, system_prompt=system_prompt, temperature=0.7, max_tokens=2048)


@click.command()
@click.option("--resume", required=True, help="Path to resume text file.")
@click.option("--job-description", "job_desc", required=True, help="Path to job description text file.")
@click.option("--company", required=True, help="Company name.")
@click.option(
    "--tone",
    type=click.Choice(TONES, case_sensitive=False),
    default="professional",
    help="Writing tone.",
)
@click.option("--name", default=None, help="Applicant name.")
@click.option("--output", "-o", default=None, help="Save output to file.")
def main(resume: str, job_desc: str, company: str, tone: str, name: str | None, output: str):
    """Generate personalized cover letters matching resume to job descriptions."""
    console.print(Panel.fit("[bold green]Cover Letter Generator[/bold green]", border_style="green"))

    if not check_ollama_running():
        console.print("[red]Error: Ollama is not running. Start it with: ollama serve[/red]")
        sys.exit(1)

    resume_text = read_file(resume, "Resume")
    jd_text = read_file(job_desc, "Job description")

    console.print(f"[cyan]Company:[/cyan] {company}")
    console.print(f"[cyan]Tone:[/cyan] {tone}")
    console.print(f"[cyan]Resume:[/cyan] {resume} ({len(resume_text)} chars)")
    console.print(f"[cyan]Job Description:[/cyan] {job_desc} ({len(jd_text)} chars)")
    if name:
        console.print(f"[cyan]Name:[/cyan] {name}")
    console.print()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        progress.add_task("Writing cover letter...", total=None)
        result = generate_cover_letter(resume_text, jd_text, company, tone, name)

    console.print(Panel(Markdown(result), title="✉️ Cover Letter", border_style="green"))

    word_count = len(result.split())
    console.print(f"\n[dim]Word count: ~{word_count}[/dim]")

    if output:
        with open(output, "w", encoding="utf-8") as f:
            f.write(result)
        console.print(f"[green]Saved to {output}[/green]")


if __name__ == "__main__":
    main()
