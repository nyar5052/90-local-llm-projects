# 📋 Meeting Summarizer

An AI-powered meeting transcript summarizer that extracts attendees, agenda topics, key decisions, action items, and follow-ups using a local LLM.

## Features

- **Attendee Extraction** — Identifies participants and their roles from the transcript
- **Agenda Detection** — Finds discussion topics covered in the meeting
- **Decision Tracking** — Highlights key decisions made during the meeting
- **Action Items** — Extracts tasks with assignee, description, and deadline
- **Follow-ups** — Captures items needing future attention
- **Rich Output** — Formatted panels, tables, and colored sections in the terminal
- **File Export** — Optionally save the summary to a Markdown file
- **Local Processing** — All data stays on your machine via Ollama + Gemma 4

## Installation

1. **Install and start Ollama:**
   ```bash
   ollama serve
   ollama pull gemma4
   ```

2. **Install dependencies:**
   ```bash
   cd 13-meeting-summarizer
   pip install -r requirements.txt
   ```

## Usage

```bash
# Basic usage
python app.py --transcript meeting.txt

# Save summary to a file
python app.py --transcript meeting.txt --output summary.md
```

### CLI Options

| Option          | Required | Description                              |
|-----------------|----------|------------------------------------------|
| `--transcript`  | Yes      | Path to the meeting transcript text file  |
| `--output`      | No       | Path to save the summary output           |

## Example Output

```
╭──────────── 📋 Meeting Summary ────────────╮
│                                             │
│  The team discussed the Q1 roadmap,         │
│  reviewed progress on the API spec and      │
│  dashboard redesign, and decided to go      │
│  with Option B for the pricing page.        │
│                                             │
╰─────────────────────────────────────────────╯

╭───────────── 👥 Attendees ──────────────────╮
│  - Alice (PM)                               │
│  - Bob (Dev)                                │
│  - Carol (Design)                           │
│  - Dave (QA)                                │
╰─────────────────────────────────────────────╯

       📝 Action Items
┏━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┓
┃ Who     ┃ What                  ┃ When     ┃
┡━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━┩
│ Bob     │ Share technical spec  │ Friday   │
│ Carol   │ Share mockups         │ Today    │
│ Dave    │ Write test cases      │ TBD      │
│ Bob     │ Update documentation  │ Wed      │
└─────────┴───────────────────────┴──────────┘
```

## Testing

```bash
pytest test_app.py -v
```

## Requirements

- Python 3.10+
- [Ollama](https://ollama.com/) with the `gemma4` model
- Dependencies listed in `requirements.txt`

## Project Structure

```
13-meeting-summarizer/
├── app.py              # Main application
├── test_app.py         # Test suite
├── requirements.txt    # Python dependencies
└── README.md           # This file
```
