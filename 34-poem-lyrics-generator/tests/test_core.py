"""Tests for Poem & Lyrics Generator core logic."""

import json
import os
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path

from poem_gen.core import (
    build_prompt,
    generate_poem,
    generate_with_rhyme_scheme,
    mix_styles,
    count_syllables,
    detect_rhyme_scheme,
    analyze_poem,
    format_poem,
    manage_collection,
    Poem,
    PoemCollection,
    STYLES,
    MOODS,
    STYLE_INSTRUCTIONS,
)


# ---------------------------------------------------------------------------
# build_prompt
# ---------------------------------------------------------------------------
class TestBuildPrompt:
    def test_prompt_contains_theme(self):
        prompt = build_prompt("ocean sunset", "sonnet", None, None)
        assert "ocean sunset" in prompt

    def test_prompt_contains_style_instructions(self):
        prompt = build_prompt("love", "haiku", None, None)
        assert "5-7-5" in prompt

    def test_prompt_contains_mood(self):
        prompt = build_prompt("rain", "free-verse", "melancholic", None)
        assert "melancholic" in prompt

    def test_prompt_contains_title(self):
        prompt = build_prompt("stars", "sonnet", None, "Starlight")
        assert "Starlight" in prompt

    def test_rap_style_mentions_verses(self):
        prompt = build_prompt("city life", "rap", None, None)
        assert "verse" in prompt.lower()

    def test_unknown_style_fallback(self):
        prompt = build_prompt("test", "unknown-style", None, None)
        assert "Write a poem in this style" in prompt


# ---------------------------------------------------------------------------
# Syllable counting
# ---------------------------------------------------------------------------
class TestCountSyllables:
    def test_simple_words(self):
        result = count_syllables("hello world")
        assert result == [3]  # hel-lo = 2 vowel clusters, world = 1

    def test_multiline(self):
        text = "the cat sat\non the mat"
        result = count_syllables(text)
        assert len(result) == 2

    def test_empty_lines_skipped(self):
        text = "hello\n\nworld"
        result = count_syllables(text)
        assert len(result) == 2

    def test_empty_text(self):
        assert count_syllables("") == []

    def test_haiku_approximate(self):
        # "An old silent pond" should give ~5 syllables
        result = count_syllables("An old silent pond")
        assert len(result) == 1
        assert 3 <= result[0] <= 6  # approximate


# ---------------------------------------------------------------------------
# Rhyme scheme detection
# ---------------------------------------------------------------------------
class TestDetectRhymeScheme:
    def test_aabb(self):
        text = "The cat in the hat\nSitting on the mat\nThe dog on the log\nHiding in the fog"
        scheme = detect_rhyme_scheme(text)
        assert scheme == "AABB"

    def test_no_rhymes(self):
        text = "The quick brown fox\nJumps over the lazy dog\nLife is but a dream"
        scheme = detect_rhyme_scheme(text)
        # All different endings → should be ABC or similar
        assert len(scheme) == 3

    def test_empty_text(self):
        assert detect_rhyme_scheme("") == ""

    def test_single_line(self):
        scheme = detect_rhyme_scheme("Hello world")
        assert len(scheme) == 1

    def test_abab_pattern(self):
        text = "I walked along the way\nBeneath the summer night\nI saw the light of day\nA warm and gentle light"
        scheme = detect_rhyme_scheme(text)
        # "way/day" rhyme, "night/light" rhyme → ABAB
        assert scheme == "ABAB"


# ---------------------------------------------------------------------------
# Poem analysis
# ---------------------------------------------------------------------------
class TestAnalyzePoem:
    def test_basic_analysis(self):
        text = "Roses are red\nViolets are blue\nSugar is sweet\nAnd so are you"
        result = analyze_poem(text)
        assert result["line_count"] == 4
        assert result["word_count"] > 0
        assert len(result["syllables_per_line"]) == 4
        assert isinstance(result["detected_rhyme_scheme"], str)

    def test_empty_text(self):
        result = analyze_poem("")
        assert result["line_count"] == 0
        assert result["word_count"] == 0


# ---------------------------------------------------------------------------
# Format poem
# ---------------------------------------------------------------------------
class TestFormatPoem:
    def test_haiku_indentation(self):
        text = "An old silent pond\nA frog jumps in\nSplash silence"
        formatted = format_poem(text, "haiku")
        for line in formatted.splitlines():
            if line.strip():
                assert line.startswith("    ")

    def test_sonnet_indentation(self):
        lines = [f"Line {i}" for i in range(1, 15)]
        text = "\n".join(lines)
        formatted = format_poem(text, "sonnet")
        assert formatted.count("  Line") > 0

    def test_default_style(self):
        text = "Hello world\nGoodbye world"
        formatted = format_poem(text, "free-verse")
        assert "Hello world" in formatted

    def test_empty_text(self):
        assert format_poem("", "haiku") == ""

    def test_rap_tags(self):
        text = "CHORUS\nYeah yeah yeah\nVERSE 1\nRhymes all day"
        formatted = format_poem(text, "rap")
        assert "[CHORUS]" in formatted


# ---------------------------------------------------------------------------
# Poem / PoemCollection dataclasses
# ---------------------------------------------------------------------------
class TestPoemDataclass:
    def test_create_poem(self):
        p = Poem(title="Test", content="Hello", style="haiku")
        assert p.title == "Test"
        assert p.style == "haiku"
        assert p.created_at is not None

    def test_poem_round_trip(self):
        p = Poem(title="Test", content="Hello", style="haiku", mood="happy", theme="nature")
        d = p.to_dict()
        p2 = Poem.from_dict(d)
        assert p2.title == p.title
        assert p2.content == p.content
        assert p2.mood == p.mood


class TestPoemCollection:
    def test_empty_collection(self):
        c = PoemCollection(name="test")
        assert len(c.poems) == 0

    def test_collection_round_trip(self):
        p = Poem(title="Test", content="Hello", style="haiku")
        c = PoemCollection(name="my-poems", poems=[p])
        d = c.to_dict()
        c2 = PoemCollection.from_dict(d)
        assert c2.name == "my-poems"
        assert len(c2.poems) == 1
        assert c2.poems[0].title == "Test"


# ---------------------------------------------------------------------------
# Collection management (uses temp files)
# ---------------------------------------------------------------------------
class TestManageCollection:
    @patch("poem_gen.core._collections_path")
    def test_add_poem(self, mock_path, tmp_path):
        json_file = tmp_path / "test.json"
        mock_path.return_value = json_file

        poem = Poem(title="Sunset", content="The sun sets.", style="haiku")
        coll = manage_collection("test", "add", poem)
        assert len(coll.poems) == 1
        assert coll.poems[0].title == "Sunset"
        assert json_file.exists()

    @patch("poem_gen.core._collections_path")
    def test_list_empty_collection(self, mock_path, tmp_path):
        json_file = tmp_path / "empty.json"
        mock_path.return_value = json_file

        coll = manage_collection("empty", "list")
        assert len(coll.poems) == 0

    @patch("poem_gen.core._collections_path")
    def test_remove_poem(self, mock_path, tmp_path):
        json_file = tmp_path / "test.json"
        mock_path.return_value = json_file

        poem = Poem(title="To Remove", content="Gone.", style="free-verse")
        manage_collection("test", "add", poem)
        coll = manage_collection("test", "remove", poem)
        assert len(coll.poems) == 0

    @patch("poem_gen.core._collections_path")
    def test_add_requires_poem(self, mock_path, tmp_path):
        mock_path.return_value = tmp_path / "test.json"
        with pytest.raises(ValueError, match="required"):
            manage_collection("test", "add", None)

    def test_invalid_action(self):
        with pytest.raises(ValueError, match="Unknown action"):
            manage_collection("test", "invalid")


# ---------------------------------------------------------------------------
# Generation (mocked LLM)
# ---------------------------------------------------------------------------
class TestGeneratePoem:
    @patch("poem_gen.core.chat")
    def test_generate_returns_content(self, mock_chat):
        mock_chat.return_value = "Ocean Sunset\n\nWaves crash on the shore..."
        result = generate_poem("ocean sunset", "free-verse", None, None)
        assert "Ocean Sunset" in result
        mock_chat.assert_called_once()

    @patch("poem_gen.core.chat")
    def test_generate_uses_configured_temperature(self, mock_chat):
        mock_chat.return_value = "A poem"
        generate_poem("love", "sonnet", "romantic", None)
        _, kwargs = mock_chat.call_args
        assert kwargs["temperature"] == 0.9


class TestGenerateWithRhymeScheme:
    @patch("poem_gen.core.chat")
    def test_generates_with_scheme(self, mock_chat):
        mock_chat.return_value = "Title\n\nLine one\nLine two\nLine three\nLine four"
        result = generate_with_rhyme_scheme("nature", "ABAB", "happy")
        assert result is not None
        mock_chat.assert_called_once()
        call_args = mock_chat.call_args
        prompt = call_args[0][0][0]["content"]
        assert "ABAB" in prompt


class TestMixStyles:
    @patch("poem_gen.core.chat")
    def test_mix_two_styles(self, mock_chat):
        mock_chat.return_value = "A blended poem"
        result = mix_styles("love", ["haiku", "sonnet"], "romantic")
        assert result == "A blended poem"

    def test_mix_requires_two_styles(self):
        with pytest.raises(ValueError, match="at least two"):
            mix_styles("love", ["haiku"])


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
class TestConstants:
    def test_styles_list(self):
        assert "haiku" in STYLES
        assert "sonnet" in STYLES
        assert len(STYLES) >= 7

    def test_moods_list(self):
        assert "happy" in MOODS
        assert "dark" in MOODS
        assert len(MOODS) >= 6

    def test_style_instructions_keys(self):
        for s in STYLES:
            assert s in STYLE_INSTRUCTIONS
