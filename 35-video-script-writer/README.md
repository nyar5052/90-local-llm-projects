# Video Script Writer

Create complete YouTube/video scripts with timestamps, B-roll suggestions, and on-screen text using a local Gemma 4 LLM via Ollama.

## Features

- **Complete Script Structure**: Hook, intro, main content sections, and outro
- **Timestamps**: Precise timing for each section based on target duration
- **B-Roll Suggestions**: Visual overlay recommendations for each segment
- **On-Screen Text**: Suggested text overlays and graphics
- **Multiple Styles**: Educational, entertainment, tutorial, review, vlog, documentary
- **Speaking Time Estimate**: Word count and estimated speaking duration

## Prerequisites

- Python 3.10+
- [Ollama](https://ollama.ai/) running locally with the Gemma 4 model

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
# Basic educational video
python app.py --topic "Python Tips" --duration 10 --style educational

# Tutorial with audience
python app.py --topic "React Hooks Explained" --duration 15 --style tutorial --audience "beginner developers"

# Save to file
python app.py --topic "Product Review" --duration 8 --style review -o script.md
```

### Options

| Option | Description | Default |
|--------|-------------|---------|
| `--topic` | Video topic (required) | - |
| `--duration` | Target duration in minutes | 10 |
| `--style` | Video style | educational |
| `--audience` | Target audience | None |
| `-o, --output` | Save to file | None |

## Example Output

```
╭─ 🎬 Video Script ─────────────────────────────╮
│ ## HOOK [0:00-0:15]                            │
│ **Script:** "Did you know that 90% of Python   │
│ developers don't use these 5 tips?"            │
│ [B-ROLL] Fast montage of code snippets         │
│                                                │
│ ## INTRO [0:15-1:00]                           │
│ **Script:** "Hey everyone, welcome back..."    │
│ [ON-SCREEN TEXT] "5 Python Tips You Need"      │
│ ...                                            │
╰────────────────────────────────────────────────╯
```

## Testing

```bash
pytest test_app.py -v
```
