# 📋 Survey Response Analyzer

Analyze survey free-text responses to extract themes, insights, and actionable recommendations using a local Gemma 4 LLM.

## Features

- **Theme Extraction**: Automatically groups responses into major themes
- **Sentiment Detection**: Identifies sentiment per theme (positive/negative/mixed)
- **Detailed Reports**: Brief or detailed analysis modes
- **Multi-column Support**: Analyzes multiple text columns from CSV
- **Auto-detection**: Identifies free-text columns automatically

## Prerequisites

- Python 3.10+
- [Ollama](https://ollama.ai/) running locally with Gemma 4 model

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
# Brief analysis
python app.py --file survey_responses.csv --report brief

# Detailed report with insights
python app.py --file survey_responses.csv --report detailed

# Analyze specific column
python app.py -f responses.csv -c "feedback" -r detailed
```

## Input Format

CSV file with at least one free-text column:

```csv
id,feedback,rating
1,The onboarding process was very smooth,5
2,Customer support was slow and unresponsive,2
3,Great product but documentation needs work,4
```

## Example Output

```
📋 Survey Response Analyzer
✓ Loaded 50 responses from survey.csv

Analyzing columns: feedback

Column: feedback (50 responses)

┌───┬──────────────────┬───────────┬───────────┬────────────────────────────────┐
│ # │ Theme            │ Responses │ Sentiment │ Description                    │
├───┼──────────────────┼───────────┼───────────┼────────────────────────────────┤
│ 1 │ Customer Support │ 15        │ Negative  │ Slow response times            │
│ 2 │ Product Quality  │ 20        │ Positive  │ Users love core features       │
│ 3 │ Pricing          │ 10        │ Mixed     │ Value concerns vs competitors  │
└───┴──────────────────┴───────────┴───────────┴────────────────────────────────┘
```

## Testing

```bash
pytest test_app.py -v
```
