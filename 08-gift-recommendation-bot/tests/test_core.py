"""Tests for Gift Recommendation Bot core logic."""

import pytest
from unittest.mock import patch

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from gift_recommender.core import (
    generate_recommendations,
    get_gift_details,
    compare_prices,
    add_to_wishlist,
    get_wishlist,
    mark_purchased,
    add_occasion,
    get_upcoming_occasions,
    OCCASIONS,
    RELATIONSHIPS,
    SYSTEM_PROMPT,
)


class TestConfiguration:
    """Tests for app configuration."""

    def test_occasions_defined(self):
        assert "birthday" in OCCASIONS
        assert "christmas" in OCCASIONS
        assert "wedding" in OCCASIONS
        assert len(OCCASIONS) >= 10

    def test_relationships_defined(self):
        assert "partner" in RELATIONSHIPS
        assert "friend" in RELATIONSHIPS
        assert "parent" in RELATIONSHIPS
        assert len(RELATIONSHIPS) >= 5

    def test_system_prompt_is_gift_expert(self):
        assert "gift" in SYSTEM_PROMPT.lower()


class TestGenerateRecommendations:
    """Tests for recommendation generation."""

    @patch("gift_recommender.core.chat")
    def test_basic_recommendations(self, mock_chat):
        mock_chat.return_value = "1. Custom Photo Album ($30)\n2. Gourmet Basket ($45)"
        result = generate_recommendations("birthday", "friend", 50)
        assert "Album" in result or "Basket" in result

    @patch("gift_recommender.core.chat")
    def test_includes_budget(self, mock_chat):
        mock_chat.return_value = "Recommendations..."
        generate_recommendations("christmas", "partner", 100)
        messages = mock_chat.call_args[0][0]
        assert "$100" in messages[0]["content"]

    @patch("gift_recommender.core.chat")
    def test_includes_interests(self, mock_chat):
        mock_chat.return_value = "Recommendations..."
        generate_recommendations("birthday", "friend", 50, interests="gaming,cooking")
        messages = mock_chat.call_args[0][0]
        assert "gaming" in messages[0]["content"].lower()

    @patch("gift_recommender.core.chat")
    def test_includes_age(self, mock_chat):
        mock_chat.return_value = "Recommendations..."
        generate_recommendations("birthday", "child", 30, age="8")
        messages = mock_chat.call_args[0][0]
        assert "8" in messages[0]["content"]


class TestGetGiftDetails:
    """Tests for gift detail retrieval."""

    @patch("gift_recommender.core.chat")
    def test_returns_details(self, mock_chat):
        mock_chat.return_value = "A custom photo album is a wonderful..."
        result = get_gift_details("Custom Photo Album", 50)
        assert "photo album" in result.lower()

    @patch("gift_recommender.core.chat")
    def test_includes_budget(self, mock_chat):
        mock_chat.return_value = "Details..."
        get_gift_details("Board Game", 30)
        messages = mock_chat.call_args[0][0]
        assert "$30" in messages[0]["content"]


class TestPriceComparison:
    """Tests for price comparison."""

    @patch("gift_recommender.core.chat")
    def test_compares_prices(self, mock_chat):
        mock_chat.return_value = "Amazon: $29.99\nTarget: $34.99..."
        result = compare_prices("Gaming Headset")
        assert "$" in result


class TestWishlist:
    """Tests for wishlist management."""

    @patch("gift_recommender.core.save_json_file")
    @patch("gift_recommender.core.load_json_file", return_value={})
    def test_add_to_wishlist(self, mock_load, mock_save):
        item = add_to_wishlist("Mom", "Cookbook", "$25", "birthday")
        assert item["gift"] == "Cookbook"
        assert item["purchased"] is False
        mock_save.assert_called_once()

    @patch("gift_recommender.core.load_json_file", return_value={
        "mom": {"name": "Mom", "items": [{"id": 1, "gift": "Cookbook", "purchased": False}]}
    })
    def test_get_wishlist(self, mock_load):
        items = get_wishlist("Mom")
        assert len(items) == 1
        assert items[0]["gift"] == "Cookbook"


class TestCalendar:
    """Tests for occasion calendar."""

    @patch("gift_recommender.core.save_json_file")
    @patch("gift_recommender.core.load_json_file", return_value=[])
    def test_add_occasion(self, mock_load, mock_save):
        entry = add_occasion("Mom", "birthday", "2025-03-15")
        assert entry["person"] == "Mom"
        assert entry["occasion"] == "birthday"
        mock_save.assert_called_once()


class TestCLI:
    """Tests for the CLI interface."""

    @patch("gift_recommender.core.check_ollama_running", return_value=False)
    def test_exits_when_ollama_down(self, mock_check):
        from click.testing import CliRunner
        from gift_recommender.cli import cli
        runner = CliRunner()
        result = runner.invoke(cli, ["recommend", "--occasion", "birthday"])
        assert result.exit_code != 0
