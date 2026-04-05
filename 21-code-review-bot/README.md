# 🔍 Code Review Bot

AI-powered code review tool that analyzes code files for bugs, style issues, security vulnerabilities, and performance problems using a local Gemma 4 LLM.

## ✨ Features

- **Multi-category Review** — Identifies bugs, style issues, security vulnerabilities, performance problems, and best practice violations
- **Line-number References** — Every finding references specific line numbers in your code
- **Focus Areas** — Narrow the review to specific concerns like security or performance
- **Syntax Highlighting** — View your source code with syntax highlighting before the review
- **Rich Output** — Beautiful, colored terminal output with structured results

## 📦 Installation

```bash
pip install -r requirements.txt
```

## 🚀 Usage

```bash
# Basic code review
python app.py --file script.py

# Review with specific focus areas
python app.py --file script.py --focus "security,performance"

# Show source code alongside review
python app.py --file script.py --show-code

# Combine options
python app.py --file app.js --focus "bugs,style" --show-code
```

## 📋 Example Output

```
╭──────────────────────────────────────────╮
│  🔍 Code Review Bot                     │
│  AI-powered code review with feedback    │
╰──────────────────────────────────────────╯

Reviewing: script.py

╭── 📋 Code Review Results ───────────────╮
│ ## Security Issues                       │
│ - Line 15: SQL injection vulnerability   │
│   Severity: HIGH                         │
│   Fix: Use parameterized queries         │
│                                          │
│ ## Performance                           │
│ - Line 42: Nested loop O(n²)            │
│   Severity: MEDIUM                       │
│   Fix: Consider using a hash map         │
╰──────────────────────────────────────────╯
```

## 🧪 Testing

```bash
pytest test_app.py -v
```

## ⚙️ Requirements

- Python 3.10+
- Ollama running locally with Gemma 4 model
