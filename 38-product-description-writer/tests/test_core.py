"""Tests for Product Description Writer core module."""

import pytest
from product_writer.core import (
    build_prompt,
    load_config,
    get_platform_configs,
    map_features_to_benefits,
    calculate_seo_score,
    _deep_merge,
    PLATFORM_CONFIGS,
)


class TestBuildPrompt:
    def test_prompt_contains_product(self):
        prompt = build_prompt("Wireless Headphones", ["noise-cancel"], "amazon", "medium", 2)
        assert "Wireless Headphones" in prompt

    def test_prompt_contains_features(self):
        prompt = build_prompt("Headphones", ["noise-cancel", "bluetooth"], "amazon", "medium", 1)
        assert "noise-cancel" in prompt
        assert "bluetooth" in prompt

    def test_prompt_contains_platform_tips(self):
        prompt = build_prompt("Product", [], "amazon", "medium", 1)
        assert "bullet points" in prompt.lower() or "Amazon" in prompt

    def test_prompt_with_keywords(self):
        prompt = build_prompt("Product", [], "generic", "medium", 1, keywords=["wireless", "headphone"])
        assert "wireless" in prompt


class TestFeatureBenefitMapping:
    def test_known_feature(self):
        mapped = map_features_to_benefits(["waterproof"])
        assert "dry" in mapped[0]["benefit"].lower()

    def test_unknown_feature(self):
        mapped = map_features_to_benefits(["custom-feature"])
        assert mapped[0]["feature"] == "custom-feature"


class TestSEOScore:
    def test_score_with_keywords(self):
        text = "wireless headphones with noise canceling bluetooth technology"
        score = calculate_seo_score(text, ["wireless", "bluetooth"])
        assert score["overall_score"] >= 0
        assert score["keyword_coverage"] > 0

    def test_score_no_keywords(self):
        score = calculate_seo_score("some text", [])
        assert score["overall_score"] == 0


class TestConfig:
    def test_default_config(self):
        config = load_config()
        assert config["llm"]["temperature"] == 0.7

    def test_platforms_exist(self):
        assert len(get_platform_configs()) >= 5
