#!/usr/bin/env python3
"""
CSV Data Analyzer - Ask natural language questions about CSV data.

Uses pandas to read and summarize CSV files, then sends the summary
along with user questions to a local Gemma 4 LLM via Ollama.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import click
import pandas as pd
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown

from common.llm_client import chat, check_ollama_running

console = Console()


def load_csv(file_path: str) -> pd.DataFrame:
    """Load a CSV file into a pandas DataFrame."""
    if not os.path.exists(file_path):
        console.print(f"[red]Error:[/red] File '{file_path}' not found.")
        sys.exit(1)
    try:
        df = pd.read_csv(file_path)
        if df.empty:
            console.print("[red]Error:[/red] CSV file is empty.")
            sys.exit(1)
        return df
    except Exception as e:
        console.print(f"[red]Error reading CSV:[/red] {e}")
        sys.exit(1)


def generate_data_summary(df: pd.DataFrame) -> str:
    """Generate a text summary of the DataFrame for the LLM."""
    summary_parts = []
    summary_parts.append(f"Dataset shape: {df.shape[0]} rows x {df.shape[1]} columns")
    summary_parts.append(f"Columns: {', '.join(df.columns.tolist())}")
    summary_parts.append(f"\nColumn types:\n{df.dtypes.to_string()}")
    summary_parts.append(f"\nBasic statistics:\n{df.describe(include='all').to_string()}")
    summary_parts.append(f"\nFirst 5 rows:\n{df.head().to_string()}")

    null_counts = df.isnull().sum()
    if null_counts.any():
        summary_parts.append(f"\nNull values per column:\n{null_counts[null_counts > 0].to_string()}")

    return "\n".join(summary_parts)


def display_data_preview(df: pd.DataFrame) -> None:
    """Display a preview of the data using a rich table."""
    table = Table(title="Data Preview (First 5 Rows)", show_lines=True)
    for col in df.columns:
        table.add_column(str(col), style="cyan", overflow="fold")
    for _, row in df.head().iterrows():
        table.add_row(*[str(v) for v in row.values])
    console.print(table)


def analyze_data(df: pd.DataFrame, query: str) -> str:
    """Send the data summary and query to the LLM for analysis."""
    data_summary = generate_data_summary(df)

    system_prompt = (
        "You are a data analyst expert. You are given a summary of a CSV dataset "
        "and a question about the data. Analyze the data summary carefully and "
        "provide a clear, accurate, and insightful answer. Use specific numbers "
        "from the data when possible. Format your response with markdown."
    )

    user_message = (
        f"Here is the dataset summary:\n\n{data_summary}\n\n"
        f"Question: {query}\n\n"
        "Please analyze the data and answer the question thoroughly."
    )

    messages = [{"role": "user", "content": user_message}]
    return chat(messages, system_prompt=system_prompt, temperature=0.3)


@click.command()
@click.option("--file", "-f", required=True, help="Path to the CSV file to analyze.")
@click.option("--query", "-q", required=True, help="Natural language question about the data.")
@click.option("--show-preview/--no-preview", default=True, help="Show data preview table.")
def main(file: str, query: str, show_preview: bool) -> None:
    """CSV Data Analyzer - Ask natural language questions about your CSV data."""
    console.print(Panel("📊 [bold blue]CSV Data Analyzer[/bold blue]", expand=False))

    if not check_ollama_running():
        console.print("[red]Error:[/red] Ollama is not running. Start it with: ollama serve")
        sys.exit(1)

    with console.status("[bold green]Loading CSV file..."):
        df = load_csv(file)

    console.print(f"[green]✓[/green] Loaded [bold]{file}[/bold]: {df.shape[0]} rows × {df.shape[1]} columns\n")

    if show_preview:
        display_data_preview(df)
        console.print()

    console.print(f"[bold yellow]Question:[/bold yellow] {query}\n")

    with console.status("[bold green]Analyzing data with LLM..."):
        answer = analyze_data(df, query)

    console.print(Panel(Markdown(answer), title="📈 Analysis Result", border_style="green"))


if __name__ == "__main__":
    main()
