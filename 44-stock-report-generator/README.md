# 📈 Stock Report Generator

Generate professional stock analysis reports from CSV data using a local Gemma 4 LLM.

## Features

- **Technical Metrics**: Calculates SMA, volatility, returns, and more
- **Trend Analysis**: Identifies bullish/bearish patterns
- **Narrative Reports**: LLM-generated professional analysis
- **Rich Display**: Formatted tables with color-coded indicators
- **Support/Resistance**: Key price levels identification

## Prerequisites

- Python 3.10+
- [Ollama](https://ollama.ai/) running locally with Gemma 4 model

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
# Generate report
python app.py --file stock_data.csv --ticker AAPL

# Short flags
python app.py -f msft_prices.csv -t MSFT
```

## Input Format

CSV with at least a `Close` price column:

```csv
Date,Open,High,Low,Close,Volume
2024-01-02,150.00,152.00,149.00,151.00,1000000
2024-01-03,151.00,155.00,150.00,154.00,1200000
```

## Example Output

```
📈 Stock Report Generator - AAPL

┌──────────────────┬──────────────┐
│ Metric           │        Value │
├──────────────────┼──────────────┤
│ Current Price    │      $185.50 │
│ Period High      │      $192.00 │
│ Period Low       │      $170.25 │
│ Change           │    ↑  8.75%  │
│ SMA (5)          │      $183.20 │
│ SMA (20)         │      $178.90 │
│ Volatility       │        $5.42 │
└──────────────────┴──────────────┘

╭── 📋 AAPL Analysis Report ──╮
│ # Executive Summary          │
│ AAPL shows a strong bullish  │
│ trend with 8.75% gain...     │
╰──────────────────────────────╯
```

## Testing

```bash
pytest test_app.py -v
```
