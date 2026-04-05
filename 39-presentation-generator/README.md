# Presentation Generator

Generate complete presentation slide content with speaker notes using a local Gemma 4 LLM via Ollama.

## Features

- **Complete Slide Decks**: Title, content, visuals, and transitions for every slide
- **Speaker Notes**: Conversational talking points for each slide
- **Visual Suggestions**: Recommended images, charts, and diagrams
- **Multiple Formats**: Standard, Pecha Kucha, lightning talk, keynote
- **Audience-Aware**: Content tailored to audience knowledge level
- **Structured Layout**: Title, agenda, content, data, Q&A, and closing slides

## Prerequisites

- Python 3.10+
- [Ollama](https://ollama.ai/) running locally with the Gemma 4 model

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
# Basic presentation
python app.py --topic "Machine Learning 101" --slides 12 --audience "beginners"

# Keynote format
python app.py --topic "Future of AI" --slides 20 --audience "executives" --format keynote

# Lightning talk
python app.py --topic "Docker in 5 Minutes" --slides 8 --format lightning -o slides.md
```

### Options

| Option | Description | Default |
|--------|-------------|---------|
| `--topic` | Presentation topic (required) | - |
| `--slides` | Number of slides | 12 |
| `--audience` | Target audience | general |
| `--format` | Format (standard/pecha-kucha/lightning/keynote) | standard |
| `-o, --output` | Save to file | None |

## Example Output

```
╭─ 📊 Presentation ─────────────────────────────╮
│ ### Slide 1: Machine Learning 101              │
│ **Content:**                                   │
│ - "Making Machines Learn from Data"            │
│ - Your Name | Date                             │
│                                                │
│ **Visual:** Clean title slide with neural      │
│ network illustration                           │
│                                                │
│ **Speaker Notes:** Welcome everyone! Today     │
│ we're going to demystify machine learning...   │
│                                                │
│ **Transition:** "Let's start with the basics"  │
╰────────────────────────────────────────────────╯
```

## Testing

```bash
pytest test_app.py -v
```
