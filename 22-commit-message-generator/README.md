# 📝 Commit Message Generator

AI-powered tool that reads git diffs and generates high-quality conventional commit messages using a local Gemma 4 LLM.

## ✨ Features

- **Conventional Commits** — Follows the Conventional Commits specification (feat, fix, refactor, etc.)
- **Multiple Suggestions** — Provides 3 ranked commit message options
- **Flexible Input** — Reads from staged changes, all changes, stdin, or diff files
- **Type Hints** — Optionally specify the commit type to guide generation
- **Change Summary** — Displays diff stats before generating messages

## 📦 Installation

```bash
pip install -r requirements.txt
```

## 🚀 Usage

```bash
# Generate from staged changes (default)
python app.py

# Generate from all changes (including unstaged)
python app.py --all

# Specify commit type
python app.py --type feat

# Read from a diff file
python app.py --diff-file changes.diff

# Pipe from git diff
git diff | python app.py
```

## 📋 Example Output

```
╭──────────────────────────────────────────╮
│  📝 Commit Message Generator             │
│  Generate conventional commit messages   │
╰──────────────────────────────────────────╯

╭── 📊 Changes Summary ──────────────────╮
│ 2 files changed, 15 insertions(+)      │
╰─────────────────────────────────────────╯

╭── 💡 Suggested Commit Messages ────────╮
│ 1. feat(auth): add JWT token refresh   │
│ 2. feat: implement token refresh logic │
│ 3. feat(auth): add automatic refresh   │
╰─────────────────────────────────────────╯
```

## 🧪 Testing

```bash
pytest test_app.py -v
```

## ⚙️ Requirements

- Python 3.10+
- Git installed and in PATH
- Ollama running locally with Gemma 4 model
