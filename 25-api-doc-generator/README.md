# 📚 API Doc Generator

AI-powered tool that generates professional API documentation from Python source code using a local Gemma 4 LLM.

## ✨ Features

- **AST-based Extraction** — Uses Python's AST module for accurate code analysis
- **Function & Class Detection** — Extracts functions, classes, methods, parameters, and return types
- **Docstring Aware** — Leverages existing docstrings to enhance documentation
- **Async Support** — Properly documents async functions and methods
- **Directory Scanning** — Recursively scans entire project directories
- **File Output** — Save documentation to Markdown files

## 📦 Installation

```bash
pip install -r requirements.txt
```

## 🚀 Usage

```bash
# Generate docs for a single file
python app.py --source module.py

# Generate docs for a directory
python app.py --source src/

# Save to a file
python app.py --source src/ --output docs.md
```

## 📋 Example Output

```
╭──────────────────────────────────────────╮
│  📚 API Doc Generator                   │
│  Generate API docs from Python source    │
╰──────────────────────────────────────────╯

Found 5 Python file(s)

╭── 📚 API Documentation ───────────────╮
│ # API Reference                        │
│                                        │
│ ## `add(a: int, b: int) -> int`        │
│ Add two numbers together.              │
│                                        │
│ | Param | Type | Description |         │
│ |-------|------|-------------|         │
│ | a     | int  | First number |        │
│ | b     | int  | Second number |       │
╰────────────────────────────────────────╯
```

## 🧪 Testing

```bash
pytest test_app.py -v
```

## ⚙️ Requirements

- Python 3.10+
- Ollama running locally with Gemma 4 model
