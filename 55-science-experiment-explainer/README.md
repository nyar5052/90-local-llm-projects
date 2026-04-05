# 🔬 Science Experiment Explainer

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

> **Production-grade** science experiment explainer powered by a local LLM (Ollama).
> Get step-by-step guides with safety warnings, equipment lists, cost estimates,
> difficulty ratings, and alternative experiments — all from a single prompt.

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────┐
│                    User Interface                     │
│  ┌──────────────┐           ┌──────────────────────┐ │
│  │   CLI (Click) │           │  Web UI (Streamlit)  │ │
│  └──────┬───────┘           └──────────┬───────────┘ │
│         │                              │              │
│  ┌──────▼──────────────────────────────▼───────────┐ │
│  │                 Core Engine                      │ │
│  │  ┌──────────┐ ┌───────────┐ ┌────────────────┐  │ │
│  │  │  Safety   │ │ Equipment │ │   Experiment   │  │ │
│  │  │ Database  │ │  Manager  │ │   Explainer    │  │ │
│  │  └──────────┘ └───────────┘ └───────┬────────┘  │ │
│  └─────────────────────────────────────┼───────────┘ │
│                                        │              │
│  ┌─────────────────────────────────────▼───────────┐ │
│  │              LLM Client (Ollama)                 │ │
│  └──────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────┘
```

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🛡️ **Safety Database** | Built-in chemical/material safety rules with severity levels |
| 🔧 **Equipment Lists** | Automatic equipment detection with household alternatives |
| 💰 **Cost Estimates** | Estimated costs for equipment and materials |
| 📊 **Expected Results** | Clear descriptions of what should happen |
| ⭐ **Difficulty Ratings** | Beginner → Expert rating system |
| 🔄 **Alternative Experiments** | LLM-powered suggestions for related experiments |
| 📋 **Step-by-Step Guides** | Numbered procedures with tips and safety notes |
| 🧾 **Materials Checklists** | Printable shopping lists and checklists |
| 📤 **Multiple Export Formats** | JSON, Markdown, and Checklist output |
| 🌐 **Web UI** | Interactive Streamlit dashboard |
| 💻 **CLI** | Full-featured command-line interface |
| 🔍 **Experiment Search** | Search by topic, subject, or difficulty |

## 🚀 Quick Start

```bash
# 1. Make sure Ollama is running
ollama serve

# 2. Pull a model (if not already done)
ollama pull llama3

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run your first experiment explanation
python -m src.science_explainer.cli explain -e "baking soda volcano"
```

## 📦 Installation

### Prerequisites

- **Python 3.10+**
- **[Ollama](https://ollama.ai/)** running locally with a supported model

### Install from source

```bash
git clone <repo-url>
cd 55-science-experiment-explainer

# Production install
pip install -r requirements.txt

# Development install (includes testing & linting tools)
pip install -r requirements.txt
pip install pytest pytest-cov ruff

# Or use the Makefile
make install   # production
make dev       # development
```

### Editable install

```bash
pip install -e .
```

After editable install the `science-explainer` command is available globally.

## 💻 CLI Usage

The CLI is organized as a Click command group with several sub-commands.

### Explain an experiment

```bash
# Basic usage
science-explainer explain -e "baking soda volcano"

# Specify grade level & detail
science-explainer explain -e "electrolysis of water" -l "high school" -d detailed

# Save to file
science-explainer explain -e "plant growth" -o experiment.json
```

### Search experiments

```bash
# By topic
science-explainer search -t "chemical reactions"

# By subject and difficulty
science-explainer search -s "Physics" -d "Intermediate"
```

### Safety lookup

```bash
# Check safety info for a material
science-explainer safety -e "hydrogen peroxide"
science-explainer safety -e "hydrochloric acid"
```

### Equipment info

```bash
# Get alternatives for equipment
science-explainer equipment -e "beaker"
science-explainer equipment -e "microscope"
```

### Alternative experiments

```bash
science-explainer alternatives -e "baking soda volcano" -l "middle school"
```

### Export experiment

```bash
# Export to markdown
science-explainer export -i experiment.json -f markdown -o experiment.md

# Export to checklist
science-explainer export -i experiment.json -f checklist -o checklist.txt
```

### CLI Options Reference

| Command | Option | Short | Description |
|---------|--------|-------|-------------|
| `explain` | `--experiment` | `-e` | Experiment name (required) |
| | `--level` | `-l` | Grade level (default: middle school) |
| | `--detail` | `-d` | brief / medium / detailed |
| | `--output` | `-o` | Save to JSON file |
| `search` | `--topic` | `-t` | Topic keyword |
| | `--subject` | `-s` | Subject area |
| | `--difficulty` | `-d` | Difficulty level |
| `safety` | `--experiment` | `-e` | Material or experiment name |
| `equipment` | `--experiment` | `-e` | Equipment item name |
| `alternatives` | `--experiment` | `-e` | Experiment name |
| | `--level` | `-l` | Grade level |
| `export` | `--input` | `-i` | Input JSON file |
| | `--format` | `-f` | json / markdown / checklist |
| | `--output` | `-o` | Output file path |

## 🌐 Web UI

Launch the interactive Streamlit dashboard:

```bash
streamlit run src/science_explainer/web_ui.py
# or
make run-web
```

### Web UI Tabs

| Tab | Features |
|-----|----------|
| **🔬 Explore Experiment** | Enter experiment name, generate full explanation, search experiments |
| **📋 Step-by-Step Guide** | Interactive checklist with progress tracking, tips per step |
| **🛡️ Safety Center** | Risk levels with color coding (🟢🟡🟠🔴), PPE checklist, age check |
| **📦 Materials & Equipment** | Materials checklist, equipment alternatives, cost estimates, shopping list |

### Sidebar Controls

- **Subject** filter dropdown
- **Grade Level** selector
- **Difficulty** slider (Beginner → Expert)

## 🛡️ Safety Features

Safety is a first-class concern in this tool.

### Built-in Safety Database

The `SafetyDatabase` class contains curated safety information for common lab materials:

| Material | Risk Level | Required PPE |
|----------|-----------|--------------|
| Vinegar | 🟢 Low | Safety goggles |
| Hydrogen Peroxide | 🟡 Medium | Goggles, gloves |
| Ethanol | 🟡 Medium | Goggles, fire extinguisher |
| Dry Ice | 🟡 Medium | Insulated gloves, goggles |
| Hydrochloric Acid | 🟠 High | Full PPE, fume hood |
| Sodium Hydroxide | 🟠 High | Full PPE |
| Magnesium Ribbon | 🟠 High | Goggles, tongs |
| Potassium Permanganate | 🟠 High | Goggles, gloves, lab coat |

### Age Appropriateness

Certain materials are restricted by grade level:
- **Hydrochloric acid**, **Sodium hydroxide**, **Potassium permanganate**, **Magnesium ribbon** → High school+
- **Ethanol** → Middle school+

### Automatic PPE Detection

The system scans experiment materials and compiles the required personal protective equipment list.

## 🧪 Experiment Database

### Equipment Manager

The `EquipmentManager` provides:
- **14+ lab equipment items** with descriptions
- **Household alternatives** for each item (e.g., beaker → mason jar)
- **Cost estimates** in USD
- **Substitute suggestions** for budget-friendly experiments

### Export Formats

| Format | Description | Extension |
|--------|-------------|-----------|
| JSON | Machine-readable, re-importable | `.json` |
| Markdown | Human-readable documentation | `.md` |
| Checklist | Printable checklist with checkboxes | `.txt` |

## ⚙️ Configuration

Configuration is managed via `config.yaml`:

```yaml
llm:
  temperature: 0.5
  max_tokens: 4096

experiment:
  default_level: "middle school"
  default_detail: "medium"

safety:
  require_adult_supervision_below: "high school"
  mandatory_ppe:
    - safety goggles
    - lab coat

equipment:
  show_cost_estimates: true
  currency: "USD"
```

Environment variables (see `.env.example`):

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_HOST` | `http://localhost:11434` | Ollama server URL |
| `OLLAMA_MODEL` | `llama3` | Model to use |
| `LOG_LEVEL` | `INFO` | Logging verbosity |
| `EXPERIMENTS_DIR` | `./experiments` | Saved experiments directory |

## 🏗️ Project Structure

```
55-science-experiment-explainer/
├── src/
│   └── science_explainer/
│       ├── __init__.py         # Package metadata & version
│       ├── core.py             # Business logic, safety DB, equipment mgr
│       ├── cli.py              # Click CLI interface
│       └── web_ui.py           # Streamlit web dashboard
├── tests/
│   ├── __init__.py
│   ├── test_core.py            # Core logic unit tests
│   └── test_cli.py             # CLI integration tests
├── config.yaml                 # Application configuration
├── setup.py                    # Package setup / entry points
├── requirements.txt            # Python dependencies
├── Makefile                    # Build & run targets
├── .env.example                # Environment variable template
└── README.md                   # This file
```

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# With coverage
pytest tests/ -v --cov=src/science_explainer --cov-report=term-missing

# Run specific test file
pytest tests/test_core.py -v
pytest tests/test_cli.py -v

# Using Makefile
make test
```

### Test Coverage

| Module | Tests |
|--------|-------|
| `core.py` | Experiment parsing, safety DB, equipment manager, validation, export |
| `cli.py` | CLI commands, output saving, error handling |

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.
