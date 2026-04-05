![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![License](https://img.shields.io/badge/License-MIT-green)
![Version](https://img.shields.io/badge/Version-1.0.0-orange)
![LLM](https://img.shields.io/badge/Local%20LLM-Ollama-purple)
![PRs Welcome](https://img.shields.io/badge/PRs-Welcome-brightgreen)

# 📝 Quiz Generator

**Production-grade quiz generation powered by a local LLM.** Generate, take, score, and manage quizzes from any topic — all from your terminal or a Streamlit web UI.

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                      User Interfaces                    │
│                                                         │
│   ┌─────────────┐              ┌──────────────────┐     │
│   │  CLI (Click) │              │  Web UI (Streamlit)│   │
│   └──────┬──────┘              └────────┬─────────┘     │
│          │                              │               │
│          ▼                              ▼               │
│   ┌─────────────────────────────────────────────┐       │
│   │           Core Engine (core.py)             │       │
│   │  • Quiz generation   • Scoring              │       │
│   │  • Question bank     • Score tracker         │       │
│   │  • Export (JSON/MD)  • Timer                 │       │
│   │  • Config manager    • Validation            │       │
│   └──────────────────────┬──────────────────────┘       │
│                          │                              │
│                          ▼                              │
│              ┌───────────────────────┐                  │
│              │  Ollama Local LLM     │                  │
│              │  (Gemma 4 / Llama 3)  │                  │
│              └───────────────────────┘                  │
└─────────────────────────────────────────────────────────┘
```

---

## ✨ Features

### 🎯 Quiz Generation
- Generate quizzes on **any topic** using a local LLM
- **Multiple-choice**, **true/false**, **short-answer**, or **mixed** formats
- Three difficulty levels: **easy**, **medium**, **hard**
- Smart JSON parsing with code-fence handling

### 🖥️ Dual Interface
- **Rich CLI** with Click commands and beautiful terminal output
- **Streamlit Web UI** with interactive forms, charts, and downloads

### 📊 Scoring & History
- Interactive quiz mode with instant feedback
- **Score tracking** across sessions (persisted to JSON)
- Average score, best score, and trend charts

### ⏱️ Timed Quizzes
- Optional per-question timer
- Time tracking for each quiz attempt

### 🗂️ Question Bank
- Save questions from generated quizzes
- Filter by **topic**, **type**, or **difficulty**
- Persistent storage for reuse

### 📤 Export
- Export to **JSON** for integrations
- Export to **Markdown** (PDF-ready) for printing

### ⚙️ Configurable
- YAML-based configuration with sensible defaults
- Customise LLM parameters, timer settings, file paths, and more

---

## 🚀 Quick Start

```bash
# 1. Make sure Ollama is running
ollama serve

# 2. Install dependencies
pip install -r requirements.txt

# 3. Generate your first quiz
python -m quiz_gen.cli generate --topic "Python Programming" --questions 5

# 4. Or launch the web UI
streamlit run src/quiz_gen/web_ui.py
```

---

## 📦 Installation

### From requirements.txt

```bash
pip install -r requirements.txt
```

### Development mode (editable install)

```bash
pip install -e ".[dev]"
```

### Prerequisites

| Requirement | Version |
|-------------|---------|
| Python      | ≥ 3.10  |
| Ollama      | Latest  |
| LLM Model   | Gemma 4 / Llama 3 (configurable) |

---

## 💻 CLI Usage

The CLI is organised as a Click command group with four sub-commands.

### `generate` — Create a new quiz

```bash
# Basic generation
python -m quiz_gen.cli generate --topic "World War II" --questions 10

# With answers shown
python -m quiz_gen.cli generate -t "Biology" -q 5 --show-answers

# Specific type and difficulty
python -m quiz_gen.cli generate -t "Calculus" --type short-answer -d hard

# Save to file
python -m quiz_gen.cli generate -t "Chemistry" -q 15 --output quiz.json
```

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--topic` | `-t` | *required* | Quiz topic |
| `--questions` | `-q` | `5` | Number of questions |
| `--type` | | `multiple-choice` | `multiple-choice`, `true-false`, `short-answer`, `mixed` |
| `--difficulty` | `-d` | `medium` | `easy`, `medium`, `hard` |
| `--output` | `-o` | — | Save quiz to a JSON file |
| `--show-answers` | `-a` | `false` | Show answers inline |

### `take` — Take a quiz interactively

```bash
# Take a quiz from a saved file
python -m quiz_gen.cli take --file quiz.json

# Generate and take in one step
python -m quiz_gen.cli take --topic "Geography" --questions 10

# Enable timer
python -m quiz_gen.cli take --file quiz.json --timer
```

### `export` — Convert quiz to other formats

```bash
# Export to Markdown (PDF-ready)
python -m quiz_gen.cli export --input quiz.json --format markdown --output quiz.md

# Re-export as formatted JSON
python -m quiz_gen.cli export --input quiz.json --format json --output clean.json
```

### `bank` — Manage the question bank

```bash
# Add questions from a quiz file
python -m quiz_gen.cli bank add --file quiz.json

# List all questions
python -m quiz_gen.cli bank list

# Filter by topic
python -m quiz_gen.cli bank list --topic "Math"

# Clear the bank
python -m quiz_gen.cli bank clear
```

---

## 🌐 Web UI

The Streamlit-based web interface provides a visual, interactive experience.

```bash
streamlit run src/quiz_gen/web_ui.py
```

### Tabs

| Tab | Description |
|-----|-------------|
| **📝 Generate Quiz** | Set topic, type, difficulty — generate and view with expandable answers |
| **🎯 Take Quiz** | Interactive quiz with radio buttons / text input, timer, and scoring |
| **🗂️ Question Bank** | Browse, filter, and manage saved questions |
| **📊 Score History** | View past scores, averages, best scores, and trend chart |

### Sidebar Controls

- Topic input
- Number of questions slider
- Question type selector
- Difficulty slider
- Timer toggle
- Ollama status indicator

---

## ⚙️ Configuration

All settings live in `config.yaml` at the project root:

```yaml
llm:
  temperature: 0.7        # LLM creativity (0.0–1.0)
  max_tokens: 4096         # Max response length

quiz:
  default_num_questions: 5
  default_type: "multiple-choice"
  default_difficulty: "medium"
  max_questions: 50

timer:
  enabled: false
  default_seconds_per_question: 30

scoring:
  history_file: "quiz_scores.json"

question_bank:
  storage_file: "question_bank.json"

logging:
  level: "INFO"
  file: "quiz_gen.log"
```

---

## 🏗️ Project Structure

```
51-quiz-generator/
├── src/
│   └── quiz_gen/
│       ├── __init__.py        # Package init, version
│       ├── core.py            # Business logic, models, LLM integration
│       ├── cli.py             # Click CLI with generate/take/export/bank
│       └── web_ui.py          # Streamlit web interface
├── tests/
│   ├── __init__.py
│   ├── test_core.py           # Core module tests
│   └── test_cli.py            # CLI integration tests
├── config.yaml                # Application configuration
├── setup.py                   # Package setup
├── Makefile                   # Development shortcuts
├── requirements.txt           # Python dependencies
├── .env.example               # Environment variable template
└── README.md                  # This file
```

---

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/ -v --tb=short

# Run with coverage
python -m pytest tests/ -v --cov=quiz_gen --cov-report=term-missing

# Run only core tests
python -m pytest tests/test_core.py -v

# Run only CLI tests
python -m pytest tests/test_cli.py -v
```

Tests mock the LLM calls so they run **instantly** without Ollama.

---

## 📄 License

This project is licensed under the MIT License.
