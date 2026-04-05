<div align="center">

# Presentation Generator

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Powered by Ollama](https://img.shields.io/badge/LLM-Ollama-green.svg)](https://ollama.ai/)

**Generate compelling slide decks with speaker notes, visual suggestions, and timing estimates using AI.**

[Features](#-features) - [Installation](#-installation) - [CLI Usage](#-cli-usage) - [Web UI](#-web-ui) - [Architecture](#-architecture)

</div>

---

## Features

| Feature | Description |
|---------|-------------|
| 4 Presentation Formats | Standard, Pecha Kucha (20x20), Lightning Talk, Keynote |
| 9 Slide Templates | Title, Agenda, Content, Data, Quote, Comparison, Timeline, Q&A, Closing |
| Speaker Notes | Conversational speaker notes for each slide |
| Visual Suggestions | AI-recommended charts, diagrams, and images per slide |
| Timing Estimates | Per-slide and total presentation timing with visual bar |
| Markdown Export | Clean markdown export for easy conversion |
| Dual Interface | Full CLI + Streamlit Web UI |
| YAML Configuration | Flexible config management |

## Architecture

`
39-presentation-generator/
├── src/
│   └── presentation_gen/
│       ├── __init__.py          # Package metadata
│       ├── core.py              # Business logic, formats, templates, timing
│       ├── cli.py               # Click CLI with subcommands
│       └── web_ui.py            # Streamlit web interface
├── tests/
│   ├── __init__.py
│   ├── test_core.py             # Core logic tests
│   └── test_cli.py              # CLI tests
├── config.yaml                  # Configuration
├── setup.py                     # Package setup
├── Makefile                     # Build commands
├── .env.example                 # Environment template
├── requirements.txt             # Dependencies
└── README.md                    # Documentation
`

## Installation

`bash
make install    # or: pip install -e .
make dev        # with dev dependencies
`

## CLI Usage

### Generate a Presentation

`bash
# Basic
presentation-gen generate --topic "Machine Learning 101"

# Full options
presentation-gen generate \
  --topic "Machine Learning 101" \
  --slides 15 \
  --audience "beginners" \
  --format keynote \
  --notes-only \
  -o slides.md
`

### List Formats and Templates

`bash
presentation-gen formats
presentation-gen slide-types
`

### Estimate Timing

`bash
presentation-gen timing --slides 20 --format pecha-kucha
`

## Web UI

`bash
make run-web
`

| Tab | Description |
|-----|-------------|
| Topic Input | Enter topic, audience, format, slide count |
| Slide Cards | Expandable slide cards with notes |
| Timing | Visual timing bar with per-slide estimates |
| Download | Download full presentation or notes only |

## Configuration

`yaml
llm:
  temperature: 0.7
  max_tokens: 4096
presentation:
  default_slides: 12
  words_per_minute: 130
`

## Testing

`bash
make test
`

## License

Part of the [90 Local LLM Projects](../../README.md) collection.
