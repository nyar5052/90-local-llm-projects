# Poem & Lyrics Generator

Generate beautiful poems and song lyrics from themes using a local Gemma 4 LLM via Ollama.

## Features

- **Multiple Styles**: Haiku, sonnet, free verse, limerick, rap, ballad, and acrostic
- **Mood Selection**: Happy, melancholic, romantic, dark, hopeful, or nostalgic
- **Style-Accurate**: Follows proper rules for each poetic form (syllable counts, rhyme schemes)
- **Creative Temperature**: Uses higher creativity settings for more expressive output
- **Custom Titles**: Specify a title or let the AI generate one

## Prerequisites

- Python 3.10+
- [Ollama](https://ollama.ai/) running locally with the Gemma 4 model

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
# Sonnet about ocean sunset
python app.py --theme "ocean sunset" --style sonnet

# Haiku with mood
python app.py --theme "spring rain" --style haiku --mood melancholic

# Rap lyrics with title
python app.py --theme "city life" --style rap --title "Urban Rhythms"

# Save to file
python app.py --theme "lost love" --style ballad --mood nostalgic -o poem.txt
```

### Options

| Option | Description | Default |
|--------|-------------|---------|
| `--theme` | Theme or subject (required) | - |
| `--style` | Poetic style | free-verse |
| `--mood` | Mood/emotion | None |
| `--title` | Custom title | Auto-generated |
| `-o, --output` | Save to file | None |

## Example Output

```
╭─ ✨ Sonnet ────────────────────────────────────╮
│ Ocean Sunset                                   │
│                                                │
│ Upon the western rim the sun descends,         │
│ A golden orb that kisses azure deep,           │
│ While crimson light across the water bends,    │
│ And shadows slowly from the shoreline creep... │
╰────────────────────────────────────────────────╯
```

## Testing

```bash
pytest test_app.py -v
```
