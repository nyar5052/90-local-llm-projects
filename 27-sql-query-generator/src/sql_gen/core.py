"""
Core business logic for SQL Query Generator.
Handles schema parsing, query generation, optimization, and history.
"""

import os
import json
import time
import logging
from typing import Optional

import yaml

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an expert SQL developer. Convert natural language questions into SQL queries.

Given a database schema and a natural language question:
1. Generate the correct SQL query
2. Explain what the query does step by step
3. Note any assumptions made
4. Suggest optimizations if applicable (indexes, query structure)
5. Provide alternative approaches if relevant

Support standard SQL compatible with PostgreSQL, MySQL, and SQLite.
Format SQL in a code block. Use proper indentation and formatting."""

SUPPORTED_DIALECTS = ["standard", "postgresql", "mysql", "sqlite"]


def load_config(config_path: str = "config.yaml") -> dict:
    """Load configuration from YAML file."""
    defaults = {
        "ollama_base_url": "http://localhost:11434",
        "model": "gemma3:1b",
        "temperature": 0.3,
        "default_dialect": "standard",
        "history_file": "query_history.json",
        "max_history": 100,
        "max_schema_chars": 4000,
    }
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                user_config = yaml.safe_load(f) or {}
            defaults.update(user_config)
            logger.info("Loaded config from %s", config_path)
        except Exception as e:
            logger.warning("Failed to load config: %s", e)
    return defaults


def read_schema(schema_path: str) -> str:
    """Read a SQL schema file."""
    if not os.path.exists(schema_path):
        raise FileNotFoundError(f"Schema file '{schema_path}' not found.")
    with open(schema_path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def parse_schema_text(schema_text: str) -> list[dict]:
    """Extract table info from schema text."""
    tables = []
    current_table = None
    current_columns = []

    for line in schema_text.splitlines():
        line_stripped = line.strip()
        line_upper = line_stripped.upper()

        if line_upper.startswith("CREATE TABLE"):
            if current_table:
                tables.append({"name": current_table, "columns": current_columns})
            parts = line_stripped.split()
            if len(parts) >= 3:
                current_table = parts[2].strip("(").strip("`").strip('"').strip("'")
                current_columns = []
        elif current_table and line_stripped and not line_upper.startswith(")"):
            col_parts = line_stripped.rstrip(",").split()
            if col_parts and not col_parts[0].upper() in ("PRIMARY", "FOREIGN", "UNIQUE", "INDEX", "CONSTRAINT", "CHECK"):
                col_name = col_parts[0].strip("`").strip('"')
                col_type = col_parts[1] if len(col_parts) > 1 else "UNKNOWN"
                current_columns.append({"name": col_name, "type": col_type})
        elif line_upper.startswith(")"):
            if current_table:
                tables.append({"name": current_table, "columns": current_columns})
                current_table = None
                current_columns = []

    if current_table:
        tables.append({"name": current_table, "columns": current_columns})

    return tables


def get_table_names(schema_text: str) -> list[str]:
    """Extract table names from schema text."""
    return [t["name"] for t in parse_schema_text(schema_text)]


def visualize_schema(tables: list[dict]) -> str:
    """Generate a text-based schema visualization."""
    lines = []
    for table in tables:
        lines.append(f"┌─ {table['name']} ──────────────")
        for col in table["columns"]:
            lines.append(f"│  {col['name']}: {col['type']}")
        lines.append("└─────────────────────────")
        lines.append("")
    return "\n".join(lines)


def generate_sql(schema: str, query: str, chat_fn, dialect: str = "standard",
                 config: Optional[dict] = None) -> str:
    """Generate SQL from natural language using the LLM."""
    if config is None:
        config = load_config()

    dialect_hint = f"\nTarget SQL dialect: {dialect}" if dialect != "standard" else ""

    prompt = f"""Given this database schema:

```sql
{schema[:config.get('max_schema_chars', 4000)]}
```
{dialect_hint}

Convert this question to SQL: "{query}"

Provide the SQL query, explanation, and any optimization tips."""

    messages = [{"role": "user", "content": prompt}]
    logger.info("Generating SQL for: %s (dialect=%s)", query[:80], dialect)

    response = chat_fn(messages, system_prompt=SYSTEM_PROMPT, temperature=config.get("temperature", 0.3))
    return response


def generate_sql_no_schema(query: str, chat_fn, dialect: str = "standard",
                           config: Optional[dict] = None) -> str:
    """Generate SQL from natural language without a schema."""
    if config is None:
        config = load_config()

    dialect_hint = f"\nTarget SQL dialect: {dialect}" if dialect != "standard" else ""

    prompt = f"""Convert this natural language question to SQL:{dialect_hint}

"{query}"

Create reasonable table and column names. Provide the SQL query with explanation."""

    messages = [{"role": "user", "content": prompt}]
    logger.info("Generating SQL (no schema) for: %s", query[:80])

    response = chat_fn(messages, system_prompt=SYSTEM_PROMPT, temperature=config.get("temperature", 0.3))
    return response


def optimize_query(sql: str, chat_fn, dialect: str = "standard") -> str:
    """Get optimization suggestions for a SQL query."""
    prompt = f"""Analyze this SQL query and suggest optimizations:

```sql
{sql}
```

Target dialect: {dialect}

Provide:
1. Performance issues
2. Index recommendations
3. Optimized version of the query
4. Explanation of improvements"""

    messages = [{"role": "user", "content": prompt}]
    response = chat_fn(messages, system_prompt=SYSTEM_PROMPT, temperature=0.3)
    return response


# --- Query History ---

def load_history(history_file: str = "query_history.json") -> list[dict]:
    """Load query history."""
    if not os.path.exists(history_file):
        return []
    try:
        with open(history_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def save_to_history(entry: dict, history_file: str = "query_history.json",
                    max_history: int = 100) -> None:
    """Save a query to history."""
    history = load_history(history_file)
    entry["timestamp"] = time.time()
    history.append(entry)
    if len(history) > max_history:
        history = history[-max_history:]
    with open(history_file, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)
    logger.info("Saved query to history")


def clear_history(history_file: str = "query_history.json") -> None:
    """Clear query history."""
    with open(history_file, "w", encoding="utf-8") as f:
        json.dump([], f)
