![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)
![Version](https://img.shields.io/badge/Version-2.0.0-orange)

# 📖 Family Story Creator

Create personalized, production-grade family stories from memories and events using a local LLM via Ollama. Features a CLI, Streamlit web UI, character builder, chapter system, and export pipeline.

---

## ✨ Features

- 👤 **Character Builder** — Build rich family member profiles with age, personality, relationship, and appearance
- 📸 **Photo Integration** — Describe photos and weave them naturally into your stories
- 📚 **Chapter Structure** — Create multi-chapter story books with table of contents
- 📤 **Book Export** — Export stories to Markdown and HTML (PDF-ready)
- 🎨 **6 Story Styles** — Heartwarming, Humorous, Adventurous, Nostalgic, Fairy-Tale, Poetic
- 🎭 **Poem Creator** — Generate personalized family poems in multiple styles

---

## 🏗️ Architecture

```
67-family-story-creator/
├── src/family_story/
│   ├── __init__.py          # Package metadata
│   ├── core.py              # Business logic, LLM integration, export
│   ├── cli.py               # Click CLI with Rich output
│   └── web_ui.py            # Streamlit web interface
├── tests/
│   ├── __init__.py
│   └── test_core.py         # Pytest test suite
├── config.yaml              # Application configuration
├── setup.py                 # Package installer
├── Makefile                 # Dev automation
├── .env.example             # Environment template
├── requirements.txt         # Python dependencies
└── README.md                # This file
```

---

## 🚀 Installation

### Prerequisites

- Python 3.10+
- [Ollama](https://ollama.ai/) running locally with a model (e.g. `llama3.2`)

### Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Or install as a package
pip install -e ".[dev]"
```

---

## 💻 CLI Usage

### Create a Story

```bash
family-story create -m "Mom, Dad, Kids" -e "vacation 2024" -s heartwarming
```

### Create with Details & Photos

```bash
family-story create \
  -m "Grandma, Grandpa" \
  -e "50th anniversary" \
  -s nostalgic \
  -d "held at the family farm" \
  -p "A black and white photo of the couple dancing" \
  -l long --save
```

### Create a Family Poem

```bash
family-story poem -m "Mom, Dad, Sam, Emma" -e "Christmas morning" -s rhyming
```

### Create a Chapter

```bash
family-story chapter -n 1 -t "The Beginning" -m "Mom, Dad" -e "Moving to the new house"
```

### Create a Multi-Chapter Book

```bash
family-story book -t "Our Family Story" -m "Mom, Dad, Sam" \
  -c "The Move:Moving to the new house" \
  -c "First Day:Sam's first day at new school" \
  -c "Homecoming:The family reunion"
```

### List Saved Stories

```bash
family-story list
```

### Export a Story

```bash
family-story export -i <story-id> -f html -o story.html
family-story export -i <story-id> -f markdown -o story.md
```

### Delete a Story

```bash
family-story delete -i <story-id>
```

### Global Options

```bash
family-story --verbose --config custom_config.yaml create ...
```

---

## 🌐 Web UI

Launch the Streamlit web interface:

```bash
streamlit run src/family_story/web_ui.py
```

### Pages

| Page | Description |
|------|-------------|
| **Story Creator** | Build characters, describe events and photos, generate stories |
| **Chapter Builder** | Compose multi-chapter books with a chapter manager |
| **Story Browser** | Browse, view, continue, and delete saved stories |
| **Poem Creator** | Generate family poems in multiple styles |

---

## ⚙️ Configuration

Edit `config.yaml` to customize behavior:

```yaml
llm:
  model: "llama3.2"
  temperature: 0.8
  max_tokens: 3000

stories_file: "family_stories.json"
default_style: "heartwarming"
default_length: "medium"

export:
  formats: ["markdown", "html"]
  output_dir: "exports"

logging:
  level: "INFO"
  file: "family_story.log"
```

Environment variables (see `.env.example`):

| Variable | Description | Default |
|----------|-------------|---------|
| `OLLAMA_HOST` | Ollama server URL | `http://localhost:11434` |
| `OLLAMA_MODEL` | LLM model name | `llama3.2` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `FAMILY_STORY_CONFIG` | Config file path | `config.yaml` |

---

## 🎨 Story Styles

| Style | Description |
|-------|-------------|
| 💖 **heartwarming** | Warm, emotional, celebrating family bonds |
| 😄 **humorous** | Funny anecdotes and light-hearted observations |
| ⚔️ **adventurous** | Exciting adventure with dramatic moments |
| 🕰️ **nostalgic** | Reflective, cherishing memories |
| 🧚 **fairy-tale** | Magical elements woven into real events |
| ✍️ **poetic** | Rich imagery and lyrical prose |

---

## 📤 Export Formats

| Format | Extension | Description |
|--------|-----------|-------------|
| **Markdown** | `.md` | Clean markdown with metadata header |
| **HTML** | `.html` | Styled HTML page, print/PDF-ready |

---

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --tb=short
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

MIT
