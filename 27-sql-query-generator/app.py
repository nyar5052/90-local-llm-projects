"""
SQL Query Generator - Converts natural language to SQL queries.
Uses a local Gemma 4 LLM via Ollama.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from common.llm_client import chat, check_ollama_running

import click
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich.table import Table

console = Console()

SYSTEM_PROMPT = """You are an expert SQL developer. Convert natural language questions into SQL queries.

Given a database schema and a natural language question:
1. Generate the correct SQL query
2. Explain what the query does step by step
3. Note any assumptions made
4. Suggest optimizations if applicable (indexes, query structure)
5. Provide alternative approaches if relevant

Support standard SQL compatible with PostgreSQL, MySQL, and SQLite.
Format SQL in a code block. Use proper indentation and formatting."""


def read_schema(schema_path: str) -> str:
    """Read a SQL schema file."""
    if not os.path.exists(schema_path):
        console.print(f"[red]Error:[/red] Schema file '{schema_path}' not found.")
        sys.exit(1)
    with open(schema_path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def parse_schema_text(schema_text: str) -> list[str]:
    """Extract table names from schema text."""
    tables = []
    for line in schema_text.splitlines():
        line_upper = line.strip().upper()
        if line_upper.startswith("CREATE TABLE"):
            parts = line.strip().split()
            if len(parts) >= 3:
                table_name = parts[2].strip("(").strip("`").strip('"').strip("'")
                tables.append(table_name)
    return tables


def generate_sql(schema: str, query: str, dialect: str = "standard") -> str:
    """Generate SQL from natural language using the LLM."""
    dialect_hint = f"\nTarget SQL dialect: {dialect}" if dialect != "standard" else ""

    prompt = f"""Given this database schema:

```sql
{schema[:4000]}
```
{dialect_hint}

Convert this question to SQL: "{query}"

Provide the SQL query, explanation, and any optimization tips."""

    messages = [{"role": "user", "content": prompt}]

    with console.status("[bold cyan]Generating SQL query...[/bold cyan]", spinner="dots"):
        response = chat(messages, system_prompt=SYSTEM_PROMPT, temperature=0.3)

    return response


def generate_sql_no_schema(query: str, dialect: str = "standard") -> str:
    """Generate SQL from natural language without a schema."""
    dialect_hint = f"\nTarget SQL dialect: {dialect}" if dialect != "standard" else ""

    prompt = f"""Convert this natural language question to SQL:{dialect_hint}

"{query}"

Create reasonable table and column names. Provide the SQL query with explanation."""

    messages = [{"role": "user", "content": prompt}]

    with console.status("[bold cyan]Generating SQL query...[/bold cyan]", spinner="dots"):
        response = chat(messages, system_prompt=SYSTEM_PROMPT, temperature=0.3)

    return response


@click.command()
@click.option("--schema", "-s", type=click.Path(exists=True), help="Path to SQL schema file.")
@click.option("--schema-text", help="Inline schema definition.")
@click.option("--query", "-q", required=True, help="Natural language query to convert.")
@click.option(
    "--dialect", "-d", default="standard",
    type=click.Choice(["standard", "postgresql", "mysql", "sqlite"], case_sensitive=False),
    help="SQL dialect (default: standard).",
)
def main(schema: str, schema_text: str, query: str, dialect: str):
    """🗃️ SQL Query Generator - Convert natural language to SQL."""
    console.print(
        Panel(
            "[bold cyan]🗃️ SQL Query Generator[/bold cyan]\n"
            "Convert natural language questions to SQL queries",
            border_style="cyan",
        )
    )

    if not check_ollama_running():
        console.print("[red]Error:[/red] Ollama is not running. Start it with: ollama serve")
        sys.exit(1)

    console.print(f'[dim]Query:[/dim] "{query}"')
    console.print(f"[dim]Dialect:[/dim] {dialect}")

    if schema:
        schema_content = read_schema(schema)
        tables = parse_schema_text(schema_content)
        if tables:
            console.print(f"[dim]Tables found:[/dim] {', '.join(tables)}")
        console.print()

        # Show schema preview
        syntax = Syntax(schema_content[:1000], "sql", line_numbers=True, theme="monokai")
        console.print(Panel(syntax, title="📊 Schema", border_style="dim"))

        result = generate_sql(schema_content, query, dialect)
    elif schema_text:
        result = generate_sql(schema_text, query, dialect)
    else:
        console.print("[dim]No schema provided — generating with assumed table structure[/dim]")
        console.print()
        result = generate_sql_no_schema(query, dialect)

    console.print()
    console.print(Panel(Markdown(result), title="📝 Generated SQL", border_style="green"))


if __name__ == "__main__":
    main()
