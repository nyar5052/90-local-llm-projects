<div align="center">

# 📰 Newsletter Editor

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Powered by Ollama](https://img.shields.io/badge/LLM-Ollama-green.svg)](https://ollama.ai/)

**Transform raw notes and content into polished, professional newsletters with AI-powered editing.**

[Features](#-features) • [Installation](#-installation) • [CLI Usage](#-cli-usage) • [Web UI](#-web-ui) • [Architecture](#-architecture) • [Configuration](#-configuration)

</div>

---

## 🌟 Features

| Feature | Description |
|---------|-------------|
| 📝 **Smart Content Curation** | AI transforms raw notes into polished newsletter sections |
| 📋 **Section Templates** | 6 built-in templates: News Roundup, Deep Dive, Tips & Tricks, Spotlight, Events, Q&A |
| 👥 **Subscriber Segmentation** | Target content for All, New, Premium, or Inactive subscribers |
| 🗄️ **Archive Management** | Automatic archiving with browsable history |
| 🌐 **HTML Export** | Professional styled HTML output for email delivery |
| 🎨 **Multiple Tones** | Informative, casual, witty, formal, or friendly writing styles |
| 💻 **Dual Interface** | Full CLI + Streamlit Web UI |
| ⚙️ **YAML Configuration** | Flexible config management |
| 📊 **Rich Terminal UI** | Beautiful CLI output with Rich library |

## 🏗️ Architecture

```
36-newsletter-editor/
├── src/
│   └── newsletter_editor/
│       ├── __init__.py          # Package metadata
│       ├── core.py              # Business logic, templates, segmentation
│       ├── cli.py               # Click CLI with subcommands
│       └── web_ui.py            # Streamlit web interface
├── tests/
│   ├── __init__.py
│   ├── test_core.py             # Core logic tests
│   └── test_cli.py              # CLI integration tests
├── config.yaml                  # Configuration file
├── setup.py                     # Package setup
├── Makefile                     # Build & run commands
├── .env.example                 # Environment template
├── requirements.txt             # Dependencies
└── README.md                    # This file
```

## 📦 Installation

### Prerequisites

- Python 3.10+
- [Ollama](https://ollama.ai/) running locally with a model pulled

### Quick Start

```bash
# Install the package
make install

# Or install with dev dependencies
make dev

# Or manual install
pip install -e .
```

## 🖥️ CLI Usage

The CLI provides subcommands for all functionality:

### Generate a Newsletter

```bash
# Basic generation
newsletter-editor generate --input notes.txt --name "Tech Weekly"

# With template and segment
newsletter-editor generate \
  --input notes.txt \
  --name "Tech Weekly" \
  --sections 6 \
  --tone witty \
  --template deep_dive \
  --segment premium \
  --html \
  -o output.md

# Without archiving
newsletter-editor generate --input notes.txt --name "Quick Update" --no-archive
```

### List Templates

```bash
newsletter-editor templates
```

### List Subscriber Segments

```bash
newsletter-editor segments
```

### Browse Archive

```bash
newsletter-editor archive
```

### Global Options

```bash
newsletter-editor --config custom-config.yaml --verbose generate ...
```

### Input File Format

Create a text file with your raw notes:
```
AI news: GPT-5 released with major improvements
New NVIDIA chip boosts training 2x
Python 3.13 out with performance gains
React 19 now stable - new hooks API
https://example.com/ai-news
```

## 🌐 Web UI

Launch the interactive Streamlit interface:

```bash
make run-web
# or
streamlit run src/newsletter_editor/web_ui.py
```

### Web UI Features

| Tab | Description |
|-----|-------------|
| ✍️ **Section Builder** | Input content, configure settings, generate newsletter |
| 👁️ **Preview** | Live rendered preview of your newsletter |
| 📋 **Template Selector** | Browse and learn about section templates |
| 📤 **Export** | Download as Markdown/HTML, manage archive |

## ⚙️ Configuration

Edit `config.yaml` to customize behavior:

```yaml
llm:
  temperature: 0.7        # Creativity level (0.0-1.0)
  max_tokens: 4096         # Max output length

newsletter:
  default_sections: 4
  default_tone: "informative"
  supported_tones:
    - informative
    - casual
    - witty
    - formal
    - friendly

export:
  output_dir: "output"
  archive_dir: "archive"
```

## 🧪 Testing

```bash
# Run all tests
make test

# With coverage
python -m pytest tests/ -v --cov=newsletter_editor
```

## 🔧 Development

```bash
# Install dev dependencies
make dev

# Run linting
make lint

# Clean build artifacts
make clean
```

## 📄 License

This project is part of the [90 Local LLM Projects](../../README.md) collection.
