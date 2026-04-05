# 🔥 Stack Trace Explainer

AI-powered tool that explains stack traces and error messages in plain English, identifies root causes, and suggests fixes using a local Gemma 4 LLM.

## ✨ Features

- **Plain English Explanations** — Translates cryptic error messages into understandable language
- **Language Detection** — Automatically detects Python, JavaScript, Java, C#, Go, and Rust traces
- **Root Cause Analysis** — Identifies the most likely cause of the error
- **Fix Suggestions** — Provides concrete code fixes for common errors
- **Multiple Input Sources** — Read from files, stdin pipes, or direct text input

## 📦 Installation

```bash
pip install -r requirements.txt
```

## 🚀 Usage

```bash
# Read from a file
python app.py --trace error.txt

# Pipe from another command
cat error.txt | python app.py
python script.py 2>&1 | python app.py

# Paste directly
python app.py --text "Traceback (most recent call last):..."

# With language hint
python app.py --trace error.txt --lang python
```

## 📋 Example Output

```
╭──────────────────────────────────────────╮
│  🔥 Stack Trace Explainer               │
│  Understand errors in plain English      │
╰──────────────────────────────────────────╯

Detected language: python

╭── 📜 Stack Trace ──────────────────────╮
│ Traceback (most recent call last):     │
│   File "app.py", line 42, in main      │
│     result = data["key"]               │
│ KeyError: 'key'                        │
╰────────────────────────────────────────╯

╭── 💡 Explanation & Fix ────────────────╮
│ ## Error Summary                       │
│ The program tried to access a          │
│ dictionary key that doesn't exist.     │
│                                        │
│ ## Fix                                 │
│ Use dict.get("key", default_value)     │
╰────────────────────────────────────────╯
```

## 🧪 Testing

```bash
pytest test_app.py -v
```

## ⚙️ Requirements

- Python 3.10+
- Ollama running locally with Gemma 4 model
