# 📚 Personal Knowledge Base

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![License](https://img.shields.io/badge/License-MIT-green)
![Tests](https://img.shields.io/badge/Tests-pytest-orange?logo=pytest)
![LLM](https://img.shields.io/badge/LLM-Ollama-purple)
![UI](https://img.shields.io/badge/UI-Streamlit-red?logo=streamlit)

AI-powered personal knowledge base with **semantic search**, **tagging**, **backlinks**, **note templates**, and a **Streamlit web UI** — all powered by a local LLM via Ollama.

---

## ✨ Features

| Category | Features |
|---|---|
| 📝 **Notes** | Create, edit, delete notes with rich content |
| 🏷️ **Tags** | Organise notes with tags, browse tag cloud |
| 🔗 **Backlinks** | Automatic detection of cross-note references |
| 🔍 **Search** | AI semantic search **+** fast full-text search |
| 📋 **Templates** | Meeting notes, book reviews, project plans |
| 📤 **Export / Import** | Markdown export & round-trip import |
| 📊 **Summaries** | AI-generated knowledge base overview |
| 🌐 **Web UI** | Full Streamlit interface with sidebar navigation |
| ⌨️ **CLI** | Complete Click-based command-line interface |
| ⚙️ **Config** | YAML configuration with sensible defaults |

---

## 🏗️ Architecture

```
62-personal-knowledge-base/
├── src/knowledge_base/
│   ├── __init__.py          # Package metadata & version
│   ├── core.py              # All business logic (CRUD, tags, backlinks, search, templates, export)
│   ├── cli.py               # Click CLI commands
│   └── web_ui.py            # Streamlit web interface
├── tests/
│   ├── __init__.py
│   └── test_core.py         # Comprehensive test suite
├── data/                    # JSON knowledge base storage
├── config.yaml              # Application configuration
├── setup.py                 # Package setup with entry point
├── Makefile                 # Build / test / run shortcuts
├── requirements.txt         # Python dependencies
├── .env.example             # Environment variable template
└── README.md
```

---

## 📋 Prerequisites

- **Python 3.10+**
- [Ollama](https://ollama.ai/) running locally
  ```bash
  ollama serve
  ollama pull llama3
  ```

---

## 🚀 Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Install as editable package
pip install -e .
```

---

## ⌨️ CLI Usage

### Add a Note
```bash
knowledge-base add --title "ML Notes" --content "Neural networks use backpropagation" --tags "ml,ai"
```

### Semantic Search (AI)
```bash
knowledge-base search --query "neural network training"
```

### Full-Text Search (fast, no LLM)
```bash
knowledge-base find --query "backpropagation"
```

### List All Notes
```bash
knowledge-base list
knowledge-base list --tag ml       # filter by tag
```

### Generate Summary
```bash
knowledge-base summary
```

### Delete a Note
```bash
knowledge-base delete --note-id 1
```

### Tag Cloud
```bash
knowledge-base tags
```

### Backlinks
```bash
knowledge-base backlinks --note-id 1
```

### Templates
```bash
# List available templates
knowledge-base template

# Apply a template
knowledge-base template --name meeting_notes -p date=2024-06-15
```

### Export / Import
```bash
knowledge-base export --output notes.md
knowledge-base import notes.md
```

---

## 🌐 Web UI

Launch the Streamlit interface:

```bash
streamlit run src/knowledge_base/web_ui.py
```

The web UI provides:
- **Add Note** — editor with title, content, tags, and template selector
- **Search** — toggle between fast full-text and AI semantic search
- **Browse** — scroll through all notes with delete option
- **Tags** — tag cloud with note counts and filtering
- **Backlinks** — visualise note connections
- **Templates** — preview available templates
- **Export / Import** — one-click Markdown export & file upload import

---

## ⚙️ Configuration

Edit `config.yaml` to customise behaviour:

```yaml
app:
  name: "Personal Knowledge Base"
  log_level: "INFO"       # DEBUG, INFO, WARNING, ERROR
  data_dir: "./data"      # Where JSON storage lives

knowledge_base:
  max_notes: 10000
  search_limit: 20
  backup_enabled: true

llm:
  model: "llama3"
  temperature: 0.3

templates:
  meeting_notes:
    title: "Meeting Notes - {date}"
    content: "## Attendees\n\n## Agenda\n..."
```

---

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# With coverage
pytest tests/ -v --cov=knowledge_base --cov-report=term-missing
```

---

## 📝 Example Output

```
╭────────── 📚 Personal Knowledge Base ──────────╮
│ Searching for: neural network training          │
╰─────────────────────────────────────────────────╯

╭─────────── 🔍 Search Results ───────────╮
│ ## Relevant Notes                        │
│ - Note #1: ML Notes covers neural        │
│   networks and backpropagation           │
│ - Related topics: deep learning, SGD     │
╰──────────────────────────────────────────╯
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes and add tests
4. Run the test suite (`pytest tests/ -v`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

---

## 📄 License

MIT
