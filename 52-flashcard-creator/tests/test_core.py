#!/usr/bin/env python3
"""Tests for flashcard_creator.core — business logic, SM-2, deck management."""

import json
import os
import tempfile
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

import pytest

from src.flashcard_creator.core import (
    Flashcard,
    Deck,
    ReviewStats,
    SpacedRepetition,
    DeckManager,
    ReviewSession,
    ConfigManager,
    create_flashcards,
    parse_response,
    dict_to_flashcards,
    export_deck_json,
    import_deck_json,
    export_deck_csv,
    import_deck_csv,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

SAMPLE_CARDS = {
    "topic": "Python Basics",
    "cards": [
        {
            "id": 1,
            "front": "What is a list comprehension?",
            "back": "A concise way to create lists using a single line of code.",
            "hint": "Think of [x for x in ...]",
            "difficulty": "easy",
            "tags": ["python", "lists"],
        },
        {
            "id": 2,
            "front": "What is a decorator?",
            "back": "A function that wraps another function to extend its behaviour.",
            "hint": "Uses the @ symbol",
            "difficulty": "medium",
            "tags": ["python", "functions"],
        },
        {
            "id": 3,
            "front": "Explain the GIL.",
            "back": "The Global Interpreter Lock prevents multiple native threads from executing Python bytecodes simultaneously.",
            "hint": "Concurrency limitation",
            "difficulty": "hard",
            "tags": ["python", "concurrency"],
        },
    ],
}


@pytest.fixture
def sample_cards():
    return SAMPLE_CARDS.copy()


@pytest.fixture
def deck_dir(tmp_path):
    d = tmp_path / "decks"
    d.mkdir()
    return str(d)


# ---------------------------------------------------------------------------
# Flashcard dataclass
# ---------------------------------------------------------------------------


class TestFlashcardDataclass:
    def test_flashcard_defaults(self):
        card = Flashcard(front="Q", back="A")
        assert card.front == "Q"
        assert card.back == "A"
        assert card.difficulty == "medium"
        assert card.ease_factor == 2.5
        assert card.interval == 1
        assert card.repetitions == 0
        assert card.last_reviewed is None
        assert isinstance(card.tags, list)
        assert card.id  # auto-generated

    def test_flashcard_custom(self):
        card = Flashcard(id="c1", front="Q", back="A", difficulty="hard",
                         tags=["math"], hint="think")
        assert card.id == "c1"
        assert card.difficulty == "hard"
        assert card.hint == "think"
        assert card.tags == ["math"]


# ---------------------------------------------------------------------------
# parse_response
# ---------------------------------------------------------------------------


class TestParseResponse:
    def test_create_flashcards_parses_json(self, sample_cards):
        raw = json.dumps(sample_cards)
        result = parse_response(raw)
        assert result["topic"] == "Python Basics"
        assert len(result["cards"]) == 3

    def test_create_flashcards_handles_code_blocks(self, sample_cards):
        raw = "```json\n" + json.dumps(sample_cards) + "\n```"
        result = parse_response(raw)
        assert result["topic"] == "Python Basics"
        assert len(result["cards"]) == 3

    def test_parse_response_invalid_json(self):
        with pytest.raises(json.JSONDecodeError):
            parse_response("not json at all")


# ---------------------------------------------------------------------------
# create_flashcards (LLM call mocked)
# ---------------------------------------------------------------------------


class TestCreateFlashcards:
    @patch("src.flashcard_creator.core.chat")
    def test_create_flashcards_returns_dict(self, mock_chat, sample_cards):
        mock_chat.return_value = json.dumps(sample_cards)
        result = create_flashcards("Python Basics", count=3, difficulty="medium")
        assert result["topic"] == "Python Basics"
        assert len(result["cards"]) == 3
        mock_chat.assert_called_once()

    @patch("src.flashcard_creator.core.chat")
    def test_create_flashcards_with_code_blocks(self, mock_chat, sample_cards):
        mock_chat.return_value = "```json\n" + json.dumps(sample_cards) + "\n```"
        result = create_flashcards("Python Basics")
        assert len(result["cards"]) == 3


# ---------------------------------------------------------------------------
# SpacedRepetition (SM-2)
# ---------------------------------------------------------------------------


class TestSpacedRepetition:
    def test_sm2_easy(self):
        sr = SpacedRepetition()
        card = Flashcard(front="Q", back="A")
        assert card.repetitions == 0
        assert card.interval == 1

        # Perfect answer
        sr.calculate_next_review(card, quality=5)
        assert card.repetitions == 1
        assert card.interval == 1  # first rep stays at initial_interval
        assert card.ease_factor > 2.5  # increases for quality 5
        assert card.last_reviewed is not None

        # Second perfect answer
        sr.calculate_next_review(card, quality=5)
        assert card.repetitions == 2
        assert card.interval == 6  # graduating_interval

    def test_sm2_hard(self):
        sr = SpacedRepetition()
        card = Flashcard(front="Q", back="A")

        # Failed answer (quality < 3) — resets
        sr.calculate_next_review(card, quality=1)
        assert card.repetitions == 0
        assert card.interval == 1
        assert card.ease_factor < 2.5  # decreases

    def test_sm2_minimum_ease(self):
        sr = SpacedRepetition()
        card = Flashcard(front="Q", back="A", ease_factor=1.3)
        sr.calculate_next_review(card, quality=0)
        assert card.ease_factor >= sr.min_ef

    def test_get_due_cards_new(self):
        sr = SpacedRepetition()
        deck = Deck(name="Test", cards=[
            Flashcard(front="Q1", back="A1"),
            Flashcard(front="Q2", back="A2"),
        ])
        due = sr.get_due_cards(deck)
        assert len(due) == 2  # never reviewed = always due

    def test_get_due_cards_reviewed(self):
        sr = SpacedRepetition()
        card = Flashcard(front="Q", back="A", interval=10,
                         last_reviewed=datetime.now().isoformat())
        deck = Deck(name="Test", cards=[card])
        due = sr.get_due_cards(deck)
        assert len(due) == 0  # not due yet (10-day interval)


# ---------------------------------------------------------------------------
# DeckManager
# ---------------------------------------------------------------------------


class TestDeckManager:
    def test_create_deck(self, deck_dir):
        dm = DeckManager(deck_dir)
        deck = dm.create_deck("My Deck", description="Test deck")
        assert deck.name == "My Deck"
        assert deck.description == "Test deck"
        assert dm.get_deck("My Deck") is not None

    def test_add_card(self, deck_dir):
        dm = DeckManager(deck_dir)
        dm.create_deck("D1")
        card = Flashcard(front="Q", back="A")
        deck = dm.add_card("D1", card)
        assert len(deck.cards) == 1
        assert deck.cards[0].front == "Q"

    def test_remove_card(self, deck_dir):
        dm = DeckManager(deck_dir)
        dm.create_deck("D1")
        card = Flashcard(id="x1", front="Q", back="A")
        dm.add_card("D1", card)
        deck = dm.remove_card("D1", "x1")
        assert len(deck.cards) == 0

    def test_list_decks(self, deck_dir):
        dm = DeckManager(deck_dir)
        dm.create_deck("Alpha")
        dm.create_deck("Beta")
        decks = dm.list_decks()
        assert len(decks) == 2

    def test_delete_deck(self, deck_dir):
        dm = DeckManager(deck_dir)
        dm.create_deck("Del")
        assert dm.delete_deck("Del") is True
        assert dm.get_deck("Del") is None

    def test_merge_decks(self, deck_dir):
        dm = DeckManager(deck_dir)
        d1 = dm.create_deck("D1")
        d2 = dm.create_deck("D2")
        dm.add_card("D1", Flashcard(front="Q1", back="A1"))
        dm.add_card("D2", Flashcard(front="Q2", back="A2"))
        d1 = dm.get_deck("D1")
        d2 = dm.get_deck("D2")
        merged = dm.merge_decks(d1, d2, "Merged")
        assert len(merged.cards) == 2

    def test_get_stats(self, deck_dir):
        dm = DeckManager(deck_dir)
        dm.create_deck("S1")
        dm.add_card("S1", Flashcard(front="Q", back="A", difficulty="hard"))
        deck = dm.get_deck("S1")
        stats = dm.get_stats(deck)
        assert stats.total_cards == 1
        assert stats.cards_by_difficulty.get("hard") == 1


# ---------------------------------------------------------------------------
# Export / Import
# ---------------------------------------------------------------------------


class TestExportImport:
    def test_export_import_json(self, tmp_path):
        deck = Deck(name="Ex", cards=[
            Flashcard(id="1", front="Q", back="A", tags=["t"]),
        ])
        path = str(tmp_path / "deck.json")
        export_deck_json(deck, path)
        loaded = import_deck_json(path)
        assert loaded.name == "Ex"
        assert len(loaded.cards) == 1
        assert loaded.cards[0].front == "Q"

    def test_export_import_csv(self, tmp_path):
        deck = Deck(name="Csv", cards=[
            Flashcard(id="1", front="Q1", back="A1", tags=["a", "b"]),
            Flashcard(id="2", front="Q2", back="A2"),
        ])
        path = str(tmp_path / "deck.csv")
        export_deck_csv(deck, path)
        loaded = import_deck_csv(path)
        assert len(loaded.cards) == 2
        assert loaded.cards[0].tags == ["a", "b"]


# ---------------------------------------------------------------------------
# ReviewSession
# ---------------------------------------------------------------------------


class TestReviewSession:
    def test_review_session_basic(self):
        deck = Deck(name="R", cards=[
            Flashcard(front="Q1", back="A1"),
            Flashcard(front="Q2", back="A2"),
        ])
        session = ReviewSession(deck, shuffle=False)
        assert len(session.cards) == 2

        session.record(5)
        session.record(2)
        stats = session.finish()
        assert stats.cards_reviewed == 2
        assert stats.correct == 1
        assert stats.incorrect == 1
        assert stats.score_pct == 50.0
        assert stats.avg_quality == 3.5
        assert stats.time_elapsed_s >= 0
