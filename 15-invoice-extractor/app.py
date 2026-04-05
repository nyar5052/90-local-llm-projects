"""
Invoice Extractor — Extract structured data from invoices and receipts.

Uses a local LLM (via Ollama) to parse invoice text and return structured
JSON containing vendor details, line items, totals, and payment terms.
"""

import sys
import os
import json
import re

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from common.llm_client import chat, check_ollama_running

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.json import JSON as RichJSON

console = Console()

SYSTEM_PROMPT = """\
You are an expert invoice parser. Given the raw text of an invoice or receipt,
extract ALL relevant information and return it as a single valid JSON object.

Return ONLY the JSON object — no markdown fences, no commentary.

Use this exact schema:
{
  "vendor": {
    "name": "string",
    "address": "string or null",
    "phone": "string or null",
    "email": "string or null"
  },
  "invoice_number": "string or null",
  "date": "string (ISO 8601 preferred, e.g. 2024-01-15)",
  "due_date": "string or null",
  "line_items": [
    {
      "description": "string",
      "quantity": number,
      "unit_price": number,
      "total": number
    }
  ],
  "subtotal": number,
  "tax": number,
  "grand_total": number,
  "currency": "string (e.g. USD)",
  "payment_terms": "string or null"
}

Rules:
- Use numeric types for all monetary values (no currency symbols).
- If a field cannot be determined, use null.
- Quantities default to 1 when unspecified.
- Compute missing totals from quantity × unit_price when possible.
"""


def read_invoice_file(filepath: str) -> str:
    """Read and return the contents of an invoice text file.

    Args:
        filepath: Path to the invoice file.

    Returns:
        The raw text content of the file.

    Raises:
        click.ClickException: If the file cannot be read.
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        raise click.ClickException(f"File not found: {filepath}")
    except PermissionError:
        raise click.ClickException(f"Permission denied: {filepath}")
    except Exception as exc:
        raise click.ClickException(f"Error reading file: {exc}")


def extract_invoice_data(text: str) -> dict:
    """Send invoice text to the LLM and parse the structured JSON response.

    Args:
        text: Raw invoice text.

    Returns:
        Parsed dictionary of invoice data.

    Raises:
        click.ClickException: If the LLM response cannot be parsed as JSON.
    """
    messages = [
        {
            "role": "user",
            "content": f"Extract all data from this invoice:\n\n{text}",
        }
    ]

    response = chat(
        messages=messages,
        system_prompt=SYSTEM_PROMPT,
        temperature=0.1,
        max_tokens=4096,
    )

    return parse_llm_json(response)


def parse_llm_json(response: str) -> dict:
    """Parse a JSON object from the LLM response, tolerating markdown fences.

    Args:
        response: Raw string returned by the LLM.

    Returns:
        Parsed dictionary.

    Raises:
        click.ClickException: If no valid JSON can be extracted.
    """
    # Strip markdown code fences if present
    cleaned = re.sub(r"```(?:json)?\s*", "", response)
    cleaned = cleaned.strip().rstrip("`")

    # Try direct parse first
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # Fallback: find the first { ... } block
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    raise click.ClickException(
        "Failed to parse JSON from LLM response. Raw output:\n" + response
    )


# ---------------------------------------------------------------------------
# Output formatters
# ---------------------------------------------------------------------------

def format_json(data: dict) -> None:
    """Display invoice data as a pretty-printed JSON panel."""
    json_str = json.dumps(data, indent=2)
    console.print(Panel(RichJSON(json_str), title="📄 Invoice Data", border_style="green"))


def format_table(data: dict) -> None:
    """Display invoice data as Rich tables."""
    # Vendor & metadata
    meta_table = Table(title="🧾 Invoice Details", show_header=False, border_style="cyan")
    meta_table.add_column("Field", style="bold")
    meta_table.add_column("Value")

    vendor = data.get("vendor", {})
    meta_table.add_row("Vendor", vendor.get("name", "N/A"))
    meta_table.add_row("Address", vendor.get("address") or "N/A")
    meta_table.add_row("Phone", vendor.get("phone") or "N/A")
    meta_table.add_row("Email", vendor.get("email") or "N/A")
    meta_table.add_row("Invoice #", data.get("invoice_number") or "N/A")
    meta_table.add_row("Date", data.get("date") or "N/A")
    meta_table.add_row("Due Date", data.get("due_date") or "N/A")
    meta_table.add_row("Payment Terms", data.get("payment_terms") or "N/A")
    console.print(meta_table)
    console.print()

    # Line items
    items_table = Table(title="📦 Line Items", border_style="blue")
    items_table.add_column("#", justify="right", style="dim")
    items_table.add_column("Description")
    items_table.add_column("Qty", justify="right")
    items_table.add_column("Unit Price", justify="right")
    items_table.add_column("Total", justify="right", style="green")

    for idx, item in enumerate(data.get("line_items", []), start=1):
        items_table.add_row(
            str(idx),
            item.get("description", ""),
            str(item.get("quantity", "")),
            f"{item.get('unit_price', 0):.2f}",
            f"{item.get('total', 0):.2f}",
        )
    console.print(items_table)
    console.print()

    # Totals
    currency = data.get("currency", "USD")
    totals_table = Table(title="💰 Totals", show_header=False, border_style="yellow")
    totals_table.add_column("Label", style="bold")
    totals_table.add_column("Amount", justify="right", style="green")
    totals_table.add_row("Subtotal", f"{data.get('subtotal', 0):.2f} {currency}")
    totals_table.add_row("Tax", f"{data.get('tax', 0):.2f} {currency}")
    totals_table.add_row("Grand Total", f"[bold]{data.get('grand_total', 0):.2f} {currency}[/bold]")
    console.print(totals_table)


def format_csv(data: dict) -> None:
    """Display invoice line items as CSV to stdout."""
    print("description,quantity,unit_price,total")
    for item in data.get("line_items", []):
        desc = item.get("description", "").replace(",", ";")
        qty = item.get("quantity", "")
        price = item.get("unit_price", "")
        total = item.get("total", "")
        print(f"{desc},{qty},{price},{total}")


OUTPUT_FORMATTERS = {
    "json": format_json,
    "table": format_table,
    "csv": format_csv,
}


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

@click.command(help="🧾 Extract structured data from invoice/receipt text files.")
@click.option(
    "--file", "-f",
    "filepath",
    required=True,
    type=click.Path(exists=True),
    help="Path to the invoice text file.",
)
@click.option(
    "--output", "-o",
    "output_format",
    type=click.Choice(["json", "table", "csv"], case_sensitive=False),
    default="json",
    show_default=True,
    help="Output format.",
)
def main(filepath: str, output_format: str) -> None:
    """Extract structured data from an invoice or receipt file."""
    # Verify Ollama is available
    if not check_ollama_running():
        console.print("[red bold]Error:[/] Ollama is not running. Start it with: ollama serve")
        raise SystemExit(1)

    console.print(f"[cyan]Reading invoice:[/] {filepath}")
    text = read_invoice_file(filepath)

    if not text.strip():
        raise click.ClickException("Invoice file is empty.")

    console.print("[cyan]Extracting data with LLM…[/]")
    data = extract_invoice_data(text)

    console.print()
    OUTPUT_FORMATTERS[output_format](data)


if __name__ == "__main__":
    main()
