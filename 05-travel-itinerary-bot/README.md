# ✈️ Travel Itinerary Bot

> AI-powered vacation planner that creates detailed day-by-day travel itineraries using a local LLM.

## ✨ Features

- **Global Destinations** — Plan trips to any destination worldwide
- **3 Budget Levels** — Budget, moderate, and luxury options
- **Interest-Based Planning** — Tailor activities to your interests
- **Day-by-Day Schedule** — Morning, afternoon, and evening activities
- **Cost Estimates** — Budget-aware recommendations with price estimates
- **Place Details** — Get detailed info about any attraction mentioned

## 📦 Installation

```bash
pip install -r requirements.txt
```

## 🚀 Usage

```bash
# Basic trip
python app.py --destination "Tokyo" --days 5 --budget moderate

# With interests
python app.py --destination "Paris" --days 7 --budget luxury --interests "food,art,history"

# Group travel
python app.py --destination "Barcelona" --days 4 --budget budget --travelers 3
```

### Example Output

```
╭─ 🗺️ Tokyo — 5-Day Itinerary ────────────────╮
│ ## Day 1 - Arrival & Shibuya                  │
│ **Morning:** Arrive at Narita Airport          │
│ **Afternoon:** Explore Shibuya Crossing        │
│ **Evening:** Dinner in Shinjuku                │
│ **Est. Cost:** $80-120                         │
╰───────────────────────────────────────────────╯

📍 Tell me about: Senso-ji Temple
╭─ 📍 Senso-ji Temple ─────────────────────────╮
│ Tokyo's oldest Buddhist temple...             │
╰───────────────────────────────────────────────╯
```

## 🧪 Running Tests

```bash
pytest test_app.py -v
```

## 📁 Project Structure

```
05-travel-itinerary-bot/
├── app.py              # Main application
├── requirements.txt    # Dependencies
├── test_app.py         # Unit tests
└── README.md           # This file
```
