# 📚 Reading Comprehension Builder

![Python](https://img.shields.io/badge/Python-3.9+-blue?logo=python&logoColor=white)
![LLM](https://img.shields.io/badge/LLM-Ollama-orange?logo=meta&logoColor=white)
![Streamlit](https://img.shields.io/badge/UI-Streamlit-red?logo=streamlit&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)
![Tests](https://img.shields.io/badge/Tests-Passing-brightgreen?logo=pytest)

> 📖 **Create reading comprehension exercises with difficulty calibration, scoring rubrics, passage annotations, and answer keys — powered by a local LLM.**

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 📖 **AI-Generated Passages** | Custom reading passages on any topic |
| 🎯 **Difficulty Calibration** | Elementary → middle school → high school → college |
| 📋 **Answer Key with Explanations** | Detailed explanations for every question |
| 📝 **Passage Annotations** | Relevant passage references for each question |
| 🏆 **Scoring Rubric** | 4-level rubric: Excellent, Good, Fair, Needs Improvement |
| ❓ **Multiple Question Types** | Factual, inferential, analytical, vocabulary, main-idea |
| 🌐 **Streamlit Web UI** | Interactive exercise and scoring dashboard |
| 💻 **Rich CLI** | Terminal interface with interactive mode |
| ⚙️ **YAML Config** | Centralized configuration management |

---

## 🏗️ Architecture

```
60-reading-comprehension-builder/
├── src/reading_comp/
│   ├── __init__.py          # Package metadata
│   ├── core.py              # Business logic, scoring, difficulty calibration
│   ├── cli.py               # Rich CLI with Click commands
│   └── web_ui.py            # Streamlit web interface
├── tests/
│   ├── test_core.py         # Core logic + scoring tests
│   └── test_cli.py          # CLI integration tests
├── config.yaml              # Application configuration
├── setup.py                 # Package installation
├── Makefile                 # Common development tasks
├── .env.example             # Environment variable template
├── requirements.txt         # Python dependencies
└── README.md                # This file
```

---

## 🚀 Installation

```bash
cd 60-reading-comprehension-builder
pip install -e ".[dev]"
ollama serve
```

---

## 💻 CLI Usage

```bash
# Generate an exercise
reading-comp generate --topic "Climate Change" --level "high school" --questions 5

# Interactive mode (answer & get scored)
reading-comp generate --topic "Space Exploration" --interactive

# Show answers immediately
reading-comp generate --topic "Ancient Egypt" --level "middle school" --show-answers

# View answer key from saved file
reading-comp answer-key --file exercise.json

# Save to file
reading-comp generate --topic "Marine Biology" --output exercise.json
```

---

## 🌐 Web UI

```bash
streamlit run src/reading_comp/web_ui.py
```

Features:
- 📝 **Topic/Text Input** — Enter any topic or custom passage
- 📖 **Passage Display** — Clean reading view with vocabulary highlights
- ❓ **Interactive Questions** — Select answers with dropdown menus
- 📊 **Score Dashboard** — Instant scoring with detailed feedback and rubric

---

## 🧪 Testing

```bash
pytest tests/ -v
pytest tests/ -v --cov=src/reading_comp --cov-report=term-missing
```

---

## ⚙️ Configuration

Edit `config.yaml` to customize reading levels, passage lengths, scoring thresholds, and LLM settings.

---

## 📝 License

MIT
