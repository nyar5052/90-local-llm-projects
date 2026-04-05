# Newsletter Editor

Curate and rewrite raw content into polished, professional newsletters using a local Gemma 4 LLM via Ollama.

## Features

- **Content Curation**: Transforms raw notes, links, and bullet points into polished sections
- **Custom Sections**: Configurable number of newsletter sections
- **Editorial Intro**: Auto-generated engaging editorial opening
- **Consistent Formatting**: Clean markdown output with emoji and visual hierarchy
- **Link Preservation**: Maintains any URLs from source content
- **Key Takeaways**: Each section includes actionable takeaways

## Prerequisites

- Python 3.10+
- [Ollama](https://ollama.ai/) running locally with the Gemma 4 model

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
# Basic usage
python app.py --input notes.txt --name "Tech Weekly" --sections 4

# Casual tone
python app.py --input raw_notes.txt --name "Dev Digest" --sections 3 --tone casual

# Save to file
python app.py --input notes.txt --name "AI Weekly" --sections 5 -o newsletter.md
```

### Input File Format

Create a text file with your raw notes:
```
AI news: GPT-5 released with major improvements
New NVIDIA chip boosts training 2x
Python 3.13 out with performance gains
React 19 now stable - new hooks API
https://example.com/ai-news
```

### Options

| Option | Description | Default |
|--------|-------------|---------|
| `--input` | Path to raw notes file (required) | - |
| `--name` | Newsletter name (required) | - |
| `--sections` | Number of sections | 4 |
| `--tone` | Writing tone | informative |
| `-o, --output` | Save to file | None |

## Example Output

```
╭─ 📰 Tech Weekly ──────────────────────────────╮
│ # 📬 Tech Weekly                               │
│ *Your curated guide to what matters in tech*   │
│                                                │
│ Welcome to this week's edition! From AI        │
│ breakthroughs to framework updates...          │
│                                                │
│ ## 🤖 AI Takes a Leap Forward                  │
│ GPT-5 has arrived, bringing significant...     │
│ **Key Takeaway:** Start exploring the new...   │
│ ...                                            │
╰────────────────────────────────────────────────╯
```

## Testing

```bash
pytest test_app.py -v
```
