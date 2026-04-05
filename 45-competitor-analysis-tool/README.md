# 🏢 Competitor Analysis Tool

Generate SWOT analysis, competitive comparisons, and strategic recommendations using a local Gemma 4 LLM.

## Features

- **SWOT Analysis**: Strengths, Weaknesses, Opportunities, Threats grid
- **Feature Comparison**: Side-by-side competitor evaluation
- **Market Positioning**: Industry-specific context analysis
- **Strategic Recommendations**: Actionable insights with priority levels
- **Rich Visual Output**: Color-coded panels and formatted tables

## Prerequisites

- Python 3.10+
- [Ollama](https://ollama.ai/) running locally with Gemma 4 model

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
# Full competitive analysis
python app.py --company "Our Product" --competitors "Comp1,Comp2" --industry tech

# SWOT analysis only
python app.py -c "Our SaaS" -comp "Slack,Teams" -i "communication" --swot-only
```

## Example Output

```
🏢 Competitor Analysis Tool
Company: Our Product
Competitors: Comp1, Comp2
Industry: tech

╭── 💪 Strengths ───╮  ╭── ⚠️ Weaknesses ──╮
│ • Strong R&D team  │  │ • Higher pricing   │
│ • AI-first design  │  │ • Smaller team     │
│ • User experience  │  │ • Limited reach    │
╰────────────────────╯  ╰────────────────────╯
╭── 🎯 Opportunities ╮  ╭── 🔥 Threats ──────╮
│ • API marketplace   │  │ • Big tech entry   │
│ • Enterprise tier   │  │ • Price wars       │
│ • Global expansion  │  │ • Talent shortage  │
╰─────────────────────╯  ╰────────────────────╯
```

## Testing

```bash
pytest test_app.py -v
```
