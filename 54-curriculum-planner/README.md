# 📚 Curriculum Planner

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)](#-testing)

> **Production-grade AI-powered curriculum design** with learning outcome mapping,
> assessment planning, prerequisite tracking, and Bloom's taxonomy integration.

Design comprehensive course curricula from a topic and duration using a local LLM
(Ollama). Get structured weekly breakdowns, resource recommendations, outcome
matrices, and balanced assessment schedules — all from the command line or a
Streamlit web interface.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Curriculum Planner                     │
├──────────────┬──────────────┬───────────────────────────┤
│   CLI (Click) │  Web UI      │  Python API               │
│   cli.py      │  (Streamlit) │  core.py                  │
│               │  web_ui.py   │                           │
├──────────────┴──────────────┴───────────────────────────┤
│                    Core Engine                           │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────────┐ │
│  │ OutcomeMapper│ │ Assessment   │ │ Resource         │ │
│  │              │ │ Planner      │ │ Suggester        │ │
│  └──────────────┘ └──────────────┘ └──────────────────┘ │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────────┐ │
│  │ Prerequisite │ │ Config       │ │ Export           │ │
│  │ Tracker      │ │ Manager      │ │ (JSON/Markdown)  │ │
│  └──────────────┘ └──────────────┘ └──────────────────┘ │
├─────────────────────────────────────────────────────────┤
│              LLM Client (Ollama / Gemma)                │
└─────────────────────────────────────────────────────────┘
```

---

## ✨ Features

- **🤖 AI-Powered Design** — Generate complete curricula from a topic, duration, and level
- **🎯 Learning Outcome Mapping** — Map outcomes to weeks with coverage analysis
- **📊 Assessment Planning** — Balanced assessment schedules with weight normalization
- **📖 Resource Suggestions** — AI-curated resources categorized by type
- **📋 Prerequisite Tracking** — Dependency trees with required/optional classification
- **🧠 Bloom's Taxonomy** — Six cognitive levels (Remember → Create) for outcome classification
- **📅 Weekly Breakdowns** — Detailed topics, activities, and assessments per week
- **💾 Multi-format Export** — JSON and Markdown output
- **🌐 Web Interface** — Interactive Streamlit UI with tabs, charts, and filters
- **⚙️ Configurable** — YAML-based configuration for all settings
- **✅ Fully Tested** — Comprehensive test suite with mocked LLM calls

---

## 🚀 Quick Start

```bash
# 1. Clone and navigate to the project
cd 54-curriculum-planner

# 2. Install dependencies
pip install -r requirements.txt

# 3. Ensure Ollama is running
ollama serve

# 4. Design a curriculum
python -m src.curriculum_planner.cli design --course "Intro to Machine Learning" --weeks 12

# 5. Or launch the web UI
streamlit run src/curriculum_planner/web_ui.py
```

---

## 📦 Installation

### From source

```bash
# Production install
pip install -r requirements.txt

# Development install (includes testing and linting tools)
pip install -e ".[dev]"
```

### Prerequisites

| Requirement | Version | Purpose |
|-------------|---------|---------|
| Python | 3.10+ | Runtime |
| [Ollama](https://ollama.ai/) | Latest | Local LLM inference |
| Gemma model | 4b+ | Default LLM model |

```bash
# Install and start Ollama, then pull a model
ollama serve
ollama pull gemma3:4b
```

---

## 💻 CLI Usage

The CLI uses Click with a command group. All commands are accessed through subcommands:

### Design a curriculum

```bash
# Basic usage
python -m src.curriculum_planner.cli design --course "Web Development" --weeks 8

# With level and focus areas
python -m src.curriculum_planner.cli design \
  --course "Data Science" \
  --weeks 16 \
  --level advanced \
  --focus "deep learning, NLP, computer vision"

# Save output to file
python -m src.curriculum_planner.cli design \
  --course "Python Programming" \
  --weeks 12 \
  --output curriculum.json

# Export as Markdown
python -m src.curriculum_planner.cli design \
  --course "DevOps" \
  --weeks 10 \
  --output curriculum.md
```

### Manage learning outcomes

```bash
# List all outcomes
python -m src.curriculum_planner.cli outcomes --curriculum-file curriculum.json list

# Show outcome-week mapping matrix
python -m src.curriculum_planner.cli outcomes --curriculum-file curriculum.json map

# Check for uncovered outcomes
python -m src.curriculum_planner.cli outcomes --curriculum-file curriculum.json check
```

### Suggest resources

```bash
python -m src.curriculum_planner.cli resources --course "Machine Learning"
```

### Export to different formats

```bash
# Export to Markdown
python -m src.curriculum_planner.cli export --input curriculum.json --format markdown

# Export to JSON with custom output path
python -m src.curriculum_planner.cli export --input curriculum.json --format json --output output.json
```

### View prerequisite tree

```bash
python -m src.curriculum_planner.cli prerequisites --curriculum-file curriculum.json
```

### CLI Options Reference

| Command | Option | Short | Description |
|---------|--------|-------|-------------|
| `design` | `--course` | `-c` | Course name (required) |
| `design` | `--weeks` | `-w` | Duration in weeks (default: 12) |
| `design` | `--level` | `-l` | beginner / intermediate / advanced |
| `design` | `--focus` | `-f` | Focus areas (comma-separated) |
| `design` | `--output` | `-o` | Output file path (.json or .md) |
| `outcomes` | `--curriculum-file` | `-f` | Path to curriculum JSON |
| `resources` | `--course` | `-c` | Topic for resource suggestions |
| `export` | `--input` | `-i` | Input curriculum JSON file |
| `export` | `--format` | `-f` | Output format (json/markdown) |
| `prerequisites` | `--curriculum-file` | `-f` | Path to curriculum JSON |

---

## 🌐 Web UI

Launch the interactive Streamlit interface:

```bash
streamlit run src/curriculum_planner/web_ui.py
```

### Tabs

| Tab | Description |
|-----|-------------|
| **📋 Course Design** | Overview with metrics, objectives, prerequisites, and export buttons |
| **📅 Weekly Breakdown** | Expandable weeks with topics, activities, and assessments |
| **🎯 Outcome Matrix** | Interactive table mapping outcomes to weeks with coverage analysis |
| **📖 Resources** | Categorized resource list with type filters |
| **📊 Assessment Plan** | Calendar view and weight distribution bar chart |

### Features

- **Sidebar form** for course configuration (name, weeks, level, focus)
- **Real-time Ollama status** indicator
- **Upload existing curricula** (JSON) for viewing and analysis
- **Download buttons** for JSON and Markdown export

---

## 🎯 Learning Outcomes

The system supports Bloom's taxonomy levels for classifying learning outcomes:

| Level | Description | Example Verbs |
|-------|-------------|---------------|
| **Remember** | Recall facts and basic concepts | define, list, identify |
| **Understand** | Explain ideas or concepts | describe, explain, summarize |
| **Apply** | Use information in new situations | implement, solve, demonstrate |
| **Analyze** | Draw connections among ideas | compare, contrast, examine |
| **Evaluate** | Justify a decision or course of action | critique, assess, judge |
| **Create** | Produce new or original work | design, develop, construct |

### Outcome Mapping

The `OutcomeMapper` class provides:

- **`map_outcomes_to_weeks()`** — Maps each outcome to the weeks where it is addressed
- **`generate_outcome_matrix()`** — 2D matrix showing outcomes vs. weeks (X marks coverage)
- **`check_coverage()`** — Identifies outcomes not covered by any week

---

## 📊 Assessment Planning

The `AssessmentPlanner` automatically creates balanced assessment schedules:

- **Automatic scheduling** — Distributes assessments evenly across weeks
- **Weight normalization** — Ensures all assessment weights sum to 100%
- **Calendar view** — Chronological assessment timeline
- **Type variety** — Cycles through quizzes, assignments, projects, and exams

### Default Assessment Weights

| Type | Weight |
|------|--------|
| Quizzes | 20% |
| Assignments | 30% |
| Project | 30% |
| Exam | 20% |

---

## ⚙️ Configuration

All settings are managed via `config.yaml`:

```yaml
llm:
  temperature: 0.7        # LLM creativity (0.0-1.0)
  max_tokens: 8192         # Maximum response length

curriculum:
  default_weeks: 12        # Default course duration
  default_level: beginner  # Default difficulty level
  max_weeks: 52            # Maximum allowed weeks

assessment:
  default_weights:         # Assessment weight distribution
    quizzes: 20
    assignments: 30
    project: 30
    exam: 20

storage:
  output_dir: "./curricula"

logging:
  level: INFO
  file: curriculum_planner.log
```

---

## 🏗️ Project Structure

```
54-curriculum-planner/
├── src/
│   └── curriculum_planner/
│       ├── __init__.py        # Package metadata and version
│       ├── core.py            # Business logic, dataclasses, LLM integration
│       ├── cli.py             # Click CLI with command groups
│       └── web_ui.py          # Streamlit web interface
├── tests/
│   ├── __init__.py
│   ├── test_core.py           # Core logic tests (30+ tests)
│   └── test_cli.py            # CLI integration tests
├── config.yaml                # Application configuration
├── setup.py                   # Package setup with entry points
├── requirements.txt           # Python dependencies
├── Makefile                   # Development workflow targets
├── .env.example               # Environment variable template
└── README.md                  # This file
```

---

## 🧪 Testing

Run the full test suite:

```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ -v --cov=src/curriculum_planner --cov-report=term-missing

# Run specific test file
python -m pytest tests/test_core.py -v

# Run specific test
python -m pytest tests/test_core.py::test_generate_curriculum_parses_json -v
```

### Test Coverage

| Module | Tests | Description |
|--------|-------|-------------|
| `test_core.py` | 25+ | Dataclasses, OutcomeMapper, AssessmentPlanner, validation, export |
| `test_cli.py` | 5+ | CLI commands, output, error handling |

All LLM calls are mocked — no running Ollama instance needed for testing.

---

## 📄 License

MIT License. See [LICENSE](LICENSE) for details.
