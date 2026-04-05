# 🔎 Code Snippet Search

AI-powered natural language code search tool that indexes local codebases and finds relevant snippets using a local Gemma 4 LLM.

## ✨ Features

- **Natural Language Queries** — Search code using plain English descriptions
- **Directory Scanning** — Recursively indexes files while ignoring common non-code directories
- **Multi-language Support** — Indexes Python, JavaScript, TypeScript, Java, Go, Rust, and more
- **Relevance Ranking** — Results ranked by relevance with explanations
- **File Summary** — Shows indexed files with line counts
- **Configurable** — Set max files, filter by extension

## 📦 Installation

```bash
pip install -r requirements.txt
```

## 🚀 Usage

```bash
# Search in a directory
python app.py --dir ./src --query "find authentication logic"

# Limit to specific extensions
python app.py --dir ./project --query "database connection" --ext .py --ext .sql

# Limit number of indexed files
python app.py --dir ./src --query "error handling" --max-files 50
```

## 📋 Example Output

```
╭──────────────────────────────────────────╮
│  🔎 Code Snippet Search                 │
│  Search code with natural language       │
╰──────────────────────────────────────────╯

Indexed 23 file(s)

╭── 🎯 Search Results ──────────────────╮
│ ## auth/login.py (HIGH)                │
│ Lines 15-30: JWT token validation      │
│                                        │
│ ## middleware/auth.py (MEDIUM)          │
│ Lines 5-12: Authentication middleware  │
╰────────────────────────────────────────╯
```

## 🧪 Testing

```bash
pytest test_app.py -v
```

## ⚙️ Requirements

- Python 3.10+
- Ollama running locally with Gemma 4 model
