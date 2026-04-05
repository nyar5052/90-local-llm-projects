# 📐 Math Problem Solver

![Python](https://img.shields.io/badge/Python-3.9+-blue?logo=python&logoColor=white)
![LLM](https://img.shields.io/badge/LLM-Ollama-orange?logo=meta&logoColor=white)
![Streamlit](https://img.shields.io/badge/UI-Streamlit-red?logo=streamlit&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)
![Tests](https://img.shields.io/badge/Tests-Passing-brightgreen?logo=pytest)

> 🧮 **Solve math problems with step-by-step explanations, LaTeX output, formula library, and practice mode — powered by a local LLM.**

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🔢 **Step-by-Step Solutions** | Detailed breakdowns of every math problem |
| 📐 **Formula Library** | Built-in reference for algebra, geometry, calculus, trigonometry |
| 🏋️ **Practice Mode** | Generate practice problems with difficulty progression |
| 📄 **LaTeX Output** | Publication-ready mathematical notation |
| 🎯 **Difficulty Progression** | Problems from basic → intermediate → advanced |
| 🌐 **Streamlit Web UI** | Beautiful interactive web interface |
| 💻 **Rich CLI** | Full-featured terminal interface with color output |
| ⚙️ **YAML Config** | Centralized configuration management |
| 📊 **Structured Logging** | Production-grade logging throughout |

---

## 🏗️ Architecture

```
56-math-problem-solver/
├── src/math_solver/
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
# Clone and navigate
cd 56-math-problem-solver

# Install with pip
pip install -e .

# Or install dev dependencies
pip install -e ".[dev]"

# Ensure Ollama is running
ollama serve
```

---

## 💻 CLI Usage

```bash
# Solve a problem with step-by-step explanation
math-solver solve --problem "Solve 2x + 5 = 15"

# Specify category
math-solver solve --problem "Find the area of a circle with r=5" --category geometry

# Save solution to file
math-solver solve --problem "∫ x² dx" --output solution.json

# Browse formula library
math-solver formulas --category algebra

# Generate practice problems
math-solver practice --category calculus --difficulty intermediate --count 5
```

---

## 🌐 Web UI

```bash
# Launch the Streamlit web interface
streamlit run src/math_solver/web_ui.py
```

Features:
- 🔢 **Problem Input** — Enter any math problem and get instant solutions
- 📝 **Step-by-Step Display** — Expandable solution steps with LaTeX rendering
- 📖 **Formula Reference** — Browse formulas by category
- 🏋️ **Practice Quiz** — Interactive practice with hints and answers

---

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# With coverage
pytest tests/ -v --cov=src/math_solver --cov-report=term-missing
```

---

## ⚙️ Configuration

Edit `config.yaml` to customize:

```yaml
llm:
  model: "llama3"
  temperature: 0.2
  max_tokens: 4096
```

---

## 📝 License

MIT
