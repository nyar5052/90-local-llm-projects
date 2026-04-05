# 🎙️ Debate Topic Generator

![Python](https://img.shields.io/badge/Python-3.9+-blue?logo=python&logoColor=white)
![LLM](https://img.shields.io/badge/LLM-Ollama-orange?logo=meta&logoColor=white)
![Streamlit](https://img.shields.io/badge/UI-Streamlit-red?logo=streamlit&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)
![Tests](https://img.shields.io/badge/Tests-Passing-brightgreen?logo=pytest)

> ⚔️ **Generate debate topics with evidence-rated arguments, counterargument pairs, moderator guides, and judging criteria — powered by a local LLM.**

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| ⚖️ **Balanced Arguments** | Pro and con sides with detailed evidence |
| 📊 **Evidence Strength Rating** | Weak/moderate/strong ratings for every argument |
| ⚔️ **Counterargument Pairs** | Matched argument → counter → rebuttal chains |
| 📋 **Moderator Guide** | Opening statements, time allocation, closing instructions |
| 🏆 **Judging Criteria** | Weighted evaluation rubric for debate scoring |
| 🎯 **Adjustable Complexity** | Basic, intermediate, and advanced topics |
| 🌐 **Streamlit Web UI** | Interactive debate preparation dashboard |
| 💻 **Rich CLI** | Side-by-side pro/con display in terminal |
| ⚙️ **YAML Config** | Centralized configuration management |

---

## 🏗️ Architecture

```
59-debate-topic-generator/
├── src/debate_gen/
│   ├── __init__.py          # Package metadata
│   ├── core.py              # Business logic, data models, LLM interaction
│   ├── cli.py               # Rich CLI with Click commands
│   └── web_ui.py            # Streamlit web interface
├── tests/
│   ├── test_core.py         # Core logic tests
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
cd 59-debate-topic-generator
pip install -e ".[dev]"
ollama serve
```

---

## 💻 CLI Usage

```bash
# Generate debate topics
debate-gen generate --subject "technology" --complexity advanced --topics 5

# Generate moderator guide
debate-gen moderator --motion "AI should be regulated by governments"

# Save to file
debate-gen generate --subject "education" --output debate_topics.json
```

---

## 🌐 Web UI

```bash
streamlit run src/debate_gen/web_ui.py
```

Features:
- 🎯 **Subject Input** — Generate balanced debate topics on any subject
- ✅❌ **Pro/Con Cards** — Side-by-side argument display with strength ratings
- 📊 **Evidence Panel** — Visual strength analysis of all arguments
- 📋 **Moderator Notes** — Generate complete moderator guides

---

## 🧪 Testing

```bash
pytest tests/ -v
pytest tests/ -v --cov=src/debate_gen --cov-report=term-missing
```

---

## ⚙️ Configuration

Edit `config.yaml` to customize complexity levels, judging criteria weights, and LLM settings.

---

## 📝 License

MIT
