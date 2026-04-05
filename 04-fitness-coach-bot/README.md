# 💪 Fitness Coach Bot

> AI-powered personal fitness trainer that creates customized workout plans using a local LLM.

## ✨ Features

- **3 Fitness Levels** — Beginner, intermediate, and advanced programs
- **6 Goal Types** — Weight loss, muscle gain, endurance, flexibility, strength, general fitness
- **Equipment Aware** — Plans tailored to your available equipment
- **Customizable Schedule** — Set workout days per week and session duration
- **Exercise Details** — Get detailed form instructions for any exercise
- **Safety First** — Includes warm-ups, cool-downs, and injury prevention tips

## 📦 Installation

```bash
pip install -r requirements.txt
```

## 🚀 Usage

```bash
# Basic usage
python app.py --level beginner --goal "weight-loss" --equipment "dumbbells,mat"

# Advanced with custom schedule
python app.py --level advanced --goal "muscle-gain" --equipment "barbell,rack,dumbbells" --days 5 --duration 60

# Bodyweight only
python app.py --level intermediate --goal "general-fitness" --equipment "bodyweight"
```

### Example Output

```
╭─ 🏋️ Your Workout Plan ──────────────────────╮
│ ## Day 1 - Upper Body                        │
│ **Warm-up:** 5 min light cardio              │
│ - Push-ups: 3 sets × 10 reps (60s rest)      │
│ - Dumbbell Rows: 3 sets × 12 reps            │
│ **Cool-down:** 5 min stretching              │
╰──────────────────────────────────────────────╯

🔍 Exercise details for: Push-ups
╭─ 📖 Push-ups ────────────────────────────────╮
│ **Proper Form:** Start in plank position...  │
│ **Common Mistakes:** Sagging hips...          │
╰──────────────────────────────────────────────╯
```

## 🧪 Running Tests

```bash
pytest test_app.py -v
```

## 📁 Project Structure

```
04-fitness-coach-bot/
├── app.py              # Main application
├── requirements.txt    # Dependencies
├── test_app.py         # Unit tests
└── README.md           # This file
```
