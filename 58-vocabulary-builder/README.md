# 📖 Vocabulary Builder

![Python](https://img.shields.io/badge/Python-3.9+-blue?logo=python&logoColor=white)
![LLM](https://img.shields.io/badge/LLM-Ollama-orange?logo=meta&logoColor=white)
![Streamlit](https://img.shields.io/badge/UI-Streamlit-red?logo=streamlit&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)
![Tests](https://img.shields.io/badge/Tests-Passing-brightgreen?logo=pytest)

> 📚 **Build vocabulary with spaced repetition, etymology, word families, context sentences, and interactive quizzes — powered by a local LLM.**

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🧠 **Spaced Repetition** | SM-2 algorithm for optimal memory retention |
| 📝 **Context Sentences** | Multiple usage examples per word |
| 🏛️ **Etymology** | Word origins and historical development |
| 👨‍👩‍👧‍👦 **Word Families** | Related words and derivations |
| 📊 **Progress Stats** | Track mastery, quiz scores, and streaks |
| 🎯 **Quiz Mode** | Interactive vocabulary testing |
| 🃏 **Flashcards** | Card-based learning in the web UI |
| 🌐 **Streamlit Web UI** | Full-featured learning dashboard |
| 💻 **Rich CLI** | Terminal interface with color output |
| ⚙️ **YAML Config** | Centralized configuration management |

---

## 🏗️ Architecture

```
58-vocabulary-builder/
├── src/vocab_builder/
│   ├── __init__.py          # Package metadata
│   ├── core.py              # Business logic, spaced repetition, quiz engine
│   ├── cli.py               # Rich CLI with Click commands
│   └── web_ui.py            # Streamlit web interface
├── tests/
│   ├── test_core.py         # Core logic + spaced repetition tests
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
cd 58-vocabulary-builder
pip install -e ".[dev]"
ollama serve
```

---

## 💻 CLI Usage

```bash
# Generate vocabulary list
vocab-builder learn --topic "SAT words" --count 15

# With specific level
vocab-builder learn --topic "Medical terminology" --level advanced

# Quiz mode from saved file
vocab-builder quiz --file vocab_sat_words.json

# Save to custom file
vocab-builder learn --topic "GRE words" --output gre_vocab.json
```

---

## 🌐 Web UI

```bash
streamlit run src/vocab_builder/web_ui.py
```

Features:
- 📚 **Learn Mode** — Generate vocabulary with definitions, etymology, and mnemonics
- 🎯 **Quiz Mode** — Test knowledge with instant scoring
- 🃏 **Word Cards** — Flashcard view with reveal animations
- 📊 **Progress Dashboard** — Track scores and learning progress over time

---

## 🧪 Testing

```bash
pytest tests/ -v
pytest tests/ -v --cov=src/vocab_builder --cov-report=term-missing
```

---

## ⚙️ Configuration

Edit `config.yaml` to customize spaced repetition parameters, quiz settings, and LLM configuration.

---

## 📝 License

MIT
