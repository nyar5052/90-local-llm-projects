# 🎁 Gift Recommendation Bot

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![LLM](https://img.shields.io/badge/LLM-Ollama%2FGemma4-orange.svg)
![UI](https://img.shields.io/badge/UI-Streamlit-red.svg)

> Find the perfect gift for any occasion with AI-powered personalized suggestions, wishlist management, and an occasion calendar.

## ✨ Features

- **14 Occasions** — Birthday, Christmas, wedding, graduation, and more
- **10 Relationship Types** — Partner, parent, friend, colleague, etc.
- **Budget Aware** — Suggestions within your price range ($5-$10,000)
- **Interest-Based** — Personalized to recipient's hobbies
- **Price Comparison** — Compare prices across retailers
- **Wishlist Management** — Track gift ideas per person
- **Occasion Calendar** — Never miss an important date
- **Detailed Info** — Where to buy and creative presentation ideas
- **Streamlit Web UI** — Full-featured browser interface

## 📦 Installation

```bash
pip install -r requirements.txt
```

## 🚀 CLI Usage

```bash
# Get gift recommendations
python -m gift_recommender.cli recommend --occasion birthday --budget 50 --interests "gaming,cooking"

# Manage wishlists
python -m gift_recommender.cli wishlist-add --person "Mom" --gift "Cookbook" --price "$25"
python -m gift_recommender.cli wishlist-show --person "Mom"

# Occasion calendar
python -m gift_recommender.cli calendar-add --person "Mom" --occasion birthday --date 2025-03-15
python -m gift_recommender.cli calendar-show --days 30
```

## 🌐 Web UI

```bash
streamlit run src/gift_recommender/web_ui.py
```

The web UI provides:
- 🎁 Gift recommendation with form inputs
- 💰 Price comparison tool
- 📋 Wishlist management per person
- 📅 Occasion calendar with reminders

## 🧪 Running Tests

```bash
python -m pytest tests/ -v
```

## 📁 Project Structure

```
08-gift-recommendation-bot/
├── src/
│   └── gift_recommender/
│       ├── __init__.py       # Package metadata
│       ├── core.py           # Core business logic
│       ├── cli.py            # Click CLI interface
│       ├── web_ui.py         # Streamlit web interface
│       ├── config.py         # Configuration management
│       └── utils.py          # Helper utilities
├── tests/
│   ├── __init__.py
│   ├── test_core.py          # Core logic tests
│   └── test_cli.py           # CLI tests
├── config.yaml               # Default configuration
├── setup.py                  # Package setup
├── requirements.txt          # Dependencies
├── Makefile                  # Common commands
├── .env.example              # Example environment variables
└── README.md                 # This file
```
