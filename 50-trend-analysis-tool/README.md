# 📈 Trend Analysis Tool

Analyze trends from text data (articles, reports, documents) to identify emerging topics and sentiment shifts using a local Gemma 4 LLM.

## Features

- **Topic Extraction**: Identifies key topics with frequency and trend direction
- **Sentiment Tracking**: Analyzes sentiment patterns across documents
- **Trend Classification**: Emerging, growing, stable, or declining labels
- **Comprehensive Reports**: LLM-generated trend analysis with predictions
- **Multi-format Support**: Reads .txt, .md, .text, .csv, .log files

## Prerequisites

- Python 3.10+
- [Ollama](https://ollama.ai/) running locally with Gemma 4 model

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
# Analyze articles directory
python app.py --dir articles/ --timeframe "last month"

# Without sentiment analysis
python app.py -d reports/ -t "Q1-2024" --no-sentiment
```

## Input Format

Place text files (.txt, .md) in a directory:

```
articles/
├── ai-in-healthcare.txt
├── cybersecurity-trends.txt
├── remote-work-update.txt
└── market-analysis.md
```

## Example Output

```
📈 Trend Analysis Tool
✓ Loaded 15 documents from articles/
Timeframe: last month

┌───┬──────────────────────┬───────────┬──────────┬─────────────────────────────┐
│ # │ Topic                │ Frequency │ Trend    │ Description                 │
├───┼──────────────────────┼───────────┼──────────┼─────────────────────────────┤
│ 1 │ AI in Healthcare     │ 🔥 High   │ Emerging │ AI applications in medical  │
│ 2 │ Cybersecurity        │ 📈 Medium │ Growing  │ Rising security threats     │
│ 3 │ Remote Work          │ 📊 Low    │ Stable   │ Hybrid work models          │
└───┴──────────────────────┴───────────┴──────────┴─────────────────────────────┘

💭 Sentiment Overview
  Overall: Mixed
  😊 Positive: 8 | 😞 Negative: 4 | 😐 Neutral: 3
```

## Testing

```bash
pytest test_app.py -v
```
