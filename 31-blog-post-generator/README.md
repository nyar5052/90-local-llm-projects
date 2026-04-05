# Blog Post Generator

Generate SEO-friendly blog posts from a topic and keywords using a local Gemma 4 LLM via Ollama.

## Features

- **SEO Optimization**: Generates posts with keyword placement in headings, meta descriptions, and natural keyword integration
- **Multiple Tones**: Professional, casual, technical, friendly, or persuasive writing styles
- **Configurable Length**: Specify target word count for your blog post
- **Markdown Output**: Clean, properly structured markdown with headings, sections, and formatting
- **File Export**: Save generated posts directly to a file

## Prerequisites

- Python 3.10+
- [Ollama](https://ollama.ai/) running locally with the Gemma 4 model
- Start Ollama: `ollama serve`
- Pull model: `ollama pull gemma4`

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
# Basic usage
python app.py --topic "AI in Healthcare"

# With keywords and tone
python app.py --topic "AI in Healthcare" --keywords "ML,diagnosis,patient care" --tone professional --length 800

# Save to file
python app.py --topic "Cloud Computing Trends" --keywords "AWS,Azure,serverless" --tone technical -o blog_post.md
```

### Options

| Option | Description | Default |
|--------|-------------|---------|
| `--topic` | Blog post topic (required) | - |
| `--keywords` | Comma-separated SEO keywords | None |
| `--tone` | Writing tone (professional/casual/technical/friendly/persuasive) | professional |
| `--length` | Approximate word count | 800 |
| `-o, --output` | Save output to file | None |

## Example Output

```
╭─ Generated Blog Post ─────────────────────────╮
│ # AI in Healthcare: Transforming Patient Care  │
│                                                │
│ > Discover how artificial intelligence and     │
│ > machine learning are revolutionizing...      │
│                                                │
│ ## Introduction                                │
│ The healthcare industry is undergoing...        │
│                                                │
│ ## How ML Powers Modern Diagnosis              │
│ Machine learning algorithms can analyze...      │
│ ...                                            │
╰────────────────────────────────────────────────╯
```

## Testing

```bash
pytest test_app.py -v
```
