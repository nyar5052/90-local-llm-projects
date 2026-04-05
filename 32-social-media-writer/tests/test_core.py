"""Tests for social_writer.core module."""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime

from social_writer.core import (
    SocialPost,
    build_prompt,
    generate_posts,
    validate_char_count,
    generate_hashtags,
    suggest_schedule,
    generate_ab_variants,
    format_for_platform,
    preview_post,
    load_config,
    _extract_hashtags,
    PLATFORMS,
    TONES,
    PLATFORM_CONFIG,
)


# ---------------------------------------------------------------------------
# SocialPost dataclass
# ---------------------------------------------------------------------------


class TestSocialPost:
    def test_basic_creation(self):
        post = SocialPost(platform="twitter", content="Hello world! #test")
        assert post.platform == "twitter"
        assert post.content == "Hello world! #test"
        assert post.char_count == len("Hello world! #test")
        assert post.is_within_limit is True
        assert post.hashtags == ["#test"]
        assert isinstance(post.created_at, datetime)

    def test_twitter_exceeds_limit(self):
        long_content = "x" * 300
        post = SocialPost(platform="twitter", content=long_content)
        assert post.char_count == 300
        assert post.is_within_limit is False

    def test_linkedin_within_limit(self):
        content = "A professional update about our company. #business #growth"
        post = SocialPost(platform="linkedin", content=content, tone="professional")
        assert post.is_within_limit is True
        assert post.tone == "professional"

    def test_instagram_hashtags_extracted(self):
        content = "Great photo! #travel #adventure #photography"
        post = SocialPost(platform="instagram", content=content)
        assert post.hashtags == ["#travel", "#adventure", "#photography"]

    def test_custom_hashtags_preserved(self):
        post = SocialPost(
            platform="twitter",
            content="Hello",
            hashtags=["#custom", "#tags"],
        )
        assert post.hashtags == ["#custom", "#tags"]

    def test_default_tone(self):
        post = SocialPost(platform="twitter", content="Test")
        assert post.tone == "professional"


# ---------------------------------------------------------------------------
# Extract hashtags helper
# ---------------------------------------------------------------------------


class TestExtractHashtags:
    def test_extracts_basic_hashtags(self):
        assert _extract_hashtags("Hello #world #test") == ["#world", "#test"]

    def test_no_hashtags(self):
        assert _extract_hashtags("Hello world") == []

    def test_hashtag_with_numbers(self):
        assert _extract_hashtags("#python3 #web2024") == ["#python3", "#web2024"]


# ---------------------------------------------------------------------------
# build_prompt
# ---------------------------------------------------------------------------


class TestBuildPrompt:
    def test_twitter_prompt_has_char_limit(self):
        prompt = build_prompt("twitter", "product launch", "excited", 2)
        assert "280" in prompt

    def test_linkedin_prompt_has_platform_name(self):
        prompt = build_prompt("linkedin", "product launch", "professional", 1)
        assert "LinkedIn" in prompt

    def test_instagram_prompt_has_hashtag_count(self):
        prompt = build_prompt("instagram", "new feature", "casual", 1)
        assert "15" in prompt

    def test_prompt_contains_topic(self):
        prompt = build_prompt("twitter", "AI trends", "informative", 1)
        assert "AI trends" in prompt

    def test_prompt_contains_tone(self):
        prompt = build_prompt("linkedin", "hiring", "excited", 3)
        assert "excited" in prompt

    def test_variant_count_in_prompt(self):
        prompt = build_prompt("twitter", "test", "casual", 5)
        assert "5" in prompt


# ---------------------------------------------------------------------------
# generate_posts
# ---------------------------------------------------------------------------


class TestGeneratePosts:
    @patch("social_writer.core.chat")
    def test_generate_returns_content(self, mock_chat):
        mock_chat.return_value = "Variant 1: Exciting news! #tech #launch"
        result = generate_posts("twitter", "launch", "excited", 1)
        assert "Variant 1" in result
        mock_chat.assert_called_once()

    @patch("social_writer.core.chat")
    def test_generate_uses_temperature(self, mock_chat):
        mock_chat.return_value = "Post content"
        generate_posts("linkedin", "update", "professional", 1)
        _, kwargs = mock_chat.call_args
        assert kwargs["temperature"] == 0.8


# ---------------------------------------------------------------------------
# validate_char_count
# ---------------------------------------------------------------------------


class TestValidateCharCount:
    def test_twitter_valid(self):
        is_valid, count, limit = validate_char_count("Short tweet", "twitter")
        assert is_valid is True
        assert count == len("Short tweet")
        assert limit == 280

    def test_twitter_too_long(self):
        content = "a" * 300
        is_valid, count, limit = validate_char_count(content, "twitter")
        assert is_valid is False
        assert count == 300
        assert limit == 280

    def test_linkedin_valid(self):
        content = "A reasonable LinkedIn post."
        is_valid, count, limit = validate_char_count(content, "linkedin")
        assert is_valid is True
        assert limit == 3000

    def test_instagram_at_limit(self):
        content = "x" * 2200
        is_valid, count, limit = validate_char_count(content, "instagram")
        assert is_valid is True
        assert count == 2200

    def test_empty_content(self):
        is_valid, count, limit = validate_char_count("", "twitter")
        assert is_valid is True
        assert count == 0


# ---------------------------------------------------------------------------
# generate_hashtags
# ---------------------------------------------------------------------------


class TestGenerateHashtags:
    @patch("social_writer.core.chat")
    def test_generates_hashtags(self, mock_chat):
        mock_chat.return_value = "#AI\n#MachineLearning\n#Tech"
        result = generate_hashtags("artificial intelligence", "twitter")
        assert "#AI" in result
        mock_chat.assert_called_once()

    @patch("social_writer.core.chat")
    def test_custom_count(self, mock_chat):
        mock_chat.return_value = "#one\n#two"
        generate_hashtags("topic", "twitter", count=2)
        call_args = mock_chat.call_args
        # The prompt should mention "2"
        prompt_content = call_args[0][0][0]["content"]
        assert "2" in prompt_content


# ---------------------------------------------------------------------------
# suggest_schedule
# ---------------------------------------------------------------------------


class TestSuggestSchedule:
    def test_twitter_schedule(self):
        times = suggest_schedule("twitter")
        assert isinstance(times, list)
        assert len(times) >= 1

    def test_linkedin_schedule(self):
        times = suggest_schedule("linkedin")
        assert isinstance(times, list)
        assert len(times) >= 1

    def test_instagram_schedule(self):
        times = suggest_schedule("instagram")
        assert isinstance(times, list)
        assert len(times) >= 1


# ---------------------------------------------------------------------------
# generate_ab_variants
# ---------------------------------------------------------------------------


class TestGenerateABVariants:
    @patch("social_writer.core.chat")
    def test_ab_variants(self, mock_chat):
        mock_chat.return_value = "Variant A: Question?\nVariant B: Bold statement!"
        result = generate_ab_variants("AI tools", "twitter", "excited", 2)
        assert "Variant A" in result
        mock_chat.assert_called_once()

    @patch("social_writer.core.chat")
    def test_ab_uses_high_temperature(self, mock_chat):
        mock_chat.return_value = "Variants"
        generate_ab_variants("topic", "linkedin", "professional", 2)
        _, kwargs = mock_chat.call_args
        assert kwargs["temperature"] == 0.9


# ---------------------------------------------------------------------------
# format_for_platform
# ---------------------------------------------------------------------------


class TestFormatForPlatform:
    def test_twitter_compact(self):
        content = "Hello    world\n\nnew  line"
        result = format_for_platform(content, "twitter")
        assert "    " not in result  # Extra spaces removed
        assert "\n" not in result

    def test_twitter_truncation(self):
        content = "x" * 300
        result = format_for_platform(content, "twitter")
        assert len(result) <= 280
        assert result.endswith("...")

    def test_linkedin_paragraphs(self):
        content = "First paragraph.\nSecond paragraph.\nThird."
        result = format_for_platform(content, "linkedin")
        assert "\n\n" in result

    def test_instagram_emoji(self):
        content = "Great day for coding"
        result = format_for_platform(content, "instagram")
        assert "✨" in result

    def test_instagram_hashtag_separation(self):
        content = "Great post #coding #python"
        result = format_for_platform(content, "instagram")
        assert ".\n.\n." in result

    def test_unknown_platform_passthrough(self):
        content = "Some content"
        result = format_for_platform(content, "unknown_platform")
        assert result == content


# ---------------------------------------------------------------------------
# preview_post
# ---------------------------------------------------------------------------


class TestPreviewPost:
    def test_basic_preview(self):
        content = "A short tweet #tech #AI #ML"
        preview = preview_post(content, "twitter")
        assert "char_count" in preview
        assert "is_valid" in preview
        assert "hashtag_count" in preview
        assert "estimated_reach_score" in preview

    def test_valid_tweet(self):
        content = "Short tweet #tech"
        preview = preview_post(content, "twitter")
        assert preview["is_valid"] is True
        assert preview["char_count"] == len(content)

    def test_invalid_tweet(self):
        content = "x" * 300
        preview = preview_post(content, "twitter")
        assert preview["is_valid"] is False

    def test_hashtag_count(self):
        content = "Post #one #two #three"
        preview = preview_post(content, "twitter")
        assert preview["hashtag_count"] == 3

    def test_reach_score_range(self):
        content = "A post with #good #content"
        preview = preview_post(content, "twitter")
        assert 0 <= preview["estimated_reach_score"] <= 100

    def test_optimal_length_boosts_score(self):
        # ~80% of 280 = 224 chars
        optimal = "x" * 220 + " #tag1 #tag2 #tag3"
        short = "Hi #tag1 #tag2 #tag3"
        score_optimal = preview_post(optimal, "twitter")["estimated_reach_score"]
        score_short = preview_post(short, "twitter")["estimated_reach_score"]
        assert score_optimal >= score_short


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------


class TestConstants:
    def test_platforms_list(self):
        assert "twitter" in PLATFORMS
        assert "linkedin" in PLATFORMS
        assert "instagram" in PLATFORMS

    def test_tones_list(self):
        assert "professional" in TONES
        assert "casual" in TONES

    def test_platform_config_keys(self):
        for plat in PLATFORMS:
            assert plat in PLATFORM_CONFIG
            assert "max_chars" in PLATFORM_CONFIG[plat]
            assert "name" in PLATFORM_CONFIG[plat]
            assert "hashtag_count" in PLATFORM_CONFIG[plat]
