# 📊 Code Complexity Analyzer

AI-powered tool that analyzes code complexity, computes metrics, and suggests improvements using a local Gemma 4 LLM.

## ✨ Features

- **Cyclomatic Complexity** — Measures the number of independent paths through code
- **Cognitive Complexity** — Evaluates how difficult code is to understand
- **Maintainability Index** — Overall maintainability score (0-100)
- **Halstead Volume** — Measures code vocabulary and length complexity
- **Line Metrics** — Counts code, comment, and blank lines
- **AI Suggestions** — LLM-powered refactoring recommendations
- **Per-function Breakdown** — Detailed metrics for each function/method

## 📦 Installation

```bash
pip install -r requirements.txt
```

## 🚀 Usage

```bash
# Summary report (default)
python app.py --file script.py

# Detailed report with AI suggestions
python app.py --file script.py --report detailed

# Metrics only (no AI)
python app.py --file script.py --no-ai
```

## 📋 Example Output

```
╭──────────────────────────────────────────╮
│  📊 Code Complexity Analyzer            │
│  Analyze and improve code complexity     │
╰──────────────────────────────────────────╯

╭── 📏 Line Counts ─────────────────────╮
│ Metric        │ Count                  │
│ Total Lines   │ 156                    │
│ Code Lines    │ 120                    │
│ Blank Lines   │ 24                     │
│ Comment Lines │ 12                     │
╰────────────────────────────────────────╯

╭── 📊 Overall Metrics ─────────────────╮
│ Metric                    │ Value      │
│ Maintainability Index     │ 62/100     │
│ Avg Cyclomatic Complexity │ 4.5        │
│ Halstead Volume           │ 245.3      │
╰────────────────────────────────────────╯

╭── 🔍 Function Complexity ─────────────╮
│ Function    │ CC │ Cognitive │ Rating   │
│ process()   │ 8  │ 12        │ MEDIUM   │
│ validate()  │ 12 │ 18        │ HIGH     │
│ helper()    │ 2  │ 1         │ LOW      │
╰────────────────────────────────────────╯

╭── 💡 AI Suggestions ──────────────────╮
│ - Extract nested conditionals into    │
│   separate methods                    │
│ - Use early returns to reduce nesting │
│ - Consider Strategy pattern for       │
│   process() function                  │
╰────────────────────────────────────────╯
```

## 🧪 Testing

```bash
pytest test_app.py -v
```

## ⚙️ Requirements

- Python 3.10+
- Ollama running locally with Gemma 4 model
