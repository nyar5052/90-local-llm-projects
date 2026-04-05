# 🔄 Code Translator

AI-powered tool that translates code between programming languages using a local Gemma 4 LLM.

## ✨ Features

- **10 Languages Supported** — Python, JavaScript, TypeScript, Java, Go, Rust, C#, C++, Ruby, PHP
- **Idiomatic Translation** — Uses target language patterns and conventions
- **Auto-detection** — Automatically detects source language from file extension
- **Translation Notes** — Explains key decisions and differences
- **File Output** — Save translated code directly to a file

## 📦 Installation

```bash
pip install -r requirements.txt
```

## 🚀 Usage

```bash
# Translate Python to JavaScript
python app.py --file script.py --target javascript

# Translate with explicit source language
python app.py --file code.txt --target rust --source-lang python

# Save translated output
python app.py --file main.go --target python --output main.py

# Translate to TypeScript
python app.py --file app.js --target typescript
```

## 📋 Example Output

```
╭──────────────────────────────────────────╮
│  🔄 Code Translator                     │
│  Translate code between languages        │
╰──────────────────────────────────────────╯

Source: script.py (Python)
Target: JavaScript

╭── 📄 Source (Python) ──────────────────╮
│ 1 │ def fibonacci(n):                  │
│ 2 │     if n <= 1:                     │
│ 3 │         return n                   │
│ 4 │     return fibonacci(n-1) + ...    │
╰────────────────────────────────────────╯

╭── 🔄 Translated to JavaScript ────────╮
│ function fibonacci(n) {                │
│   if (n <= 1) return n;                │
│   return fibonacci(n - 1) + ...;       │
│ }                                      │
╰────────────────────────────────────────╯
```

## 🧪 Testing

```bash
pytest test_app.py -v
```

## ⚙️ Requirements

- Python 3.10+
- Ollama running locally with Gemma 4 model
