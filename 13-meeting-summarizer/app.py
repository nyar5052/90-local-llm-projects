"""
Meeting Summarizer - Project 13
Summarizes meeting transcripts using a local LLM.
Extracts attendees, agenda topics, key decisions, action items, and follow-ups.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from common.llm_client import chat, generate, check_ollama_running

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown

console = Console()

SYSTEM_PROMPT = """You are an expert meeting analyst. Your job is to analyze meeting transcripts
and extract structured information. Always respond in the exact format requested.
Be thorough but concise. If information is not available in the transcript, say "Not mentioned"."""

SUMMARY_PROMPT_TEMPLATE = """Analyze the following meeting transcript and extract a structured summary.

Respond in EXACTLY this format (keep the section headers exactly as shown):

## ATTENDEES
- Name (Role if mentioned)

## AGENDA TOPICS
- Topic 1
- Topic 2

## KEY DECISIONS
- Decision 1
- Decision 2

## ACTION ITEMS
| Who | What | When |
|-----|------|------|
| Person | Task description | Deadline or "TBD" |

## FOLLOW-UPS
- Follow-up item 1
- Follow-up item 2

## SUMMARY
A 2-3 sentence overall summary of the meeting.

---

MEETING TRANSCRIPT:
{transcript}"""

MAX_TRANSCRIPT_LENGTH = 15000


def read_transcript(file_path: str) -> str:
    """
    Read a meeting transcript from a text file.

    Args:
        file_path: Path to the transcript file.

    Returns:
        The transcript text content.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file is empty or contains only whitespace.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Transcript file not found: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    if not content.strip():
        raise ValueError("Transcript file is empty or contains only whitespace.")

    return content


def preprocess_transcript(transcript: str) -> str:
    """
    Preprocess and truncate transcript if it exceeds the maximum length.

    Args:
        transcript: Raw transcript text.

    Returns:
        Preprocessed transcript text, truncated if necessary.
    """
    transcript = transcript.strip()

    if len(transcript) > MAX_TRANSCRIPT_LENGTH:
        console.print(
            f"[yellow]⚠ Transcript is long ({len(transcript)} chars). "
            f"Truncating to {MAX_TRANSCRIPT_LENGTH} chars.[/yellow]"
        )
        transcript = transcript[:MAX_TRANSCRIPT_LENGTH] + "\n\n[...transcript truncated...]"

    return transcript


def summarize_meeting(transcript: str) -> str:
    """
    Send the transcript to the LLM for analysis and summarization.

    Args:
        transcript: The meeting transcript text.

    Returns:
        Structured summary from the LLM.
    """
    processed = preprocess_transcript(transcript)
    prompt = SUMMARY_PROMPT_TEMPLATE.format(transcript=processed)

    messages = [{"role": "user", "content": prompt}]
    response = chat(
        messages=messages,
        system_prompt=SYSTEM_PROMPT,
        temperature=0.3,
        max_tokens=4096,
    )

    return response


def parse_action_items(summary: str) -> list[dict]:
    """
    Parse action items from the structured summary into a list of dicts.

    Args:
        summary: The full LLM summary text.

    Returns:
        List of dicts with keys: who, what, when.
    """
    action_items = []
    in_action_section = False

    for line in summary.split("\n"):
        stripped = line.strip()

        if "## ACTION ITEMS" in stripped:
            in_action_section = True
            continue
        if in_action_section and stripped.startswith("## "):
            break
        if in_action_section and "|" in stripped:
            parts = [p.strip() for p in stripped.split("|")]
            parts = [p for p in parts if p]
            # Skip header and separator rows
            if len(parts) >= 3 and parts[0] not in ("Who", "---", "-----"):
                if not all(c in "-" for c in parts[0]):
                    action_items.append({
                        "who": parts[0],
                        "what": parts[1],
                        "when": parts[2],
                    })

    return action_items


def extract_section(summary: str, section_name: str) -> str:
    """
    Extract a specific section's content from the structured summary.

    Args:
        summary: The full LLM summary text.
        section_name: Name of the section header (e.g., "ATTENDEES").

    Returns:
        The content under the specified section header.
    """
    lines = summary.split("\n")
    section_lines = []
    in_section = False

    for line in lines:
        stripped = line.strip()
        if f"## {section_name}" in stripped:
            in_section = True
            continue
        if in_section and stripped.startswith("## "):
            break
        if in_section:
            section_lines.append(line)

    content = "\n".join(section_lines).strip()
    return content if content else "Not mentioned"


def display_summary(summary: str) -> None:
    """
    Display the meeting summary with Rich formatting.

    Args:
        summary: The structured meeting summary text.
    """
    console.print()

    # Overall summary
    overall = extract_section(summary, "SUMMARY")
    console.print(Panel(
        overall,
        title="📋 Meeting Summary",
        border_style="bright_blue",
        padding=(1, 2),
    ))

    # Attendees
    attendees = extract_section(summary, "ATTENDEES")
    console.print(Panel(
        attendees,
        title="👥 Attendees",
        border_style="cyan",
        padding=(1, 2),
    ))

    # Agenda Topics
    agenda = extract_section(summary, "AGENDA TOPICS")
    console.print(Panel(
        agenda,
        title="📌 Agenda Topics",
        border_style="green",
        padding=(1, 2),
    ))

    # Key Decisions
    decisions = extract_section(summary, "KEY DECISIONS")
    console.print(Panel(
        decisions,
        title="✅ Key Decisions",
        border_style="yellow",
        padding=(1, 2),
    ))

    # Action Items Table
    action_items = parse_action_items(summary)
    if action_items:
        table = Table(
            title="📝 Action Items",
            show_header=True,
            header_style="bold magenta",
            border_style="magenta",
            padding=(0, 1),
        )
        table.add_column("Who", style="bold cyan", min_width=15)
        table.add_column("What", style="white", min_width=30)
        table.add_column("When", style="yellow", min_width=12)

        for item in action_items:
            table.add_row(item["who"], item["what"], item["when"])

        console.print(table)
    else:
        console.print(Panel(
            "No action items identified.",
            title="📝 Action Items",
            border_style="magenta",
        ))

    # Follow-ups
    followups = extract_section(summary, "FOLLOW-UPS")
    console.print(Panel(
        followups,
        title="🔄 Follow-ups",
        border_style="bright_red",
        padding=(1, 2),
    ))

    console.print()


def save_summary(summary: str, output_path: str) -> None:
    """
    Save the meeting summary to a file.

    Args:
        summary: The structured meeting summary text.
        output_path: Path to write the output file.
    """
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(summary)

    console.print(f"[green]✅ Summary saved to: {output_path}[/green]")


@click.command()
@click.option(
    "--transcript",
    required=True,
    type=click.Path(exists=False),
    help="Path to the meeting transcript file.",
)
@click.option(
    "--output",
    default=None,
    type=click.Path(),
    help="Optional path to save the summary output.",
)
def main(transcript: str, output: str) -> None:
    """📋 Meeting Summarizer - Extract insights from meeting transcripts."""
    console.print(Panel(
        "[bold]Meeting Summarizer[/bold]\n"
        "Extracts attendees, decisions, action items, and follow-ups.",
        title="📋 Project 13",
        border_style="bright_blue",
    ))

    # Check Ollama is running
    if not check_ollama_running():
        console.print("[bold red]Error:[/bold red] Ollama is not running.")
        console.print("Start it with: [cyan]ollama serve[/cyan]")
        raise SystemExit(1)

    # Read transcript
    try:
        transcript_text = read_transcript(transcript)
    except (FileNotFoundError, ValueError) as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise SystemExit(1)

    console.print(f"[dim]Loaded transcript: {transcript} ({len(transcript_text)} chars)[/dim]")

    # Summarize
    with console.status("[bold green]Analyzing meeting transcript...[/bold green]"):
        summary = summarize_meeting(transcript_text)

    # Display
    display_summary(summary)

    # Save if requested
    if output:
        save_summary(summary, output)


if __name__ == "__main__":
    main()
