"""
Resume Analyzer - Project 12
Analyzes resumes, suggests improvements, and scores against job descriptions
using a local LLM via Ollama.
"""

import sys
import os
import json
import re

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from common.llm_client import chat, generate, check_ollama_running

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, BarColumn, TextColumn
from rich.markdown import Markdown

console = Console()

SYSTEM_PROMPT = (
    "You are an expert resume reviewer and career coach with 20 years of "
    "experience in HR, recruiting, and talent acquisition across multiple "
    "industries. Provide specific, actionable, and professional feedback."
)


def read_file(filepath: str) -> str:
    """Read and return the contents of a text file.

    Args:
        filepath: Path to the file to read.

    Returns:
        The file contents as a string.

    Raises:
        click.ClickException: If the file cannot be read.
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read().strip()
    except FileNotFoundError:
        raise click.ClickException(f"File not found: {filepath}")
    except PermissionError:
        raise click.ClickException(f"Permission denied: {filepath}")
    except Exception as e:
        raise click.ClickException(f"Error reading {filepath}: {e}")


def analyze_resume(resume_text: str) -> dict:
    """Perform a general analysis of a resume without a job description.

    Extracts skills, experience, education, achievements, and provides
    improvement suggestions.

    Args:
        resume_text: The full text of the resume.

    Returns:
        A dict with keys: skills, experience_summary, education, achievements,
        strengths, weaknesses, formatting_suggestions, content_suggestions,
        overall_score.
    """
    prompt = f"""Analyze the following resume and provide a detailed evaluation.
Return your analysis as valid JSON with exactly these keys:
- "skills": list of extracted skills
- "experience_summary": brief summary of work experience
- "education": list of education entries
- "achievements": list of notable achievements
- "strengths": list of resume strengths
- "weaknesses": list of resume weaknesses
- "formatting_suggestions": list of formatting improvements
- "content_suggestions": list of content improvements
- "overall_score": integer from 0-100 rating the resume quality

IMPORTANT: Return ONLY valid JSON, no markdown fences, no extra text.

Resume:
\"\"\"
{resume_text}
\"\"\""""

    response = generate(
        prompt=prompt,
        system_prompt=SYSTEM_PROMPT,
        temperature=0.3,
        max_tokens=4096,
    )
    return parse_json_response(response)


def score_against_jd(resume_text: str, jd_text: str) -> dict:
    """Score a resume against a specific job description.

    Evaluates how well the resume matches the JD and provides targeted
    improvement suggestions.

    Args:
        resume_text: The full text of the resume.
        jd_text: The full text of the job description.

    Returns:
        A dict with keys: match_percentage, matching_skills, missing_skills,
        experience_alignment, suggestions, keyword_gaps, overall_assessment,
        priority_improvements.
    """
    prompt = f"""Compare the following resume against the job description and evaluate the match.
Return your analysis as valid JSON with exactly these keys:
- "match_percentage": integer from 0-100 representing overall match
- "matching_skills": list of skills from the JD found in the resume
- "missing_skills": list of skills from the JD NOT found in the resume
- "experience_alignment": string describing how well experience aligns
- "suggestions": list of specific suggestions to improve the match
- "keyword_gaps": list of important keywords from JD missing in resume
- "overall_assessment": string with overall assessment paragraph
- "priority_improvements": list of top 3 most impactful changes to make

IMPORTANT: Return ONLY valid JSON, no markdown fences, no extra text.

Resume:
\"\"\"
{resume_text}
\"\"\"

Job Description:
\"\"\"
{jd_text}
\"\"\""""

    response = generate(
        prompt=prompt,
        system_prompt=SYSTEM_PROMPT,
        temperature=0.3,
        max_tokens=4096,
    )
    return parse_json_response(response)


def parse_json_response(response: str) -> dict:
    """Parse a JSON response from the LLM, handling common formatting issues.

    Args:
        response: Raw string response from the LLM.

    Returns:
        Parsed dict from the JSON response.

    Raises:
        click.ClickException: If the response cannot be parsed as JSON.
    """
    cleaned = response.strip()
    # Strip markdown code fences if present
    cleaned = re.sub(r"^```(?:json)?\s*\n?", "", cleaned)
    cleaned = re.sub(r"\n?```\s*$", "", cleaned)
    cleaned = cleaned.strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # Try to extract JSON object from surrounding text
        match = re.search(r"\{[\s\S]*\}", cleaned)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
        raise click.ClickException(
            "Failed to parse LLM response as JSON. "
            "Try running again — LLM output can vary between runs."
        )


def display_analysis(analysis: dict) -> None:
    """Display general resume analysis results with rich formatting.

    Args:
        analysis: Parsed analysis dict from analyze_resume().
    """
    score = analysis.get("overall_score", 0)
    console.print()

    # Overall score panel
    score_color = "green" if score >= 75 else "yellow" if score >= 50 else "red"
    console.print(
        Panel(
            f"[bold {score_color}]{score}/100[/]",
            title="📊 Overall Resume Score",
            border_style=score_color,
            expand=False,
        )
    )

    # Score progress bar
    with Progress(
        TextColumn("[bold blue]Score"),
        BarColumn(bar_width=50, complete_style=score_color),
        TextColumn(f"{score}%"),
        console=console,
        transient=True,
    ) as progress:
        task = progress.add_task("Score", total=100, completed=score)

    # Skills table
    skills = analysis.get("skills", [])
    if skills:
        table = Table(title="🛠️  Extracted Skills", show_lines=True)
        table.add_column("#", style="dim", width=4)
        table.add_column("Skill", style="cyan")
        for i, skill in enumerate(skills, 1):
            table.add_row(str(i), skill)
        console.print(table)

    # Experience summary
    exp = analysis.get("experience_summary", "")
    if exp:
        console.print(Panel(exp, title="💼 Experience Summary", border_style="blue"))

    # Education
    education = analysis.get("education", [])
    if education:
        edu_text = "\n".join(f"• {e}" for e in education)
        console.print(Panel(edu_text, title="🎓 Education", border_style="blue"))

    # Achievements
    achievements = analysis.get("achievements", [])
    if achievements:
        ach_text = "\n".join(f"⭐ {a}" for a in achievements)
        console.print(Panel(ach_text, title="🏆 Achievements", border_style="green"))

    # Strengths & Weaknesses
    strengths = analysis.get("strengths", [])
    weaknesses = analysis.get("weaknesses", [])
    if strengths or weaknesses:
        sw_table = Table(title="💪 Strengths & Weaknesses", show_lines=True)
        sw_table.add_column("Strengths ✅", style="green")
        sw_table.add_column("Weaknesses ⚠️", style="red")
        max_rows = max(len(strengths), len(weaknesses))
        for i in range(max_rows):
            s = strengths[i] if i < len(strengths) else ""
            w = weaknesses[i] if i < len(weaknesses) else ""
            sw_table.add_row(s, w)
        console.print(sw_table)

    # Suggestions
    fmt_suggestions = analysis.get("formatting_suggestions", [])
    cnt_suggestions = analysis.get("content_suggestions", [])
    if fmt_suggestions:
        fmt_text = "\n".join(f"📝 {s}" for s in fmt_suggestions)
        console.print(
            Panel(fmt_text, title="📐 Formatting Suggestions", border_style="yellow")
        )
    if cnt_suggestions:
        cnt_text = "\n".join(f"💡 {s}" for s in cnt_suggestions)
        console.print(
            Panel(cnt_text, title="📋 Content Suggestions", border_style="yellow")
        )


def display_jd_score(result: dict) -> None:
    """Display JD scoring results with rich formatting.

    Args:
        result: Parsed scoring dict from score_against_jd().
    """
    match_pct = result.get("match_percentage", 0)
    console.print()

    # Match percentage
    match_color = (
        "green" if match_pct >= 75 else "yellow" if match_pct >= 50 else "red"
    )
    console.print(
        Panel(
            f"[bold {match_color}]{match_pct}%[/]",
            title="🎯 Resume-JD Match Score",
            border_style=match_color,
            expand=False,
        )
    )

    with Progress(
        TextColumn("[bold blue]Match"),
        BarColumn(bar_width=50, complete_style=match_color),
        TextColumn(f"{match_pct}%"),
        console=console,
        transient=True,
    ) as progress:
        task = progress.add_task("Match", total=100, completed=match_pct)

    # Matching vs Missing skills
    matching = result.get("matching_skills", [])
    missing = result.get("missing_skills", [])
    if matching or missing:
        skills_table = Table(title="🛠️  Skills Comparison", show_lines=True)
        skills_table.add_column("Matching ✅", style="green")
        skills_table.add_column("Missing ❌", style="red")
        max_rows = max(len(matching), len(missing))
        for i in range(max_rows):
            m = matching[i] if i < len(matching) else ""
            mi = missing[i] if i < len(missing) else ""
            skills_table.add_row(m, mi)
        console.print(skills_table)

    # Experience alignment
    exp_align = result.get("experience_alignment", "")
    if exp_align:
        console.print(
            Panel(exp_align, title="💼 Experience Alignment", border_style="blue")
        )

    # Keyword gaps
    keyword_gaps = result.get("keyword_gaps", [])
    if keyword_gaps:
        gap_text = "\n".join(f"🔑 {k}" for k in keyword_gaps)
        console.print(Panel(gap_text, title="🔍 Keyword Gaps", border_style="red"))

    # Priority improvements
    priorities = result.get("priority_improvements", [])
    if priorities:
        pri_table = Table(title="🚀 Priority Improvements", show_lines=True)
        pri_table.add_column("Priority", style="bold", width=4)
        pri_table.add_column("Improvement", style="cyan")
        for i, p in enumerate(priorities, 1):
            pri_table.add_row(str(i), p)
        console.print(pri_table)

    # Suggestions
    suggestions = result.get("suggestions", [])
    if suggestions:
        sug_text = "\n".join(f"💡 {s}" for s in suggestions)
        console.print(
            Panel(sug_text, title="📋 Improvement Suggestions", border_style="yellow")
        )

    # Overall assessment
    assessment = result.get("overall_assessment", "")
    if assessment:
        console.print(
            Panel(assessment, title="📝 Overall Assessment", border_style="blue")
        )


@click.command()
@click.option(
    "--resume",
    required=True,
    type=click.Path(exists=False),
    help="Path to the resume text file.",
)
@click.option(
    "--job-description",
    default=None,
    type=click.Path(exists=False),
    help="Path to the job description text file (optional).",
)
def main(resume: str, job_description: str | None) -> None:
    """📄 Resume Analyzer — Analyze resumes and score them against job descriptions."""
    console.print(
        Panel(
            "[bold cyan]📄 Resume Analyzer[/]\n"
            "Powered by local LLM via Ollama",
            border_style="cyan",
            expand=False,
        )
    )

    # Check Ollama
    if not check_ollama_running():
        console.print("[bold red]❌ Ollama is not running![/]")
        console.print("Start it with: [cyan]ollama serve[/]")
        raise SystemExit(1)

    # Read resume
    resume_text = read_file(resume)
    if not resume_text:
        raise click.ClickException("Resume file is empty.")

    console.print(f"[green]✓[/] Loaded resume: [cyan]{resume}[/]")

    if job_description:
        # Score against JD
        jd_text = read_file(job_description)
        if not jd_text:
            raise click.ClickException("Job description file is empty.")
        console.print(f"[green]✓[/] Loaded job description: [cyan]{job_description}[/]")

        console.print("\n[bold]Scoring resume against job description...[/]")
        with console.status("[bold cyan]Analyzing with LLM...", spinner="dots"):
            result = score_against_jd(resume_text, jd_text)

        display_jd_score(result)
    else:
        # General analysis
        console.print("\n[bold]Performing general resume analysis...[/]")
        with console.status("[bold cyan]Analyzing with LLM...", spinner="dots"):
            analysis = analyze_resume(resume_text)

        display_analysis(analysis)

    console.print("\n[dim]Analysis complete.[/]")


if __name__ == "__main__":
    main()
