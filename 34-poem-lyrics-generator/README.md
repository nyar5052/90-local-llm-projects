# ✨ Poem & Lyrics Generator

![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)
![License: MIT](https://img.shields.io/badge/license-MIT-green)
![Version](https://img.shields.io/badge/version-2.0.0-orange)
![Ollama](https://img.shields.io/badge/LLM-Ollama-purple)

Generate beautiful poems and song lyrics from themes using a local LLM via Ollama. Supports 7 poetic styles, 6 moods, rhyme scheme control, style mixing, poem analysis, and collection management.

---

## 🏗️ Architecture

```
34-poem-lyrics-generator/
├── src/poem_gen/
│   ├── __init__.py        # Package metadata
│   ├── config.py          # YAML config loader & logging setup
│   ├── core.py            # Prompt building, generation, analysis, collections
│   ├── cli.py             # Rich CLI (Click)
│   └── web_ui.py          # Streamlit web interface
├── tests/
│   ├── conftest.py        # Shared test fixtures & path setup
│   ├── test_core.py       # Core logic tests
│   └── test_cli.py        # CLI integration tests
├── collections/           # Saved poem collections (JSON)
├── config.yaml            # Application configuration
├── setup.py               # Package installer
├── Makefile               # Common tasks
├── requirements.txt       # Python dependencies
└── .env.example           # Environment variable template
```

## ✅ Features

- 🎭 **7 Poetic Styles** — Haiku, sonnet, free-verse, limerick, rap, ballad, acrostic
- 💫 **6 Moods** — Happy, melancholic, romantic, dark, hopeful, nostalgic
- 🔤 **Custom Rhyme Schemes** — Request ABAB, AABB, or any pattern
- 🎨 **Style Mixing** — Blend two styles (e.g., haiku + rap) into one poem
- 📊 **Poem Analysis** — Syllable counting, rhyme scheme detection, word/line counts
- 📚 **Collection Manager** — Save, list, and download poem collections
- 🖥️ **Rich CLI** — Beautiful terminal output with panels and tables
- 🌐 **Streamlit Web UI** — Full-featured browser interface
- ⚙️ **YAML Config** — Configurable model, temperature, styles, and more
- 📝 **Style-Specific Formatting** — Proper indentation per poetic form

## 📋 Prerequisites

- Python 3.10+
- [Ollama](https://ollama.ai/) running locally (`ollama serve`)
- A model pulled (e.g., `ollama pull llama3`)

## 🚀 Installation

```bash
pip install -r requirements.txt
pip install -e .
```

## 💻 CLI Usage

```bash
# Basic generation
poem-gen --theme "ocean sunset" --style sonnet

# With mood and title
poem-gen --theme "spring rain" --style haiku --mood melancholic --title "April Showers"

# Custom rhyme scheme
poem-gen --theme "lost love" --rhyme-scheme ABAB

# Mix two styles
poem-gen --theme "city life" --mix-styles "haiku,rap"

# Analyze the generated poem
poem-gen --theme "nature" --style ballad --analyze

# Save to file
poem-gen --theme "stars" --style sonnet -o poem.txt

# Save to a named collection
poem-gen --theme "the sea" --style free-verse --collection ocean-poems

# List poems in a collection
poem-gen --list-collection ocean-poems
```

### CLI Options

| Option               | Description                                   | Default     |
|----------------------|-----------------------------------------------|-------------|
| `--theme`            | Theme or subject (required for generation)    | —           |
| `--style`            | Poetic style                                  | free-verse  |
| `--mood`             | Mood / emotion                                | None        |
| `--title`            | Custom title                                  | Auto        |
| `-o, --output`       | Save output to file                           | None        |
| `--rhyme-scheme`     | Generate with specific rhyme scheme           | None        |
| `--mix-styles`       | Comma-separated pair of styles to blend       | None        |
| `--analyze`          | Show poem analysis (syllables, rhyme, etc.)   | Off         |
| `--collection`       | Save poem to named collection                 | None        |
| `--list-collection`  | Display poems in a saved collection           | None        |

## 🌐 Web UI

```bash
streamlit run src/poem_gen/web_ui.py
```

Features:
- Theme, style, mood, and title inputs
- Optional rhyme scheme override
- Style mixing with dual dropdowns
- Beautiful poem display with formatting
- Poem analysis with syllable chart
- Collection manager: save, view, and download

## 📊 Example Output

```
╭─ ✨ Sonnet ────────────────────────────────────╮
│   Upon the western rim the sun descends,       │
│   A golden orb that kisses azure deep,         │
│   While crimson light across the water bends,  │
│   And shadows slowly from the shoreline creep. │
│                                                │
│   The seagulls cry above the foaming waves,    │
│   As twilight paints the sky in shades of gold,│
│   …                                            │
╰────────────────────────────────────────────────╯

┌──────────────────────────────────────┐
│         📊 Poem Analysis             │
├──────────────┬───────────────────────┤
│ Lines        │ 14                    │
│ Words        │ 112                   │
│ Rhyme Scheme │ ABAB CDCD EFEF GG     │
│ Syllables    │ 10, 10, 10, 10, …     │
└──────────────┴───────────────────────┘
```

## 🧪 Testing

```bash
pytest tests/ -v
```

## ⚙️ Configuration

Edit `config.yaml` to customize:

```yaml
llm:
  model: "llama3"
  temperature: 0.9
  max_tokens: 2048
poem:
  default_style: "free-verse"
  collections_dir: "collections"
```

## 📁 Project Info

- **Module**: `poem_gen`
- **Entry Point**: `poem-gen` (CLI) / `streamlit run src/poem_gen/web_ui.py` (Web)
- **Config**: `config.yaml`
- **Collections**: Stored as JSON in `collections/`
