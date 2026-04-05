# 🍽️ Nutrition Label Analyzer

![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)
![License MIT](https://img.shields.io/badge/License-MIT-green)
![Streamlit](https://img.shields.io/badge/Streamlit-Web_UI-FF4B4B?logo=streamlit&logoColor=white)
![CLI](https://img.shields.io/badge/CLI-Click-orange?logo=gnubash&logoColor=white)

---

> ## ⚕️ MEDICAL DISCLAIMER
>
> **⚠️ This tool is for EDUCATIONAL purposes ONLY.**
>
> All nutrition data and health insights are **AI-generated ESTIMATES** and may be
> **inaccurate or incomplete**. This is **NOT** medical, dietary, or health advice.
>
> - Do **NOT** use this tool to make medical or dietary decisions.
> - Do **NOT** rely on allergen detection for allergy safety — always verify with official sources.
> - **Always consult a qualified healthcare professional or registered dietitian** before
>   making dietary changes or health decisions.
>
> The authors and contributors accept **no liability** for any consequences arising from
> the use of this tool.

---

## 📖 About

**Nutrition Label Analyzer** is an AI-powered nutrition analysis and tracking toolkit that
uses a local LLM (via [Ollama](https://ollama.ai/)) to provide estimated nutritional
breakdowns, health scores, allergen detection, meal tracking, and dietary goal management.

Available as both a **Rich CLI** and a **Streamlit Web UI**.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│                  User Interface                 │
│  ┌──────────────────┐  ┌──────────────────────┐ │
│  │   Click CLI      │  │  Streamlit Web UI    │ │
│  │  (cli.py)        │  │  (web_ui.py)         │ │
│  └────────┬─────────┘  └────────┬─────────────┘ │
│           │                     │               │
│  ┌────────▼─────────────────────▼─────────────┐ │
│  │              Core Logic (core.py)          │ │
│  │  • Food Analysis    • Daily Values         │ │
│  │  • Label Analysis   • Meal Tracking        │ │
│  │  • Food Comparison  • Allergen Checking    │ │
│  │  • Dietary Goals    • %DV Calculations     │ │
│  └────────┬───────────────────────────────────┘ │
│           │                                     │
│  ┌────────▼───────────────────────────────────┐ │
│  │         common.llm_client (Ollama)         │ │
│  │  generate() / check_ollama_running()       │ │
│  └────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────┘
```

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🍽️ **Food Analysis** | Get AI-estimated nutrition data for any food item |
| 📋 **Label Analysis** | Parse nutrition label text for a detailed health assessment |
| ⚖️ **Food Comparison** | Compare multiple foods side-by-side |
| 📊 **Daily Tracking** | Track meals and monitor daily nutrient intake |
| ⚠️ **Allergen Detection** | Scan food descriptions for the FDA Big 9 allergens |
| 🎯 **Dietary Goals** | Choose from preset macro goals (Balanced, Keto, High Protein, etc.) |
| 📈 **%Daily Values** | Calculate FDA percent Daily Values for any nutrient set |
| 🏥 **Health Scoring** | Each food receives a 1–10 health score with explanation |
| 🎨 **Rich Output** | Color-coded console display with structured information |
| 🌐 **Web UI** | Interactive Streamlit dashboard for all features |

---

## 📋 Prerequisites

- **Python 3.10+**
- **[Ollama](https://ollama.ai/)** running locally with a model pulled:
  ```bash
  ollama pull llama3
  ```

---

## 🚀 Installation

### Option 1: pip install (editable)

```bash
cd 86-nutrition-label-analyzer
pip install -e ".[dev]"
```

### Option 2: requirements.txt

```bash
cd 86-nutrition-label-analyzer
pip install -r requirements.txt
```

### Option 3: Makefile

```bash
make install
```

---

## 💻 CLI Usage

All commands are available through the `nutrition-analyzer` entry point or via
`python -m nutrition_analyzer.cli`.

### Analyze a food item

```bash
nutrition-analyzer analyze --food "Big Mac"
```

### Analyze a nutrition label file

```bash
nutrition-analyzer label --file nutrition.txt
```

### Compare multiple foods

```bash
nutrition-analyzer compare --foods "Big Mac,Grilled Chicken Salad,Caesar Salad"
```

### Calculate %Daily Values

```bash
nutrition-analyzer daily-values --food "calories=550,total_fat=30,sodium=1000"
```

### Track meals

```bash
# Add a meal
nutrition-analyzer track --meal "Lunch: calories=600,protein=30,carbs=50,fat=20"

# View summary
nutrition-analyzer track --summary

# Reset tracker
nutrition-analyzer track --reset
```

### Allergen check

```bash
nutrition-analyzer allergen-check --food "peanut butter on wheat bread with milk"
nutrition-analyzer allergen-check --food "oat milk smoothie" --allergens "milk,soy,wheat"
```

### Dietary goals

```bash
# Show all presets
nutrition-analyzer goals --show

# View a specific preset
nutrition-analyzer goals --preset keto
```

---

## 🌐 Web UI Usage

Launch the Streamlit dashboard:

```bash
streamlit run src/nutrition_analyzer/web_ui.py
```

Or:

```bash
make run-web
```

The web interface provides four pages accessible from the sidebar:

- **🍽️ Food Analysis** — Enter a food item, paste a nutrition label, or compare foods
- **📊 Daily Tracker** — Add meals with nutrient values, view running totals and remaining budget
- **⚠️ Allergen Check** — Scan food descriptions against selectable allergens
- **🎯 Dietary Goals** — Browse preset macro goals with calorie and gram breakdowns

---

## ⚙️ Configuration

Application settings are stored in `config.yaml`:

```yaml
llm:
  model: "llama3"
  temperature: 0.3
  max_tokens: 2048

daily_values:
  calories: 2000
  total_fat_g: 78
  sodium_mg: 2300
  ...
```

Environment variables can be set via `.env` (see `.env.example`):

```
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3
LOG_LEVEL=INFO
```

---

## 🧪 Testing

Run the full test suite:

```bash
python -m pytest tests/ -v --tb=short
```

Or via Makefile:

```bash
make test
```

Test coverage:

```bash
python -m pytest tests/ -v --cov=src/nutrition_analyzer --cov-report=term-missing
```

---

## 📁 Project Structure

```
86-nutrition-label-analyzer/
├── app.py                          # Original standalone app
├── config.yaml                     # Application configuration
├── setup.py                        # Package setup
├── requirements.txt                # Dependencies
├── Makefile                        # Common tasks
├── .env.example                    # Environment variable template
├── README.md                       # This file
├── src/
│   ├── __init__.py
│   └── nutrition_analyzer/
│       ├── __init__.py             # Package metadata & version
│       ├── core.py                 # Core logic: analysis, tracking, allergens, goals
│       ├── cli.py                  # Click CLI interface
│       └── web_ui.py               # Streamlit web dashboard
├── tests/
│   ├── __init__.py
│   ├── test_core.py                # Core module tests
│   └── test_cli.py                 # CLI command tests
└── test_app.py                     # Original app tests
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Run tests (`make test`)
4. Commit your changes
5. Open a Pull Request

---

> ## ⚕️ DISCLAIMER (REPEATED FOR EMPHASIS)
>
> **This tool is for EDUCATIONAL purposes ONLY.**
>
> All nutrition information is **AI-generated** and may be **inaccurate**.
> This is **NOT** medical or dietary advice. **Always consult a qualified
> healthcare professional or registered dietitian** before making any
> dietary changes or health decisions.
>
> Allergen detection is a **heuristic text search** and must **NOT** be
> relied upon for allergy safety. Always verify allergen information from
> official product labeling and manufacturer sources.

---

*Built with ❤️ using [Ollama](https://ollama.ai/), [Click](https://click.palletsprojects.com/), [Rich](https://rich.readthedocs.io/), and [Streamlit](https://streamlit.io/).*
