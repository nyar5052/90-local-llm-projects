# Email Campaign Writer

Generate professional marketing email sequences using a local Gemma 4 LLM via Ollama.

## Features

- **Multi-Email Sequences**: Generate cohesive email campaigns with 1-10 emails
- **Campaign Types**: Welcome, promotional, nurture, re-engagement, and product launch
- **A/B Subject Lines**: Each email includes subject line variants for testing
- **Complete Email Copy**: Subject, preview text, body, and call-to-action
- **Send Timing**: Suggested scheduling relative to previous emails
- **Copywriting Frameworks**: Uses AIDA, PAS, and other proven frameworks

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
python app.py --product "SaaS Tool" --audience "developers" --emails 3

# Welcome campaign
python app.py --product "Fitness App" --audience "health enthusiasts" --type welcome --emails 5

# Save to file
python app.py --product "Online Course" --audience "marketers" --type nurture -o campaign.md
```

### Options

| Option | Description | Default |
|--------|-------------|---------|
| `--product` | Product/service name (required) | - |
| `--audience` | Target audience (required) | - |
| `--emails` | Number of emails in sequence | 3 |
| `--type` | Campaign type | promotional |
| `-o, --output` | Save output to file | None |

## Example Output

```
╭─ Email Campaign ───────────────────────────────╮
│ ## Email 1 - Welcome                           │
│ **Subject A:** Welcome to SaaS Tool, {{name}}! │
│ **Subject B:** Your journey starts now 🚀      │
│ **Preview:** Get started in 3 easy steps...    │
│                                                │
│ **Body:**                                      │
│ Hi {{first_name}},                             │
│ Welcome aboard! We're thrilled to have you...  │
│                                                │
│ **CTA:** [Start Your Free Trial]               │
│ **Send:** Immediately after signup              │
╰────────────────────────────────────────────────╯
```

## Testing

```bash
pytest test_app.py -v
```
