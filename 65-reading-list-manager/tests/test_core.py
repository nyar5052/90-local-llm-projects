"""Tests for Reading List Manager core module."""

import sys
import os
import json
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from reading_list.core import (
    load_books,
    save_books,
    add_book,
    update_progress,
    rate_book,
    get_genre_stats,
    recommend_similar,
    calculate_reading_speed,
    set_reading_goal,
    check_goal_progress,
    get_tbr_list,
    prioritize_tbr,
    get_summary,
    get_recommendations,
    analyze_reading_habits,
    display_books,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def mock_books_file(tmp_path, monkeypatch):
    """Redirect data files to a temp directory for every test."""
    books_path = str(tmp_path / "reading_list.json")
    goals_path = str(tmp_path / "reading_goals.json")
    monkeypatch.setattr("reading_list.core.BOOKS_FILE", books_path)
    monkeypatch.setattr("reading_list.core.GOALS_FILE", goals_path)
    return books_path


def _seed_books():
    """Helper to create a small test library."""
    add_book("Clean Code", "Robert C. Martin", "Technical", "completed", rating=5, pages=464)
    add_book("Dune", "Frank Herbert", "Science Fiction", "completed", rating=4, pages=412)
    add_book("1984", "George Orwell", "Fiction", "to-read", pages=328)
    add_book("Sapiens", "Yuval Noah Harari", "Non-Fiction", "reading", pages=443)
    add_book("Neuromancer", "William Gibson", "Science Fiction", "to-read", pages=271)


# ---------------------------------------------------------------------------
# load / save
# ---------------------------------------------------------------------------


class TestLoadSave:
    def test_load_empty(self):
        data = load_books()
        assert data == {"books": []}

    def test_save_and_load(self):
        save_books({"books": [{"id": 1, "title": "Test"}]})
        data = load_books()
        assert len(data["books"]) == 1
        assert data["books"][0]["title"] == "Test"


# ---------------------------------------------------------------------------
# add_book
# ---------------------------------------------------------------------------


class TestAddBook:
    def test_add_single(self):
        book = add_book("Clean Code", "Robert C. Martin", "Technical", "to-read")
        assert book["title"] == "Clean Code"
        assert book["author"] == "Robert C. Martin"
        assert book["genre"] == "Technical"
        assert book["id"] == 1
        assert book["pages_read"] == 0
        assert book["progress_percent"] == 0.0

    def test_add_multiple(self):
        add_book("Book A", "Author A")
        add_book("Book B", "Author B")
        add_book("Book C", "Author C")
        data = load_books()
        assert len(data["books"]) == 3
        assert data["books"][2]["id"] == 3

    def test_add_with_pages(self):
        book = add_book("Big Book", "Author", pages=500)
        assert book["pages"] == 500


# ---------------------------------------------------------------------------
# update_progress
# ---------------------------------------------------------------------------


class TestUpdateProgress:
    def test_progress_basic(self):
        add_book("Test", "Author", pages=200)
        book = update_progress(1, 50)
        assert book is not None
        assert book["pages_read"] == 50
        assert book["progress_percent"] == 25.0
        assert book["status"] == "reading"

    def test_progress_complete(self):
        add_book("Test", "Author", pages=100)
        book = update_progress(1, 100)
        assert book["status"] == "completed"
        assert book["progress_percent"] == 100.0

    def test_progress_not_found(self):
        assert update_progress(999, 10) is None

    def test_progress_no_pages(self):
        add_book("Test", "Author", pages=0)
        book = update_progress(1, 10)
        assert book["progress_percent"] == 0.0


# ---------------------------------------------------------------------------
# rate_book
# ---------------------------------------------------------------------------


class TestRateBook:
    def test_rate(self):
        add_book("Test", "Author")
        book = rate_book(1, 4, "Great read!")
        assert book["rating"] == 4
        assert book["review"] == "Great read!"

    def test_rate_invalid(self):
        add_book("Test", "Author")
        with pytest.raises(ValueError):
            rate_book(1, 0)
        with pytest.raises(ValueError):
            rate_book(1, 6)

    def test_rate_not_found(self):
        assert rate_book(999, 3) is None


# ---------------------------------------------------------------------------
# get_genre_stats
# ---------------------------------------------------------------------------


class TestGenreStats:
    def test_genre_stats(self):
        _seed_books()
        data = load_books()
        stats = get_genre_stats(data["books"])
        assert "Technical" in stats
        assert stats["Technical"]["count"] == 1
        assert stats["Technical"]["avg_rating"] == 5.0
        assert stats["Science Fiction"]["count"] == 2

    def test_genre_stats_empty(self):
        assert get_genre_stats([]) == {}


# ---------------------------------------------------------------------------
# recommend_similar
# ---------------------------------------------------------------------------


class TestRecommendSimilar:
    def test_recommend(self):
        _seed_books()
        data = load_books()
        recs = recommend_similar(data["books"])
        assert isinstance(recs, list)
        for r in recs:
            assert r["status"] in ("to-read", "on-hold")

    def test_recommend_empty(self):
        assert recommend_similar([]) == []


# ---------------------------------------------------------------------------
# calculate_reading_speed
# ---------------------------------------------------------------------------


class TestReadingSpeed:
    def test_speed_calculation(self):
        now = datetime.now()
        ten_days_ago = (now - timedelta(days=10)).isoformat()
        book = {
            "pages": 300,
            "pages_read": 300,
            "started": ten_days_ago,
            "finished": now.isoformat(),
        }
        speed = calculate_reading_speed(book)
        assert speed == 30.0

    def test_speed_no_start(self):
        book = {"pages": 100, "started": None}
        assert calculate_reading_speed(book) is None

    def test_speed_no_pages(self):
        book = {"pages": 0, "pages_read": 0, "started": datetime.now().isoformat()}
        assert calculate_reading_speed(book) is None


# ---------------------------------------------------------------------------
# Reading goals
# ---------------------------------------------------------------------------


class TestGoals:
    def test_set_and_check_goal(self):
        year = datetime.now().year
        goal = set_reading_goal(year, 12)
        assert goal["target"] == 12

        _seed_books()
        data = load_books()
        # Mark books as completed this year
        for b in data["books"]:
            if b["status"] == "completed":
                b["finished"] = datetime.now().isoformat()
        save_books(data)

        progress = check_goal_progress(year, load_books()["books"])
        assert progress["target"] == 12
        assert progress["completed"] == 2
        assert progress["remaining"] == 10

    def test_check_goal_no_goal_set(self):
        year = datetime.now().year
        progress = check_goal_progress(year, [])
        assert progress["completed"] == 0
        assert progress["target"] == 24  # default from config


# ---------------------------------------------------------------------------
# TBR management
# ---------------------------------------------------------------------------


class TestTBR:
    def test_get_tbr_list(self):
        _seed_books()
        data = load_books()
        tbr = get_tbr_list(data["books"])
        assert all(b["status"] in ("to-read", "on-hold") for b in tbr)
        assert len(tbr) == 2

    def test_prioritize_by_pages(self):
        _seed_books()
        data = load_books()
        tbr = prioritize_tbr(data["books"], sort_by="pages")
        if len(tbr) >= 2:
            assert tbr[0]["pages"] <= tbr[1]["pages"]


# ---------------------------------------------------------------------------
# AI functions (mocked)
# ---------------------------------------------------------------------------


class TestAIFunctions:
    @patch("reading_list.core.generate")
    def test_get_summary(self, mock_gen):
        mock_gen.return_value = "## Overview\nA great book."
        result = get_summary("Clean Code", "Robert Martin")
        assert "Overview" in result
        mock_gen.assert_called_once()

    @patch("reading_list.core.generate")
    def test_get_recommendations(self, mock_gen):
        mock_gen.return_value = "1. **Design Patterns** by GoF"
        books = [{"title": "Clean Code", "author": "Robert Martin", "genre": "Technical", "rating": 5}]
        result = get_recommendations("Technical", books)
        assert "Design Patterns" in result
        mock_gen.assert_called_once()

    @patch("reading_list.core.generate")
    def test_analyze_reading_habits(self, mock_gen):
        mock_gen.return_value = "## Reading Profile\nTechnical reader."
        books = [{"title": "Clean Code", "author": "Robert Martin", "genre": "Technical", "rating": 5}]
        result = analyze_reading_habits(books)
        assert "Reading Profile" in result
        mock_gen.assert_called_once()


# ---------------------------------------------------------------------------
# display_books (smoke test)
# ---------------------------------------------------------------------------


class TestDisplay:
    def test_display_books(self):
        _seed_books()
        data = load_books()
        # Should not raise
        display_books(data["books"])
