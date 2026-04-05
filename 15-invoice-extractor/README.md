# 🧾 Invoice Extractor

Extract structured data from invoices and receipts using a local LLM.

Feed in a plain-text invoice and get back clean, structured JSON with vendor
details, line items, totals, tax, and payment terms — no cloud APIs required.

## ✨ Features

- **Structured extraction** — vendor info, invoice number, date, line items,
  subtotal, tax, grand total, and payment terms.
- **Multiple output formats** — JSON, Rich table, or CSV.
- **Local & private** — runs entirely on your machine via Ollama + Gemma 4.
- **Robust parsing** — tolerates markdown fences and noisy LLM output.
- **Beautiful CLI** — powered by Rich for colourful, readable output.

## 📋 Prerequisites

- Python 3.10+
- [Ollama](https://ollama.ai/) running locally (`ollama serve`)
- The **gemma4** model pulled (`ollama pull gemma4`)

## 🚀 Installation

```bash
cd 15-invoice-extractor
pip install -r requirements.txt
```

## 📖 Usage

```bash
# JSON output (default)
python app.py --file invoice.txt

# Rich table output
python app.py --file invoice.txt --output table

# CSV output (pipe-friendly)
python app.py --file invoice.txt --output csv
```

### CLI Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--file` | `-f` | Path to invoice text file (required) | — |
| `--output` | `-o` | Output format: `json`, `table`, `csv` | `json` |

## 📄 Example Output

### JSON

```json
{
  "vendor": {
    "name": "ACME Corporation",
    "address": "123 Business Ave, Suite 100, New York, NY 10001",
    "phone": null,
    "email": null
  },
  "invoice_number": "INV-2024-0042",
  "date": "2024-03-15",
  "due_date": "2024-04-15",
  "line_items": [
    { "description": "Widget A", "quantity": 2, "unit_price": 25.00, "total": 50.00 },
    { "description": "Widget B", "quantity": 5, "unit_price": 10.00, "total": 50.00 }
  ],
  "subtotal": 250.00,
  "tax": 20.00,
  "grand_total": 270.00,
  "currency": "USD",
  "payment_terms": "Net 30"
}
```

### Table

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃       🧾 Invoice Details            ┃
┡━━━━━━━━━━━━━━━┯━━━━━━━━━━━━━━━━━━━━━┩
│ Vendor        │ ACME Corporation    │
│ Invoice #     │ INV-2024-0042       │
│ Date          │ 2024-03-15          │
│ Payment Terms │ Net 30              │
└───────────────┴─────────────────────┘
```

## 🧪 Running Tests

```bash
pytest test_app.py -v
```

## 🏗️ Project Structure

```
15-invoice-extractor/
├── app.py              # Main application & CLI
├── test_app.py         # Pytest test suite
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

## 📝 License

Part of the **90 Local LLM Projects** collection.
