"""Tests for Family Story Creator core module."""

import json
import os
import sys
import pytest
from unittest.mock import patch, MagicMock

# Ensure src is on path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.family_story.core import (
    create_character,
    create_story,
    create_poem,
    load_stories,
    save_story,
    delete_story,
    export_story,
    load_config,
    STORY_STYLES,
    DEFAULT_CONFIG,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_config():
    """Return a default test configuration."""
    return dict(DEFAULT_CONFIG)


@pytest.fixture
def sample_story():
    """Return a sample story dict."""
    return {
        "members": "Mom, Dad, Sam",
        "event": "Summer Vacation 2024",
        "style": "heartwarming",
        "story": "# A Day to Remember\n\nThe sun shone brightly as the family set off on their adventure.",
    }


@pytest.fixture
def stories_file(tmp_path):
    """Provide a temporary stories file path."""
    return str(tmp_path / "test_stories.json")


# ---------------------------------------------------------------------------
# Character Tests
# ---------------------------------------------------------------------------

class TestCreateCharacter:
    def test_create_character_basic(self):
        char = create_character("Mom")
        assert char["name"] == "Mom"
        assert char["age"] is None
        assert char["personality"] == ""
        assert char["relationship"] == ""
        assert char["appearance"] == ""

    def test_create_character_full(self):
        char = create_character(
            name="Grandma Rose",
            age=75,
            personality="warm and wise",
            relationship="grandmother",
            appearance="silver hair, kind eyes",
        )
        assert char["name"] == "Grandma Rose"
        assert char["age"] == 75
        assert char["personality"] == "warm and wise"
        assert char["relationship"] == "grandmother"
        assert char["appearance"] == "silver hair, kind eyes"


# ---------------------------------------------------------------------------
# Story Creation Tests
# ---------------------------------------------------------------------------

class TestCreateStory:
    @patch("src.family_story.core.generate")
    def test_create_story_basic(self, mock_generate, sample_config):
        mock_generate.return_value = "# A Beautiful Day\n\nThe family gathered together..."
        result = create_story(
            members="Mom, Dad, Kids",
            event="vacation 2024",
            style="heartwarming",
            config=sample_config,
        )
        assert "Beautiful Day" in result or "family" in result.lower()
        mock_generate.assert_called_once()

    @patch("src.family_story.core.generate")
    def test_create_story_with_characters(self, mock_generate, sample_config):
        mock_generate.return_value = "# Family Adventure\n\nGrandma Rose smiled warmly..."
        characters = [
            create_character("Grandma Rose", 75, "wise", "grandmother", "silver hair"),
            create_character("Sam", 10, "adventurous", "grandson"),
        ]
        result = create_story(
            members=characters,
            event="hiking trip",
            style="adventurous",
            config=sample_config,
        )
        assert result is not None
        mock_generate.assert_called_once()
        prompt_text = mock_generate.call_args[1].get("prompt", mock_generate.call_args[0][0] if mock_generate.call_args[0] else "")
        assert "Grandma Rose" in prompt_text

    @patch("src.family_story.core.generate")
    def test_create_story_with_photos(self, mock_generate, sample_config):
        mock_generate.return_value = "# Photo Memories\n\nLooking at the old photograph..."
        result = create_story(
            members="Mom, Dad",
            event="anniversary",
            style="nostalgic",
            photos="A black and white photo of the couple dancing",
            config=sample_config,
        )
        assert result is not None
        mock_generate.assert_called_once()


# ---------------------------------------------------------------------------
# Poem Tests
# ---------------------------------------------------------------------------

class TestCreatePoem:
    @patch("src.family_story.core.generate")
    def test_create_poem_basic(self, mock_generate, sample_config):
        mock_generate.return_value = "Roses are red, violets are blue,\nOur family trip was wonderful too."
        result = create_poem("Mom, Dad, Kids", "summer vacation", "rhyming", config=sample_config)
        assert "Roses" in result or "family" in result.lower()
        mock_generate.assert_called_once()

    @patch("src.family_story.core.generate")
    def test_create_poem_free_verse(self, mock_generate, sample_config):
        mock_generate.return_value = "Morning light spills\nacross the kitchen table\nwhere we gather."
        result = create_poem("Family", "breakfast", "free-verse", config=sample_config)
        assert result is not None
        mock_generate.assert_called_once()


# ---------------------------------------------------------------------------
# Persistence Tests
# ---------------------------------------------------------------------------

class TestSaveAndLoadStories:
    def test_load_empty(self, stories_file):
        stories = load_stories(stories_file)
        assert stories == []

    def test_save_and_load(self, stories_file, sample_story):
        saved = save_story(sample_story.copy(), stories_file)
        assert "id" in saved
        assert "created" in saved

        stories = load_stories(stories_file)
        assert len(stories) == 1
        assert stories[0]["event"] == "Summer Vacation 2024"
        assert stories[0]["id"] == saved["id"]

    def test_save_multiple(self, stories_file, sample_story):
        save_story(sample_story.copy(), stories_file)
        save_story({**sample_story, "event": "Christmas 2024"}, stories_file)

        stories = load_stories(stories_file)
        assert len(stories) == 2

    def test_load_corrupted_file(self, tmp_path):
        bad_file = str(tmp_path / "bad.json")
        with open(bad_file, "w") as f:
            f.write("not valid json{{{")
        stories = load_stories(bad_file)
        assert stories == []


class TestDeleteStory:
    def test_delete_existing(self, stories_file, sample_story):
        saved = save_story(sample_story.copy(), stories_file)
        result = delete_story(saved["id"], stories_file)
        assert result is True
        assert load_stories(stories_file) == []

    def test_delete_nonexistent(self, stories_file):
        result = delete_story("nonexistent", stories_file)
        assert result is False


# ---------------------------------------------------------------------------
# Export Tests
# ---------------------------------------------------------------------------

class TestExportStory:
    def test_export_markdown(self, sample_story):
        result = export_story(sample_story, format="markdown")
        assert "# Summer Vacation 2024" in result
        assert "Mom, Dad, Sam" in result
        assert "heartwarming" in result
        assert "Family Story Creator v2.0.0" in result

    def test_export_html(self, sample_story):
        result = export_story(sample_story, format="html")
        assert "<!DOCTYPE html>" in result
        assert "<title>Summer Vacation 2024</title>" in result
        assert "Mom, Dad, Sam" in result
        assert "Family Story Creator v2.0.0" in result
        assert "<html" in result

    def test_export_default_is_markdown(self, sample_story):
        result = export_story(sample_story)
        assert "# Summer Vacation 2024" in result


# ---------------------------------------------------------------------------
# Config Tests
# ---------------------------------------------------------------------------

class TestLoadConfig:
    def test_load_default(self):
        config = load_config(None)
        assert config["llm"]["model"] == "llama3.2"
        assert config["default_style"] == "heartwarming"

    def test_load_from_file(self, tmp_path):
        config_file = str(tmp_path / "test_config.yaml")
        import yaml
        with open(config_file, "w") as f:
            yaml.dump({"llm": {"model": "custom-model"}, "default_style": "humorous"}, f)

        config = load_config(config_file)
        assert config["llm"]["model"] == "custom-model"
        assert config["default_style"] == "humorous"
        # Merged defaults still present
        assert config["llm"]["temperature"] == 0.8

    def test_load_missing_file(self):
        config = load_config("nonexistent.yaml")
        assert config == DEFAULT_CONFIG
