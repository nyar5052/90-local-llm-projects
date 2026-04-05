"""Tests for Story Outline Generator core module."""

import pytest
from unittest.mock import patch

from story_gen.core import (
    build_prompt,
    load_config,
    get_character_archetypes,
    get_plot_structures,
    get_worldbuilding_categories,
    visualize_plot_arc,
    _deep_merge,
    CHARACTER_ARCHETYPES,
    PLOT_STRUCTURES,
)


class TestBuildPrompt:
    def test_prompt_contains_genre(self):
        prompt = build_prompt("sci-fi", "AI awakens", 10, 4)
        assert "sci-fi" in prompt

    def test_prompt_contains_premise(self):
        prompt = build_prompt("fantasy", "dragons return", 12, 5)
        assert "dragons return" in prompt

    def test_prompt_contains_chapter_count(self):
        prompt = build_prompt("mystery", "murder on train", 15, 3)
        assert "15" in prompt

    def test_prompt_with_plot_structure(self):
        prompt = build_prompt("sci-fi", "AI", 10, 4, plot_structure="heros_journey")
        assert "Hero's Journey" in prompt

    def test_prompt_with_worldbuilding(self):
        prompt = build_prompt("fantasy", "dragons", 10, 4, worldbuilding=True)
        assert "Worldbuilding" in prompt

    def test_prompt_includes_plot_structure(self):
        prompt = build_prompt("romance", "love story", 10, 2)
        assert "Act 1" in prompt


class TestConfig:
    def test_default_config(self):
        config = load_config()
        assert config["llm"]["temperature"] == 0.8

    def test_deep_merge(self):
        base = {"a": {"b": 1, "c": 2}}
        override = {"a": {"b": 10}}
        _deep_merge(base, override)
        assert base["a"]["b"] == 10
        assert base["a"]["c"] == 2


class TestDataStructures:
    def test_archetypes_not_empty(self):
        assert len(get_character_archetypes()) > 0

    def test_structures_not_empty(self):
        assert len(get_plot_structures()) > 0

    def test_worldbuilding_not_empty(self):
        assert len(get_worldbuilding_categories()) > 0


class TestPlotArc:
    def test_visualize_returns_data(self):
        data = visualize_plot_arc("three_act")
        assert len(data) > 0

    def test_each_point_has_fields(self):
        data = visualize_plot_arc("heros_journey")
        for point in data:
            assert "beat" in point
            assert "tension" in point
            assert "position" in point
