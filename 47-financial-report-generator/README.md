# 💰 Financial Report Generator

Generate professional narrative financial reports from CSV data using a local Gemma 4 LLM.

## Features

- **Auto Metric Computation**: Calculates totals, averages, min/max from data
- **Board-Ready Reports**: Professional narrative suitable for presentations
- **Income & Expense Analysis**: Detailed breakdown of financial performance
- **Key Ratios**: Financial indicators and ratio analysis
- **Period Comparison**: Period-over-period trend analysis

## Prerequisites

- Python 3.10+
- [Ollama](https://ollama.ai/) running locally with Gemma 4 model

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
# Full financial report
python app.py --file financials.csv --period Q4-2024

# Executive summary only
python app.py -f financials.csv -p Q4-2024 --summary
```

## Input Format

CSV with financial data columns:

```csv
month,revenue,expenses,net_income
October,500000,350000,150000
November,550000,380000,170000
December,600000,400000,200000
```

## Example Output

```
💰 Financial Report Generator - Q4-2024
✓ Loaded 3 records from financials.csv

┌──────────────┬──────────────┬──────────────┬──────────────┐
│ Metric       │        Total │      Average │       Latest │
├──────────────┼──────────────┼──────────────┼──────────────┤
│ revenue      │ $1,650,000   │   $550,000   │   $600,000   │
│ expenses     │ $1,130,000   │   $376,667   │   $400,000   │
│ net_income   │   $520,000   │   $173,333   │   $200,000   │
└──────────────┴──────────────┴──────────────┴──────────────┘

╭── 📋 Financial Report - Q4-2024 ──╮
│ # Executive Summary                │
│ Q4-2024 showed strong growth...    │
╰────────────────────────────────────╯
```

## Testing

```bash
pytest test_app.py -v
```
