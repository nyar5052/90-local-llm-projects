# 📝 Essay Grader

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)]()

**Production-grade essay grading with multi-rubric support, inline annotations, plagiarism indicators, and analytics — powered by a local LLM (Ollama).**

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Essay Grader                        │
├──────────┬───────────────┬──────────────────────────────┤
│  CLI     │  Streamlit UI │  Python API                  │
│ (click)  │  (web_ui.py)  │  (import core)               │
├──────────┴───────────────┴──────────────────────────────┤
│                    Core Engine                          │
│  • Multi-rubric grading    • Inline annotations         │
│  • Plagiarism indicators   • Grade distribution         │
│  • Export (JSON/Markdown)  • Batch grading              │
├─────────────────────────────────────────────────────────┤
│                  LLM Client (Ollama)                    │
│              common/llm_client.py                       │
└─────────────────────────────────────────────────────────┘
```

## ✨ Features

| Feature | Description |
|---------|-------------|
| **Multi-rubric grading** | 5 built-in rubric presets + custom rubric builder |
| **Inline annotations** | LLM-generated feedback pinned to specific essay passages |
| **Plagiarism indicators** | Detects suspicious writing-style shifts and generic passages |
| **Grade distribution** | Statistical tracking (mean, median, std) across essays |
| **Batch grading** | Grade an entire directory of essays in one command |
| **Dual interface** | Rich CLI + interactive Streamlit web UI |
| **Export reports** | JSON and Markdown report generation |
| **Grade history** | Track and compare grades over time |
| **Analytics dashboard** | Visualize score distributions and criterion averages |
| **Configurable** | YAML-based configuration for all settings |

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Make sure Ollama is running
ollama serve

# 3. Grade an essay
python -m src.essay_grader.cli grade --essay my_essay.txt

# 4. Or launch the web UI
streamlit run src/essay_grader/web_ui.py
```

## 📦 Installation

### Prerequisites

- **Python 3.10+**
- **[Ollama](https://ollama.ai/)** running locally with a supported model (e.g. Gemma 4)

### From Source

```bash
git clone <repo-url>
cd 53-essay-grader

# Production install
pip install -r requirements.txt

# Development install (includes test & lint tools)
pip install -r requirements.txt
pip install pytest pytest-cov ruff

# Or use Make
make install    # production
make dev        # development
```

### As a Package

```bash
pip install -e .
essay-grader grade --essay paper.txt
```

## 💻 CLI Usage

The CLI provides four commands: `grade`, `rubrics`, `report`, and `batch`.

### Grade an Essay

```bash
# Default rubric (academic)
python -m src.essay_grader.cli grade --essay essay.txt

# Preset rubric
python -m src.essay_grader.cli grade --essay essay.txt --rubric argumentative

# Custom criteria (comma-separated)
python -m src.essay_grader.cli grade --essay essay.txt --rubric "thesis,evidence,style"

# With assignment context
python -m src.essay_grader.cli grade --essay essay.txt --context "Compare and contrast WWII"

# Save results to file
python -m src.essay_grader.cli grade --essay essay.txt --output grade.json

# With inline annotations
python -m src.essay_grader.cli grade --essay essay.txt --annotate

# Markdown report
python -m src.essay_grader.cli grade --essay essay.txt --output report.md
```

### List Rubric Presets

```bash
python -m src.essay_grader.cli rubrics
```

### Generate Report from Existing Grades

```bash
# Convert JSON grades to Markdown report
python -m src.essay_grader.cli report --input grade.json --format markdown

# Custom output path
python -m src.essay_grader.cli report --input grade.json --format markdown --output my_report.md
```

### Batch Grade Essays

```bash
# Grade all .txt/.md files in a directory
python -m src.essay_grader.cli batch --directory ./essays/

# With a specific rubric and output directory
python -m src.essay_grader.cli batch --directory ./essays/ --rubric research_paper --output-dir ./results/
```

### CLI Options Reference

| Command | Option | Short | Description |
|---------|--------|-------|-------------|
| `grade` | `--essay` | `-e` | Path to essay text file (required) |
| `grade` | `--rubric` | `-r` | Preset name or comma-separated criteria |
| `grade` | `--context` | `-c` | Assignment context / prompt |
| `grade` | `--output` | `-o` | Save results to file (.json or .md) |
| `grade` | `--annotate` | | Include inline annotations |
| `rubrics` | | | No options — lists all presets |
| `report` | `--input` | `-i` | Grade JSON file to convert |
| `report` | `--format` | `-f` | Output format: `markdown` or `json` |
| `report` | `--output` | `-o` | Output file path |
| `batch` | `--directory` | `-d` | Directory with essay files |
| `batch` | `--rubric` | `-r` | Rubric preset or custom criteria |
| `batch` | `--output-dir` | `-o` | Output directory for reports |

## 🌐 Web UI

Launch the interactive Streamlit dashboard:

```bash
streamlit run src/essay_grader/web_ui.py
```

### Features

- **Grade Essay** — Paste text or upload a file, select a rubric, view detailed results with score breakdown, annotated feedback, and downloadable reports.
- **Rubric Builder** — Create custom rubrics with named criteria, weights, and descriptions.
- **Grade History** — Browse past grading sessions and compare scores.
- **Analytics** — View grade distribution charts, criterion averages, and improvement trends.

## 📊 Rubric Presets

| Preset | Criteria |
|--------|----------|
| `academic` | Thesis, Evidence, Analysis, Organization, Grammar |
| `creative_writing` | Voice, Imagery, Plot Structure, Character Development, Originality |
| `argumentative` | Claim, Reasoning, Counter Arguments, Evidence, Persuasion |
| `narrative` | Storytelling, Reflection, Descriptive Language, Structure, Mechanics |
| `research_paper` | Research Question, Literature Review, Methodology, Analysis, Citations, Writing Quality |

Each criterion has a configurable weight and max score. Use `essay-grader rubrics` to see full details.

## ⚙️ Configuration

All settings are in `config.yaml`:

```yaml
llm:
  temperature: 0.3       # LLM sampling temperature
  max_tokens: 4096        # Max response tokens

grading:
  default_rubric: "academic"
  max_essay_length: 50000
  annotation_enabled: true

grade_scale:              # Score → letter mapping
  "A+": 9.5
  "A": 9.0
  ...

plagiarism:
  enabled: true
  threshold: 0.7

storage:
  history_file: "grade_history.json"
  reports_dir: "./reports"

logging:
  level: "INFO"
  file: "essay_grader.log"
```

Environment variables can also be set via `.env` (see `.env.example`).

## 🏗️ Project Structure

```
53-essay-grader/
├── src/
│   └── essay_grader/
│       ├── __init__.py          # Package metadata & version
│       ├── core.py              # Business logic, rubrics, grading engine
│       ├── cli.py               # Click CLI (grade, rubrics, report, batch)
│       └── web_ui.py            # Streamlit web interface
├── tests/
│   ├── __init__.py
│   ├── test_core.py             # Core logic tests
│   └── test_cli.py              # CLI integration tests
├── config.yaml                  # Application configuration
├── requirements.txt             # Python dependencies
├── setup.py                     # Package setup
├── Makefile                     # Development shortcuts
├── .env.example                 # Environment variable template
└── README.md                    # This file
```

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/ -v

# With coverage
python -m pytest tests/ -v --cov=src/essay_grader --cov-report=term-missing

# Run specific test file
python -m pytest tests/test_core.py -v

# Using Make
make test
```

### Test Coverage

- **test_core.py** — Unit tests for grading logic, rubrics, grade distribution, validation, and export.
- **test_cli.py** — Integration tests for all CLI commands, including error handling.

## 📝 Example Output

```
╭──────────── Essay Grade ────────────╮
│  Overall Score: 7.5/10 (B+)        │
╰─────────────────────────────────────╯

┌──────────────┬───────┬──────────────────────────┐
│ Criterion    │ Score │ Feedback                 │
├──────────────┼───────┼──────────────────────────┤
│ Thesis       │ 8/10  │ Clear and well-defined   │
│ Evidence     │ 7/10  │ Good use of sources      │
│ Analysis     │ 7/10  │ Adequate depth           │
│ Organization │ 8/10  │ Logical flow             │
│ Grammar      │ 8/10  │ Minor errors only        │
└──────────────┴───────┴──────────────────────────┘

✓ Strengths:
  • Clear thesis statement
  • Good use of transitions

✗ Weaknesses:
  • Needs more evidence in paragraph 3

💡 Suggestions:
  • Add more primary sources
  • Strengthen conclusion
```

## 📄 License

MIT License. See [LICENSE](LICENSE) for details.
