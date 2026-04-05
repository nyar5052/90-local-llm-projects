# 🍽️ Meal Planner Bot

> Generate personalized weekly meal plans with detailed recipes using a local LLM.

## ✨ Features

- **10 Diet Types** — Omnivore, vegetarian, vegan, keto, paleo, and more
- **Allergy Aware** — Specify allergies to exclude dangerous ingredients
- **Calorie Targets** — Set daily calorie goals for weight management
- **Detailed Recipes** — Get full recipes with ingredients, steps, and nutrition info
- **Flexible Duration** — Plan meals for 1 to 14 days
- **Interactive Mode** — Request detailed recipes for any suggested meal

## 📦 Installation

```bash
pip install -r requirements.txt
```

## 🚀 Usage

```bash
# Basic 7-day vegetarian plan
python app.py --diet vegetarian --days 7

# Keto plan with allergies
python app.py --diet keto --days 5 --allergies "nuts,dairy"

# Vegan plan with calorie target
python app.py --diet vegan --days 7 --calories 1800
```

### Example Output

```
╭─ 📋 Your Meal Plan ──────────────────────────╮
│ ## Day 1                                      │
│ **Breakfast:** Avocado Toast (350 cal)         │
│ **Lunch:** Quinoa Buddha Bowl (450 cal)        │
│ **Dinner:** Lentil Curry with Rice (550 cal)   │
│ **Snack:** Mixed Fruit Smoothie (200 cal)      │
╰───────────────────────────────────────────────╯

🍳 Get recipe for: Lentil Curry with Rice
╭─ 📖 Recipe: Lentil Curry with Rice ──────────╮
│ **Ingredients:** ...                          │
│ **Steps:** ...                                │
╰───────────────────────────────────────────────╯
```

## 🧪 Running Tests

```bash
pytest test_app.py -v
```

## 📁 Project Structure

```
03-meal-planner-bot/
├── app.py              # Main application
├── requirements.txt    # Dependencies
├── test_app.py         # Unit tests
└── README.md           # This file
```
