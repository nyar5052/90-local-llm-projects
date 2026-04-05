"""Helper utilities for Fitness Coach Bot."""

import json
import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


# ── Workout Logging ──────────────────────────────────────────────────────────

def load_workout_log(filepath: str = "workout_log.json") -> list[dict]:
    p = Path(filepath)
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return []


def log_workout(
    exercise: str,
    sets: int,
    reps: int,
    weight: float | None = None,
    duration_min: int | None = None,
    notes: str = "",
    filepath: str = "workout_log.json",
) -> dict:
    """Log a workout entry."""
    log = load_workout_log(filepath)
    entry = {
        "exercise": exercise,
        "sets": sets,
        "reps": reps,
        "weight": weight,
        "duration_min": duration_min,
        "notes": notes,
        "date": datetime.now().isoformat(),
    }
    log.append(entry)
    Path(filepath).write_text(json.dumps(log, indent=2), encoding="utf-8")
    logger.info("Logged workout: %s %dx%d", exercise, sets, reps)
    return entry


# ── Progress Tracking ────────────────────────────────────────────────────────

def load_progress(filepath: str = "progress.json") -> list[dict]:
    p = Path(filepath)
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return []


def record_progress(
    weight_kg: float | None = None,
    body_fat_pct: float | None = None,
    notes: str = "",
    filepath: str = "progress.json",
) -> dict:
    """Record a progress entry (body weight, body fat, etc.)."""
    progress = load_progress(filepath)
    entry = {
        "weight_kg": weight_kg,
        "body_fat_pct": body_fat_pct,
        "notes": notes,
        "date": datetime.now().isoformat(),
    }
    progress.append(entry)
    Path(filepath).write_text(json.dumps(progress, indent=2), encoding="utf-8")
    return entry


def get_progress_summary(filepath: str = "progress.json") -> dict:
    """Return a summary of progress (latest, change, entries count)."""
    progress = load_progress(filepath)
    if not progress:
        return {"entries": 0}
    latest = progress[-1]
    first = progress[0]
    summary = {
        "entries": len(progress),
        "latest_weight": latest.get("weight_kg"),
        "latest_body_fat": latest.get("body_fat_pct"),
        "weight_change": None,
    }
    if latest.get("weight_kg") and first.get("weight_kg"):
        summary["weight_change"] = round(latest["weight_kg"] - first["weight_kg"], 1)
    return summary


# ── Exercise Library ─────────────────────────────────────────────────────────

EXERCISE_LIBRARY = {
    "push-ups": {"muscles": "Chest, Shoulders, Triceps", "type": "bodyweight", "difficulty": "beginner"},
    "pull-ups": {"muscles": "Back, Biceps", "type": "bodyweight", "difficulty": "intermediate"},
    "squats": {"muscles": "Quadriceps, Glutes, Hamstrings", "type": "bodyweight", "difficulty": "beginner"},
    "deadlifts": {"muscles": "Back, Glutes, Hamstrings", "type": "barbell", "difficulty": "intermediate"},
    "bench press": {"muscles": "Chest, Shoulders, Triceps", "type": "barbell", "difficulty": "intermediate"},
    "overhead press": {"muscles": "Shoulders, Triceps", "type": "barbell/dumbbell", "difficulty": "intermediate"},
    "lunges": {"muscles": "Quadriceps, Glutes", "type": "bodyweight/dumbbell", "difficulty": "beginner"},
    "plank": {"muscles": "Core", "type": "bodyweight", "difficulty": "beginner"},
    "burpees": {"muscles": "Full Body", "type": "bodyweight", "difficulty": "intermediate"},
    "rows": {"muscles": "Back, Biceps", "type": "barbell/dumbbell", "difficulty": "beginner"},
}


def search_exercises(query: str = "", difficulty: str | None = None) -> list[dict]:
    """Search the exercise library."""
    results = []
    for name, info in EXERCISE_LIBRARY.items():
        if query.lower() in name.lower() or query.lower() in info["muscles"].lower():
            if difficulty is None or info["difficulty"] == difficulty:
                results.append({"name": name, **info})
    return results
