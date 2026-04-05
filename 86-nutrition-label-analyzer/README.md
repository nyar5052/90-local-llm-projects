# 86 - Nutrition Label Analyzer

> **⚠️ DISCLAIMER: This tool is for EDUCATIONAL purposes ONLY. All nutrition data and health insights are AI-generated ESTIMATES and may be inaccurate. This is NOT medical or dietary advice. Always consult a qualified healthcare professional or registered dietitian before making dietary changes or health decisions.**

Analyzes food items and nutrition labels using a local LLM to provide estimated nutritional breakdowns, health scores, and actionable insights.

## Features

- **Food analysis**: Get estimated nutrition data for any food item by name
- **Label analysis**: Paste or provide nutrition label text for a detailed health assessment
- **Food comparison**: Compare multiple food items side-by-side to identify the healthiest option
- **Health scoring**: Each food receives a 1–10 health score with explanation
- **Rich output**: Color-coded console display with structured nutritional information

## Prerequisites

- Python 3.10+
- [Ollama](https://ollama.ai/) running locally with a model pulled (e.g., `ollama pull llama3.2`)

## Setup

```bash
cd 86-nutrition-label-analyzer
pip install -r requirements.txt
```

## Usage

### Analyze a food item

```bash
python app.py analyze --food "Big Mac"
```

### Analyze a nutrition label file

```bash
python app.py label --file nutrition.txt
```

### Compare multiple foods

```bash
python app.py compare --foods "Big Mac,Grilled Chicken Salad"
```

## Running Tests

```bash
pytest test_app.py -v
```

## How It Works

1. **Analyze** sends the food item name to a local LLM with a structured prompt requesting calorie estimates, macronutrients, vitamins/minerals, a health score, pros/cons, and healthier alternatives.
2. **Label** reads nutrition label text from a file and sends it to the LLM for a health assessment including key concerns and recommendations.
3. **Compare** sends multiple food items to the LLM for a side-by-side nutritional comparison with a recommendation for the healthiest choice.

## ⚠️ Important Limitations

- All nutritional values are **AI-generated estimates** and may differ significantly from actual values.
- The LLM may provide inaccurate or outdated nutrition information.
- Health scores are subjective and based on general dietary guidelines — individual needs vary.
- This tool does **not** account for food allergies, intolerances, or medical conditions.
- **Never use this as a substitute for professional medical or dietary advice.**
