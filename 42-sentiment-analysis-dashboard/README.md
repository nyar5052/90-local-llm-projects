# 💬 Sentiment Analysis Dashboard

Analyze sentiment of text files (reviews, feedback, comments) using a local Gemma 4 LLM.

## Features

- **Multi-format Output**: Table, JSON, or summary views
- **Confidence Scoring**: Each analysis includes a confidence percentage
- **Key Phrase Extraction**: Identifies important phrases driving sentiment
- **Batch Processing**: Analyze multiple entries from a single file
- **Progress Tracking**: Real-time progress bar during analysis

## Prerequisites

- Python 3.10+
- [Ollama](https://ollama.ai/) running locally with Gemma 4 model

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
# Table format (default)
python app.py --file reviews.txt --format table

# JSON output
python app.py --file feedback.txt --format json

# Summary only
python app.py -f reviews.txt -fmt summary
```

## Input Format

One review/feedback entry per line in a text file:

```
This product is amazing! Best purchase ever.
Terrible quality, broke after one day.
It's okay, nothing special but works fine.
```

## Example Output

```
💬 Sentiment Analysis Dashboard
✓ Loaded 3 text entries from reviews.txt

┌───┬─────────────────────────────┬───────────┬────────────┬──────────────────────┐
│ # │ Text                        │ Sentiment │ Confidence │ Summary              │
├───┼─────────────────────────────┼───────────┼────────────┼──────────────────────┤
│ 1 │ This product is amazing!... │ 😊 Positive │ 95%       │ Very positive review │
│ 2 │ Terrible quality, broke...  │ 😞 Negative │ 88%       │ Negative about quality│
│ 3 │ It's okay, nothing special  │ 😐 Neutral  │ 72%       │ Mixed/neutral opinion │
└───┴─────────────────────────────┴───────────┴────────────┴──────────────────────┘

📊 Overall Summary
  Total Entries: 3
  😊 Positive: 1 (33%)
  😞 Negative: 1 (33%)
  😐 Neutral: 1 (33%)
  Average Confidence: 85%
```

## Testing

```bash
pytest test_app.py -v
```
