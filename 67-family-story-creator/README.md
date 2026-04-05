# 👨‍👩‍👧‍👦 Family Story Creator

Create personalized family stories from memories and events using a local Gemma 4 LLM via Ollama.

## Features

- **Personalized Stories**: Creates stories using actual family member names and events
- **Multiple Styles**: Heartwarming, humorous, adventurous, nostalgic, fairy-tale, poetic
- **Family Poems**: Generate poems about family events
- **Photo Integration**: Incorporate photo descriptions into narratives
- **Story Library**: Save and manage your family stories
- **Adjustable Length**: Short, medium, or long stories

## Prerequisites

- Python 3.10+
- [Ollama](https://ollama.ai/) running locally with Gemma 4 model

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Create a Story
```bash
python app.py create --members "Mom,Dad,Kids" --event "vacation 2024" --style heartwarming
```

### Create with Details
```bash
python app.py create --members "Grandma,Grandpa" --event "50th anniversary" --style nostalgic --details "held at the family farm" --length long
```

### Create a Family Poem
```bash
python app.py poem --members "Mom,Dad,Sam,Emma" --event "Christmas morning" --style rhyming
```

### Save Story
```bash
python app.py create --members "Family" --event "reunion" --style heartwarming --save
```

### List Saved Stories
```bash
python app.py list
```

## Story Styles

| Style        | Description                                    |
|-------------|------------------------------------------------|
| heartwarming | Warm, emotional, celebrating family bonds     |
| humorous     | Funny anecdotes and light-hearted moments     |
| adventurous  | Exciting adventure with dramatic moments      |
| nostalgic    | Reflective, cherishing memories               |
| fairy-tale   | Magical elements woven into real events       |
| poetic       | Rich imagery and lyrical prose                |

## Example Output

```
╭────── 👨‍👩‍👧‍👦 Family Story Creator ──────╮
│ Style: heartwarming | Length: medium   │
╰────────────────────────────────────────╯

╭──────────── 📖 Your Family Story ────────────╮
│ # A Day to Remember                          │
│                                               │
│ The sun painted golden streaks across the     │
│ morning sky as Mom, Dad, and the kids piled   │
│ into the car, excitement buzzing...           │
╰───────────────────────────────────────────────╯
```

## Testing

```bash
pytest test_app.py -v
```

## License

MIT
