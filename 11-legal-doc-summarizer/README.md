# 📜 Legal Document Summarizer

AI-powered legal document analysis tool that summarizes contracts, agreements, and legal documents using a local LLM via Ollama.

## Features

- **Multi-format input** — Supports PDF and text files
- **Key information extraction** — Parties, clauses, obligations, dates, termination conditions, penalties
- **Flexible output formats** — Bullet points, narrative, or detailed analysis
- **Local & private** — All processing runs locally via Ollama (no data leaves your machine)
- **Rich CLI output** — Color-coded panels, tables, and formatted markdown in the terminal

## Installation

```bash
cd 11-legal-doc-summarizer
pip install -r requirements.txt
```

Make sure [Ollama](https://ollama.ai) is installed and running with the Gemma 4 model:

```bash
ollama serve
ollama pull gemma4
```

## Usage

```bash
# Summarize a PDF contract (default bullet format)
python app.py --file contract.pdf

# Summarize with narrative format
python app.py --file agreement.txt --format narrative

# Detailed analysis with risk assessment
python app.py --file lease.pdf --format detailed

# Short flags
python app.py -f contract.pdf -fmt bullet
```

### CLI Options

| Option | Description | Default |
|--------|-------------|---------|
| `--file`, `-f` | Path to the legal document (required) | — |
| `--format`, `-fmt` | Output format: `bullet`, `narrative`, `detailed` | `bullet` |

## Example Output

```
╭──────────────────────────────────────╮
│ 📜 Legal Document Summary            │
│ File: services_agreement.pdf         │
│ Format: Bullet                       │
╰──────────────────────────────────────╯

╭─ Analysis Results ───────────────────╮
│                                      │
│ ## Parties Involved                  │
│ - Acme Corporation (Client)          │
│ - Legal Solutions LLC (Provider)     │
│                                      │
│ ## Key Clauses                       │
│ - Services scope (Exhibit A)         │
│ - Payment terms ($5,000/month)       │
│ - Confidentiality obligations        │
│                                      │
│ ## Important Dates                   │
│ - Effective: January 1, 2025         │
│ - Expiration: December 31, 2025      │
│                                      │
│ ## Termination Conditions            │
│ - 30 days written notice by either   │
│   party                              │
│                                      │
│ ## Penalties & Liabilities           │
│ - Late payment: 1.5% monthly interest│
╰──────────────────────────────────────╯
```

## Running Tests

```bash
pytest test_app.py -v
```

## Requirements

- Python 3.10+
- [Ollama](https://ollama.ai) with `gemma4` model
- Dependencies: `requests`, `rich`, `click`, `PyPDF2`, `pytest`

## Project Structure

```
11-legal-doc-summarizer/
├── app.py              # Main application
├── test_app.py         # Pytest test suite
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

## Part of

[90 Local LLM Projects](../README.md) — A collection of projects powered by local language models.
