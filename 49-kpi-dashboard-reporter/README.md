# 📊 KPI Dashboard Reporter

Generate narrative KPI reports from metrics data with trend analysis and alerts using a local Gemma 4 LLM.

## Features

- **Trend Analysis**: Automatic period-over-period comparison
- **Alert System**: Flags KPIs with >10% change
- **Visual Dashboard**: Color-coded trend indicators (↑↓→)
- **Narrative Reports**: LLM-generated insights and recommendations
- **Flexible Periods**: Monthly, quarterly, or custom period labels

## Prerequisites

- Python 3.10+
- [Ollama](https://ollama.ai/) running locally with Gemma 4 model

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
# Monthly KPI report
python app.py --file kpis.csv --period monthly

# Quarterly report without alerts
python app.py -f kpis.csv -p Q1-2024 --no-alerts
```

## Input Format

CSV with period column and numeric KPI columns:

```csv
month,revenue,customers,churn_rate,nps_score
Jan,100000,500,5.2,72
Feb,110000,520,4.8,75
Mar,105000,510,5.5,70
```

## Example Output

```
📊 KPI Dashboard Reporter - monthly
✓ Loaded 4 periods from kpis.csv

┌──────────────┬──────────┬──────────┬──────────┬─────────┬───────┬──────────┐
│ KPI          │   Latest │ Previous │   Change │ Change% │ Trend │      Avg │
├──────────────┼──────────┼──────────┼──────────┼─────────┼───────┼──────────┤
│ revenue      │ 120,000  │ 105,000  │ +15,000  │ +14.3%  │  ↑    │ 108,750  │
│ customers    │     550  │     510  │     +40  │  +7.8%  │  ↑    │     520  │
│ churn_rate   │    4.20  │    5.50  │   -1.30  │ -23.6%  │  ↓    │    4.93  │
│ nps_score    │   78.00  │   70.00  │   +8.00  │ +11.4%  │  ↑    │   73.75  │
└──────────────┴──────────┴──────────┴──────────┴─────────┴───────┴──────────┘

🔔 Alerts
  ⚠️ revenue increased by 14.3%
  ⚠️ churn_rate decreased by 23.6%
  ⚠️ nps_score increased by 11.4%
```

## Testing

```bash
pytest test_app.py -v
```
