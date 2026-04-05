# 📰 News Digest Generator

![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![LLM](https://img.shields.io/badge/LLM-Ollama%2FGemma4-green)
![CLI](https://img.shields.io/badge/CLI-Click-orange)
![Web](https://img.shields.io/badge/Web-Streamlit-red)
![Tests](https://img.shields.io/badge/tests-pytest-yellow)

AI-powered news digest generator with category tagging, sentiment tracking, trend identification, and daily/weekly digest formats. Includes Streamlit UI with category filters and sentiment charts.

## Features

- **Category Tagging** — Auto-categorize articles into configurable topic categories
- **Sentiment Tracking** — Per-article and overall sentiment analysis
- **Trend Identification** — Discover overarching themes and emerging trends
- **Daily/Weekly Formats** — Choose between digest styles
- **Streamlit Web UI** — Source folder selector, digest preview, category filters
- **Batch Processing** — Process all `.txt` files in a directory
- **Export to File** — Save digests as Markdown files
- **YAML Configuration** — Customizable categories and settings

## Installation

```bash
cd 19-news-digest-generator
pip install -r requirements.txt
ollama serve && ollama pull gemma4
```

## Usage

### CLI

```bash
# Daily digest (default)
python -m src.news_digest.cli --sources news_folder/

# Weekly digest with sentiment
python -m src.news_digest.cli --sources news_folder/ --format weekly --sentiment

# Custom topic count with export
python -m src.news_digest.cli --sources news_folder/ --topics 3 --output digest.md
```

### Web UI

```bash
streamlit run src/news_digest/web_ui.py
```

### CLI Options

| Option        | Required | Default  | Description                            |
|---------------|----------|----------|----------------------------------------|
| `--sources`   | Yes      | —        | Path to folder of `.txt` news files    |
| `--topics`    | No       | `5`      | Number of topic groups                 |
| `--output`    | No       | —        | Save digest to file                    |
| `--format`    | No       | `daily`  | Digest format: daily / weekly          |
| `--sentiment` | No       | —        | Include sentiment analysis             |
| `--config`    | No       | —        | Path to config.yaml                    |
| `--verbose`   | No       | —        | Enable debug logging                   |

## Testing

```bash
python -m pytest tests/ -v
```

## Project Structure

```
19-news-digest-generator/
├── src/news_digest/
│   ├── __init__.py
│   ├── core.py              # Categorization & digest logic
│   ├── cli.py               # Click CLI interface
│   ├── web_ui.py            # Streamlit web interface
│   ├── config.py            # Configuration management
│   └── utils.py             # Formatting helpers
├── tests/
│   ├── __init__.py
│   ├── test_core.py
│   └── test_cli.py
├── config.yaml
├── setup.py
├── requirements.txt
├── Makefile
├── .env.example
└── README.md
```
