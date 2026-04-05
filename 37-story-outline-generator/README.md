# Story Outline Generator

Create detailed story and novel outlines with characters, plot, and chapter breakdowns using a local Gemma 4 LLM via Ollama.

## Features

- **Multiple Genres**: Sci-fi, fantasy, mystery, thriller, romance, horror, literary, historical
- **Rich Characters**: Detailed character profiles with arcs, motivations, and relationships
- **Plot Structure**: Three-act structure with inciting incident, midpoint, and climax
- **Chapter Breakdown**: Individual chapter summaries with POV, events, and cliffhangers
- **Title Suggestions**: Multiple title options for your story

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
python app.py --genre "sci-fi" --premise "AI awakens" --chapters 10

# Fantasy with more characters
python app.py --genre "fantasy" --premise "dragons return to a modern city" --chapters 15 --characters 6

# Save to file
python app.py --genre "mystery" --premise "locked room murder at a tech company" -o outline.md
```

### Options

| Option | Description | Default |
|--------|-------------|---------|
| `--genre` | Story genre (required) | - |
| `--premise` | Story premise (required) | - |
| `--chapters` | Number of chapters | 10 |
| `--characters` | Number of main characters | 4 |
| `-o, --output` | Save to file | None |

## Example Output

```
╭─ 📖 Story Outline ────────────────────────────╮
│ ## Story Overview                              │
│ **Title Options:**                             │
│ 1. The Awakening Protocol                      │
│ 2. Silicon Consciousness                       │
│ 3. Beyond the Algorithm                        │
│                                                │
│ **Logline:** When a quantum AI achieves...     │
│                                                │
│ ## Characters                                  │
│ ### Ada Chen - Protagonist                     │
│ A brilliant AI researcher who discovers...     │
│                                                │
│ ## Chapter 1: Genesis                          │
│ **POV:** Ada Chen                              │
│ - Discovers anomaly in AI training data...     │
╰────────────────────────────────────────────────╯
```

## Testing

```bash
pytest test_app.py -v
```
