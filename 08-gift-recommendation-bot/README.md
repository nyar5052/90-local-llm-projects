# 🎁 Gift Recommendation Bot

> Find the perfect gift for any occasion with AI-powered personalized suggestions.

## ✨ Features

- **14 Occasions** — Birthday, Christmas, wedding, graduation, and more
- **10 Relationship Types** — Partner, parent, friend, colleague, etc.
- **Budget Aware** — Suggestions within your price range ($5-$10,000)
- **Interest-Based** — Personalized to recipient's hobbies and interests
- **Detailed Info** — Get specifics on where to buy and how to present
- **Mix of Ideas** — Practical, fun, and sentimental options

## 📦 Installation

```bash
pip install -r requirements.txt
```

## 🚀 Usage

```bash
# Birthday gift for a friend
python app.py --occasion birthday --budget 50 --interests "gaming,cooking"

# Christmas gift for partner
python app.py --occasion christmas --relationship partner --budget 100 --interests "reading,travel"

# Graduation gift with age context
python app.py --occasion graduation --relationship child --budget 75 --age "18"
```

### Example Output

```
╭─ 🎁 Gift Recommendations ───────────────────╮
│ 1. **Custom Cookbook** ($25-35)                │
│    Perfect for the cooking enthusiast...      │
│                                               │
│ 2. **Gaming Headset** ($40-50)                │
│    Great for immersive gaming sessions...     │
╰───────────────────────────────────────────────╯

🔍 More about: Gaming Headset
╭─ 🎁 Gaming Headset ─────────────────────────╮
│ **Top picks under $50:**                      │
│ - HyperX Cloud Stinger ($39.99)              │
│ - SteelSeries Arctis 1 ($49.99)              │
╰───────────────────────────────────────────────╯
```

## 🧪 Running Tests

```bash
pytest test_app.py -v
```

## 📁 Project Structure

```
08-gift-recommendation-bot/
├── app.py              # Main application
├── requirements.txt    # Dependencies
├── test_app.py         # Unit tests
└── README.md           # This file
```
