# 📰 News Digest Generator

Aggregate, categorize, and summarize news articles from text files using a local LLM. This tool reads `.txt` news files from a folder, groups them by topic, generates per-topic summaries, and produces a polished overall digest — all powered by Ollama running locally.

## Features

- **Topic Categorization** — Automatically groups articles into a configurable number of topic categories
- **Article Summarization** — Generates concise summaries for each topic group
- **Key Headlines Extraction** — Identifies the most important headlines across all articles
- **Trending Themes** — Discovers overarching themes and patterns in the news
- **Rich Terminal Output** — Beautiful formatted output with panels, tables, and trees
- **Export to File** — Optionally save the generated digest to a Markdown file
- **Batch Processing** — Processes all `.txt` files in a directory at once

## Installation

```bash
cd 19-news-digest-generator
pip install -r requirements.txt
```

Make sure [Ollama](https://ollama.ai) is installed and running:

```bash
ollama serve
ollama pull gemma4
```

## Usage

```bash
# Basic usage — categorize into 5 topics (default)
python app.py --sources news_folder/

# Specify number of topic groups
python app.py --sources news_folder/ --topics 5

# Save digest to a file
python app.py --sources news_folder/ --topics 3 --output digest.md
```

### CLI Options

| Option      | Type   | Default | Description                                  |
|-------------|--------|---------|----------------------------------------------|
| `--sources` | PATH   | —       | **(Required)** Path to folder of `.txt` news files |
| `--topics`  | INT    | `5`     | Number of topic groups to categorize into    |
| `--output`  | PATH   | —       | Optional file path to save the digest        |

## Example Output

```
📰 News Digest Generator

✓ Ollama is running
✓ Loaded 12 article(s) from news_folder/

┌──────────────────────────────────┐
│       Source Articles            │
├──────────────────┬───────────────┤
│ File             │ Length        │
├──────────────────┼───────────────┤
│ tech_ai.txt      │ 1,234 chars  │
│ sports_nba.txt   │ 892 chars    │
│ finance_fed.txt  │ 1,567 chars  │
└──────────────────┴───────────────┘

╭─ Topic Categorization (3 groups) ─╮
│                                    │
│  ## Topic: Technology              │
│  **Articles:** tech_ai.txt         │
│  **Summary:** Major advances in …  │
│                                    │
│  ## Topic: Sports                  │
│  **Articles:** sports_nba.txt      │
│  **Summary:** Exciting playoff …   │
│                                    │
╰────────────────────────────────────╯

╭──────── 📋 News Digest ──────────╮
│                                   │
│  # Key Headlines                  │
│  - AI revolution continues        │
│  - Markets rally on Fed decision  │
│                                   │
│  # Trending Themes                │
│  - Technology-driven growth       │
│                                   │
╰───────────────────────────────────╯

📊 Generation Stats
├── Articles processed: 12
├── Topic groups requested: 3
└── Total input size: 15,432 characters
```

## Testing

```bash
pytest test_app.py -v
```

## Project Structure

```
19-news-digest-generator/
├── app.py              # Main application
├── requirements.txt    # Python dependencies
├── test_app.py         # Pytest test suite
└── README.md           # This file
```

## How It Works

1. **Read** — Scans the sources folder for `.txt` files and loads their content
2. **Categorize** — Sends all articles to the LLM to group them into topic categories
3. **Digest** — Generates a professional news digest with headlines, themes, and summaries
4. **Display** — Renders the results in a rich terminal UI with panels and tables
5. **Save** — Optionally exports the complete digest to a Markdown file
