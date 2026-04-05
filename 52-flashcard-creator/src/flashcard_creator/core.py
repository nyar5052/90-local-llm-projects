#!/usr/bin/env python3
"""
Flashcard Creator — Core business logic.

Provides flashcard generation via LLM, deck management, spaced repetition (SM-2),
import/export (JSON & CSV), and review session tracking.
"""

import sys
import os
import json
import csv
import random
import logging
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import yaml

# LLM integration — same pattern as original app.py
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
from common.llm_client import chat, check_ollama_running  # noqa: E402

logger = logging.getLogger("flashcard_creator")

# ---------------------------------------------------------------------------
# System prompt for LLM-based card generation
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """You are an expert educator creating study flashcards.
Generate flashcards in valid JSON format.

Return a JSON object with this structure:
{
  "topic": "Topic Name",
  "cards": [
    {
      "id": 1,
      "front": "Question or term on the front of the card",
      "back": "Answer or definition on the back",
      "hint": "Optional hint",
      "difficulty": "easy|medium|hard",
      "tags": ["tag1", "tag2"]
    }
  ]
}

Return ONLY the JSON, no other text."""


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

class ConfigManager:
    """Loads and provides access to config.yaml settings."""

    _defaults = {
        "llm": {"temperature": 0.7, "max_tokens": 4096},
        "flashcards": {"default_count": 10, "default_difficulty": "medium", "max_cards_per_deck": 500},
        "spaced_repetition": {
            "algorithm": "sm2",
            "initial_ease_factor": 2.5,
            "minimum_ease_factor": 1.3,
            "initial_interval": 1,
            "graduating_interval": 6,
        },
        "storage": {"decks_dir": "./decks", "stats_file": "review_stats.json"},
        "logging": {"level": "INFO", "file": "flashcard_creator.log"},
    }

    def __init__(self, config_path: Optional[str] = None) -> None:
        """Initialize the instance."""
        self._data: dict = {}
        if config_path is None:
            # Look next to the package, then cwd
            candidates = [
                Path(__file__).resolve().parent.parent.parent / "config.yaml",
                Path.cwd() / "config.yaml",
            ]
            for p in candidates:
                if p.is_file():
                    config_path = str(p)
                    break
        if config_path and Path(config_path).is_file():
            with open(config_path, "r", encoding="utf-8") as fh:
                self._data = yaml.safe_load(fh) or {}
            logger.info("Loaded config from %s", config_path)
        else:
            logger.info("No config file found; using defaults")

    def get(self, section: str, key: str, fallback: Optional[Any]=None) -> Any:
        """Retrieve a value."""
        section_data = self._data.get(section, self._defaults.get(section, {}))
        default_val = self._defaults.get(section, {}).get(key, fallback)
        return section_data.get(key, default_val)


# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------

def setup_logging(config: Optional[ConfigManager] = None) -> None:
    """Configure module-level logging based on config."""
    level_name = "INFO"
    log_file = "flashcard_creator.log"
    if config:
        level_name = config.get("logging", "level", "INFO")
        log_file = config.get("logging", "file", "flashcard_creator.log")

    level = getattr(logging, level_name.upper(), logging.INFO)
    handler = logging.FileHandler(log_file, encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
    logger.setLevel(level)
    logger.addHandler(handler)


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass
class Flashcard:
    """A single flashcard with spaced-repetition metadata."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    front: str = ""
    back: str = ""
    hint: str = ""
    difficulty: str = "medium"  # easy | medium | hard
    tags: list[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_reviewed: Optional[str] = None
    ease_factor: float = 2.5
    interval: int = 1          # days until next review
    repetitions: int = 0


@dataclass
class Deck:
    """A named collection of flashcards."""
    name: str = "Untitled"
    description: str = ""
    cards: list[Flashcard] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    tags: list[str] = field(default_factory=list)


@dataclass
class ReviewStats:
    """Aggregated statistics for display."""
    total_cards: int = 0
    cards_reviewed: int = 0
    correct: int = 0
    incorrect: int = 0
    score_pct: float = 0.0
    avg_quality: float = 0.0
    time_elapsed_s: float = 0.0
    cards_by_difficulty: dict = field(default_factory=dict)
    due_cards: int = 0


# ---------------------------------------------------------------------------
# SM-2 Spaced Repetition
# ---------------------------------------------------------------------------

class SpacedRepetition:
    """Implements the SM-2 spaced-repetition algorithm.

    Quality grades:
        0 — complete blackout
        1 — incorrect; remembered after seeing answer
        2 — incorrect; answer seemed easy to recall
        3 — correct with serious difficulty
        4 — correct with some hesitation
        5 — perfect recall
    """

    def __init__(self, config: Optional[ConfigManager] = None) -> None:
        """Initialize the instance."""
        self.min_ef = 1.3
        self.initial_ef = 2.5
        self.initial_interval = 1
        self.graduating_interval = 6
        if config:
            self.min_ef = config.get("spaced_repetition", "minimum_ease_factor", 1.3)
            self.initial_ef = config.get("spaced_repetition", "initial_ease_factor", 2.5)
            self.initial_interval = config.get("spaced_repetition", "initial_interval", 1)
            self.graduating_interval = config.get("spaced_repetition", "graduating_interval", 6)

    def calculate_next_review(self, card: Flashcard, quality: int) -> Flashcard:
        """Update *card* in-place and return it after applying SM-2."""
        quality = max(0, min(5, quality))

        if quality < 3:
            # Failed — reset repetitions
            card.repetitions = 0
            card.interval = self.initial_interval
        else:
            if card.repetitions == 0:
                card.interval = self.initial_interval
            elif card.repetitions == 1:
                card.interval = self.graduating_interval
            else:
                card.interval = int(card.interval * card.ease_factor)
            card.repetitions += 1

        # Update ease factor
        card.ease_factor = card.ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        if card.ease_factor < self.min_ef:
            card.ease_factor = self.min_ef

        card.last_reviewed = datetime.now().isoformat()
        return card

    def get_due_cards(self, deck: Deck) -> list[Flashcard]:
        """Return cards that are due for review right now."""
        now = datetime.now()
        due: list[Flashcard] = []
        for card in deck.cards:
            if card.last_reviewed is None:
                due.append(card)
                continue
            last = datetime.fromisoformat(card.last_reviewed)
            if last + timedelta(days=card.interval) <= now:
                due.append(card)
        return due


# ---------------------------------------------------------------------------
# Review session
# ---------------------------------------------------------------------------

class ReviewSession:
    """Tracks state for a single review session."""

    def __init__(self, deck: Deck, shuffle: bool = True, due_only: bool = False) -> None:
        """Initialize the instance."""
        self.deck = deck
        self.scores: list[int] = []
        self.start_time = datetime.now()
        self.end_time: Optional[datetime] = None
        sr = SpacedRepetition()
        if due_only:
            self.cards = sr.get_due_cards(deck)
        else:
            self.cards = list(deck.cards)
        if shuffle:
            random.shuffle(self.cards)

    def record(self, quality: int) -> None:
        """Record."""
        self.scores.append(max(0, min(5, quality)))

    def finish(self) -> ReviewStats:
        """Finish."""
        self.end_time = datetime.now()
        total = len(self.cards)
        reviewed = len(self.scores)
        correct = sum(1 for q in self.scores if q >= 3)
        incorrect = reviewed - correct
        pct = (correct / reviewed * 100) if reviewed > 0 else 0.0
        avg_q = (sum(self.scores) / reviewed) if reviewed > 0 else 0.0
        elapsed = (self.end_time - self.start_time).total_seconds()
        by_diff: dict[str, int] = {}
        for c in self.cards:
            by_diff[c.difficulty] = by_diff.get(c.difficulty, 0) + 1
        return ReviewStats(
            total_cards=total,
            cards_reviewed=reviewed,
            correct=correct,
            incorrect=incorrect,
            score_pct=pct,
            avg_quality=avg_q,
            time_elapsed_s=elapsed,
            cards_by_difficulty=by_diff,
        )


# ---------------------------------------------------------------------------
# Deck manager
# ---------------------------------------------------------------------------

class DeckManager:
    """Persist and manage multiple decks on disk."""

    def __init__(self, decks_dir: str = "./decks") -> None:
        """Initialize the instance."""
        self.decks_dir = Path(decks_dir)
        self.decks_dir.mkdir(parents=True, exist_ok=True)

    def _deck_path(self, name: str) -> Path:
        """Deck path."""
        safe = name.lower().replace(" ", "_")[:60]
        return self.decks_dir / f"{safe}.json"

    # CRUD -------------------------------------------------------------------

    def create_deck(self, name: str, description: str = "", tags: list[str] | None = None) -> Deck:
        """Create deck."""
        deck = Deck(name=name, description=description, tags=tags or [])
        self._save(deck)
        logger.info("Created deck '%s'", name)
        return deck

    def delete_deck(self, name: str) -> bool:
        """Delete deck."""
        path = self._deck_path(name)
        if path.exists():
            path.unlink()
            logger.info("Deleted deck '%s'", name)
            return True
        return False

    def list_decks(self) -> list[Deck]:
        """List decks."""
        decks: list[Deck] = []
        for fp in sorted(self.decks_dir.glob("*.json")):
            try:
                decks.append(self._load_from_path(fp))
            except Exception:
                logger.warning("Skipping corrupt deck file %s", fp)
        return decks

    def get_deck(self, name: str) -> Optional[Deck]:
        """Get deck."""
        path = self._deck_path(name)
        if path.exists():
            return self._load_from_path(path)
        return None

    # Cards ------------------------------------------------------------------

    def add_card(self, deck_name: str, card: Flashcard) -> Deck:
        """Add card."""
        deck = self.get_deck(deck_name)
        if deck is None:
            deck = self.create_deck(deck_name)
        deck.cards.append(card)
        self._save(deck)
        return deck

    def remove_card(self, deck_name: str, card_id: str) -> Deck:
        """Remove card."""
        deck = self.get_deck(deck_name)
        if deck is None:
            raise ValueError(f"Deck '{deck_name}' not found")
        deck.cards = [c for c in deck.cards if c.id != card_id]
        self._save(deck)
        return deck

    # Import / Export --------------------------------------------------------

    def import_deck(self, filepath: str, fmt: str = "json") -> Deck:
        """Import deck."""
        if fmt == "csv":
            return import_deck_csv(filepath)
        return import_deck_json(filepath)

    def export_deck(self, deck: Deck, filepath: str, fmt: str = "json") -> str:
        """Export deck."""
        if fmt == "csv":
            return export_deck_csv(deck, filepath)
        return export_deck_json(deck, filepath)

    # Merge ------------------------------------------------------------------

    def merge_decks(self, deck_a: Deck, deck_b: Deck, new_name: Optional[str] = None) -> Deck:
        """Merge decks."""
        merged = Deck(
            name=new_name or f"{deck_a.name} + {deck_b.name}",
            description=f"Merged from '{deck_a.name}' and '{deck_b.name}'",
            cards=deck_a.cards + deck_b.cards,
            tags=list(set(deck_a.tags + deck_b.tags)),
        )
        self._save(merged)
        return merged

    # Stats ------------------------------------------------------------------

    def get_stats(self, deck: Deck) -> ReviewStats:
        """Get stats."""
        by_diff: dict[str, int] = {}
        for c in deck.cards:
            by_diff[c.difficulty] = by_diff.get(c.difficulty, 0) + 1
        sr = SpacedRepetition()
        due = len(sr.get_due_cards(deck))
        reviewed = sum(1 for c in deck.cards if c.last_reviewed is not None)
        return ReviewStats(
            total_cards=len(deck.cards),
            cards_reviewed=reviewed,
            cards_by_difficulty=by_diff,
            due_cards=due,
        )

    # Internal persistence ---------------------------------------------------

    def _save(self, deck: Deck) -> None:
        """Save data to storage."""
        path = self._deck_path(deck.name)
        data = {
            "name": deck.name,
            "description": deck.description,
            "created_at": deck.created_at,
            "tags": deck.tags,
            "cards": [asdict(c) for c in deck.cards],
        }
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2, ensure_ascii=False)

    def _load_from_path(self, path: Path) -> Deck:
        """Load from path."""
        with open(path, "r", encoding="utf-8") as fh:
            raw = json.load(fh)
        cards = [Flashcard(**c) for c in raw.get("cards", [])]
        return Deck(
            name=raw.get("name", path.stem),
            description=raw.get("description", ""),
            cards=cards,
            created_at=raw.get("created_at", ""),
            tags=raw.get("tags", []),
        )


# ---------------------------------------------------------------------------
# LLM flashcard generation (enhanced from original app.py)
# ---------------------------------------------------------------------------

def parse_response(text: str) -> dict:
    """Strip markdown fences and parse JSON from LLM output."""
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0]
    return json.loads(text)


def create_flashcards(topic: str, count: int = 10, difficulty: str = "medium",
                      config: Optional[ConfigManager] = None) -> dict:
    """Generate flashcards using the LLM."""
    temperature = 0.7
    max_tokens = 4096
    if config:
        temperature = config.get("llm", "temperature", 0.7)
        max_tokens = config.get("llm", "max_tokens", 4096)

    prompt = (
        f"Create exactly {count} study flashcards about '{topic}'.\n"
        f"Difficulty level: {difficulty}.\n"
        f"Include clear, concise fronts (questions/terms) and detailed backs (answers/definitions).\n"
        f"Add helpful hints and relevant tags."
    )

    response = chat(
        messages=[{"role": "user", "content": prompt}],
        system_prompt=SYSTEM_PROMPT,
        temperature=temperature,
        max_tokens=max_tokens,
    )

    return parse_response(response)


def dict_to_flashcards(data: dict) -> list[Flashcard]:
    """Convert raw LLM JSON into a list of Flashcard dataclass instances."""
    cards: list[Flashcard] = []
    for raw in data.get("cards", []):
        cards.append(Flashcard(
            id=str(raw.get("id", uuid.uuid4().hex[:8])),
            front=raw.get("front", ""),
            back=raw.get("back", ""),
            hint=raw.get("hint", ""),
            difficulty=raw.get("difficulty", "medium"),
            tags=raw.get("tags", []),
        ))
    return cards


# ---------------------------------------------------------------------------
# Import / Export helpers
# ---------------------------------------------------------------------------

def export_deck_json(deck: Deck, filepath: str) -> str:
    """Export a deck to JSON file. Returns the filepath."""
    data = {
        "name": deck.name,
        "description": deck.description,
        "created_at": deck.created_at,
        "tags": deck.tags,
        "cards": [asdict(c) for c in deck.cards],
    }
    with open(filepath, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)
    logger.info("Exported deck '%s' to %s (JSON)", deck.name, filepath)
    return filepath


def import_deck_json(filepath: str) -> Deck:
    """Import a deck from a JSON file."""
    with open(filepath, "r", encoding="utf-8") as fh:
        raw = json.load(fh)
    cards = [Flashcard(**c) for c in raw.get("cards", [])]
    return Deck(
        name=raw.get("name", Path(filepath).stem),
        description=raw.get("description", ""),
        cards=cards,
        created_at=raw.get("created_at", datetime.now().isoformat()),
        tags=raw.get("tags", []),
    )


def export_deck_csv(deck: Deck, filepath: str) -> str:
    """Export a deck to CSV file. Returns the filepath."""
    fieldnames = ["id", "front", "back", "hint", "difficulty", "tags"]
    with open(filepath, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for card in deck.cards:
            writer.writerow({
                "id": card.id,
                "front": card.front,
                "back": card.back,
                "hint": card.hint,
                "difficulty": card.difficulty,
                "tags": ";".join(card.tags),
            })
    logger.info("Exported deck '%s' to %s (CSV)", deck.name, filepath)
    return filepath


def import_deck_csv(filepath: str) -> Deck:
    """Import a deck from a CSV file."""
    cards: list[Flashcard] = []
    with open(filepath, "r", newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            tags = [t.strip() for t in row.get("tags", "").split(";") if t.strip()]
            cards.append(Flashcard(
                id=row.get("id", str(uuid.uuid4())[:8]),
                front=row.get("front", ""),
                back=row.get("back", ""),
                hint=row.get("hint", ""),
                difficulty=row.get("difficulty", "medium"),
                tags=tags,
            ))
    return Deck(
        name=Path(filepath).stem,
        description=f"Imported from {Path(filepath).name}",
        cards=cards,
    )
