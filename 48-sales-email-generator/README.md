# ✉️ Sales Email Generator

Generate personalized sales outreach emails using a local Gemma 4 LLM.

## Features

- **Personalized Emails**: Tailored to prospect role, company, and industry
- **Multiple Tones**: Professional, casual, persuasive, or consultative
- **Follow-up Mode**: Generate follow-up emails with different angles
- **A/B Variants**: Create multiple email variants for testing
- **Context-Aware**: Incorporate additional prospect context

## Prerequisites

- Python 3.10+
- [Ollama](https://ollama.ai/) running locally with Gemma 4 model

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
# Basic professional email
python app.py --prospect "CTO at startup" --product "AI Platform" --tone professional

# Casual follow-up with context
python app.py -p "VP Engineering at Acme" -pr "Dev Tools" -t casual --follow-up -c "Met at conference"

# Generate 3 A/B variants
python app.py -p "CMO at enterprise" -pr "Analytics Suite" --variants 3
```

## Tone Options

| Tone | Description |
|------|-------------|
| `professional` | Formal, business-appropriate, respectful |
| `casual` | Friendly, conversational, approachable |
| `persuasive` | Compelling, benefit-focused, action-oriented |
| `consultative` | Advisory, problem-solving, thought-leadership |

## Example Output

```
✉️ Sales Email Generator
Prospect: CTO at startup
Product: AI Platform
Tone: professional

╭── ✉️ Generated Email ──╮
│ Subject: Elevate Your   │
│ AI Strategy             │
│                         │
│ Dear [Name],            │
│                         │
│ I noticed your startup  │
│ is making waves in the  │
│ AI space...             │
╰─────────────────────────╯
```

## Testing

```bash
pytest test_app.py -v
```
