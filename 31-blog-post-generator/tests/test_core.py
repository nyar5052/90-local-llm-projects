"""Tests for blog_gen.core module."""

import os
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime

from blog_gen.core import (
    build_prompt,
    generate_blog_post,
    generate_outline,
    generate_multiple_drafts,
    score_seo,
    analyze_tone,
    export_markdown,
    parse_blog_post,
    BlogPost,
    load_config,
    _extract_title,
    _extract_meta_description,
)


# ---------------------------------------------------------------------------
# Sample content fixtures
# ---------------------------------------------------------------------------

SAMPLE_BLOG_POST = """\
# AI in Healthcare: Transforming Patient Care

> Discover how artificial intelligence and machine learning are revolutionizing healthcare.

## Introduction

The healthcare industry is undergoing a major transformation driven by AI and machine learning.
Modern hospitals leverage ML algorithms to improve diagnosis accuracy and streamline patient care.

## How ML Powers Modern Diagnosis

Machine learning models analyze vast datasets of medical images and patient records.
These algorithms can detect patterns that human physicians might miss, leading to earlier
diagnosis of conditions like cancer and heart disease.

## The Role of Data in Patient Care

Data-driven approaches enable personalized treatment plans. By analyzing patient history
and genetic information, AI systems recommend optimal therapies tailored to individual needs.

## Challenges and Ethical Considerations

Despite the benefits, implementing AI in healthcare raises ethical questions about
data privacy, algorithmic bias, and the role of human oversight in medical decisions.

## Conclusion

AI and machine learning are set to transform healthcare fundamentally. Organizations
that embrace these technologies will be better positioned to deliver improved patient outcomes.
"""

SAMPLE_NO_META = """\
# Simple Post

## Section One

Some content here about technology and innovation.

## Section Two

More content discussing various topics.

## Section Three

Final section with concluding thoughts.
"""


# ---------------------------------------------------------------------------
# TestBuildPrompt
# ---------------------------------------------------------------------------


class TestBuildPrompt:
    def test_prompt_contains_topic(self):
        prompt = build_prompt("AI in Healthcare", ["ML", "diagnosis"], "professional", 800)
        assert "AI in Healthcare" in prompt

    def test_prompt_contains_keywords(self):
        prompt = build_prompt("AI", ["ML", "diagnosis"], "professional", 800)
        assert "ML" in prompt
        assert "diagnosis" in prompt

    def test_prompt_contains_tone(self):
        prompt = build_prompt("AI", [], "casual", 500)
        assert "casual" in prompt

    def test_prompt_contains_length(self):
        prompt = build_prompt("AI", [], "technical", 1200)
        assert "1200" in prompt

    def test_prompt_no_keywords(self):
        prompt = build_prompt("AI", [], "professional", 800)
        assert "none specified" in prompt

    def test_prompt_multiple_keywords(self):
        prompt = build_prompt("Tech", ["a", "b", "c"], "friendly", 600)
        assert "a, b, c" in prompt


# ---------------------------------------------------------------------------
# TestScoreSeo
# ---------------------------------------------------------------------------


class TestScoreSeo:
    def test_high_score_with_good_content(self):
        seo = score_seo(SAMPLE_BLOG_POST, ["AI", "machine learning", "healthcare"])
        assert seo["total"] > 0
        assert "keyword_density" in seo
        assert "heading_structure" in seo
        assert "meta_description" in seo
        assert "content_length" in seo

    def test_heading_structure_with_h1_and_h2s(self):
        seo = score_seo(SAMPLE_BLOG_POST, [])
        assert seo["heading_structure"] == 25.0  # H1 (10) + >=3 H2s (15)

    def test_meta_description_present(self):
        seo = score_seo(SAMPLE_BLOG_POST, [])
        assert seo["meta_description"] == 20.0

    def test_meta_description_absent(self):
        seo = score_seo(SAMPLE_NO_META, [])
        assert seo["meta_description"] == 0.0

    def test_no_keywords_gives_neutral(self):
        seo = score_seo(SAMPLE_BLOG_POST, [])
        assert seo["keyword_density"] == 15.0  # neutral score

    def test_content_length_scoring(self):
        short_content = "# Title\n\n> Meta\n\nShort."
        seo = score_seo(short_content, [])
        assert seo["content_length"] < 25.0

    def test_total_is_sum_of_parts(self):
        seo = score_seo(SAMPLE_BLOG_POST, ["AI"])
        expected = (
            seo["keyword_density"]
            + seo["heading_structure"]
            + seo["meta_description"]
            + seo["content_length"]
        )
        assert abs(seo["total"] - expected) < 0.2

    def test_empty_content(self):
        seo = score_seo("", [])
        assert seo["total"] >= 0

    def test_keywords_not_present_gives_zero_density(self):
        seo = score_seo("# Title\n\n> Meta\n\nNo keywords here at all.", ["xyzzy123"])
        assert seo["keyword_density"] == 0.0


# ---------------------------------------------------------------------------
# TestGenerateOutline
# ---------------------------------------------------------------------------


class TestGenerateOutline:
    @patch("blog_gen.core.chat")
    def test_returns_outline(self, mock_chat):
        mock_chat.return_value = "# Outline\n\n## Section 1\n- point a\n- point b\n"
        result = generate_outline("AI", ["ML"], "professional")
        assert "Outline" in result
        mock_chat.assert_called_once()

    @patch("blog_gen.core.chat")
    def test_system_prompt_is_strategist(self, mock_chat):
        mock_chat.return_value = "# Outline"
        generate_outline("AI", [], "casual")
        args, kwargs = mock_chat.call_args
        assert "strategist" in kwargs.get("system_prompt", "").lower()


# ---------------------------------------------------------------------------
# TestGenerateMultipleDrafts
# ---------------------------------------------------------------------------


class TestGenerateMultipleDrafts:
    @patch("blog_gen.core.chat")
    def test_returns_correct_number_of_drafts(self, mock_chat):
        mock_chat.return_value = "# Draft\n\nContent."
        drafts = generate_multiple_drafts("AI", ["ML"], "professional", 800, num_drafts=3)
        assert len(drafts) == 3

    @patch("blog_gen.core.chat")
    def test_caps_at_max_drafts(self, mock_chat):
        mock_chat.return_value = "# Draft"
        drafts = generate_multiple_drafts("AI", [], "casual", 500, num_drafts=100)
        assert len(drafts) <= 5  # max_drafts from config

    @patch("blog_gen.core.chat")
    def test_varying_temperatures(self, mock_chat):
        mock_chat.return_value = "# Draft"
        generate_multiple_drafts("AI", [], "professional", 800, num_drafts=3)
        temps = [call.kwargs.get("temperature", 0) for call in mock_chat.call_args_list]
        assert len(set(temps)) > 1  # temperatures should differ


# ---------------------------------------------------------------------------
# TestAnalyzeTone
# ---------------------------------------------------------------------------


class TestAnalyzeTone:
    def test_returns_all_tones(self):
        result = analyze_tone(SAMPLE_BLOG_POST)
        for tone in ["professional", "casual", "technical", "friendly", "persuasive"]:
            assert tone in result

    def test_dominant_tone_key_present(self):
        result = analyze_tone(SAMPLE_BLOG_POST)
        assert "dominant_tone" in result

    def test_technical_content_detected(self):
        tech_content = (
            "The algorithm processes data through the API framework. "
            "Configure the database module and deploy the implementation. "
            "The architecture uses protocol-based parameters."
        )
        result = analyze_tone(tech_content)
        assert result["technical"] > 0

    def test_casual_content_detected(self):
        casual_content = (
            "Hey, let's talk about some pretty cool stuff! "
            "You're gonna love this awesome thing we found. "
            "Your feedback is super important, right?"
        )
        result = analyze_tone(casual_content)
        assert result["casual"] > 0

    def test_scores_between_zero_and_one(self):
        result = analyze_tone(SAMPLE_BLOG_POST)
        for tone in ["professional", "casual", "technical", "friendly", "persuasive"]:
            assert 0 <= result[tone] <= 1

    def test_empty_content(self):
        result = analyze_tone("")
        assert result["dominant_tone"] in ["professional", "casual", "technical", "friendly", "persuasive"]


# ---------------------------------------------------------------------------
# TestExportMarkdown
# ---------------------------------------------------------------------------


class TestExportMarkdown:
    def test_creates_file(self, tmp_path):
        filepath = str(tmp_path / "test_export.md")
        result = export_markdown(SAMPLE_BLOG_POST, filepath, keywords=["AI", "healthcare"])
        assert os.path.isfile(result)

    def test_file_contains_frontmatter(self, tmp_path):
        filepath = str(tmp_path / "test_fm.md")
        export_markdown(SAMPLE_BLOG_POST, filepath, keywords=["AI"])
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()
        assert text.startswith("---\n")
        assert "title:" in text
        assert "date:" in text
        assert "keywords:" in text
        assert "seo_score:" in text

    def test_file_contains_original_content(self, tmp_path):
        filepath = str(tmp_path / "test_content.md")
        export_markdown(SAMPLE_BLOG_POST, filepath)
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()
        assert "AI in Healthcare" in text

    def test_returns_absolute_path(self, tmp_path):
        filepath = str(tmp_path / "abs.md")
        result = export_markdown(SAMPLE_BLOG_POST, filepath)
        assert os.path.isabs(result)


# ---------------------------------------------------------------------------
# TestBlogPostDataclass
# ---------------------------------------------------------------------------


class TestBlogPostDataclass:
    def test_auto_word_count(self):
        post = BlogPost(title="Test", content="one two three four five")
        assert post.word_count == 5

    def test_explicit_word_count(self):
        post = BlogPost(title="Test", content="one two three", word_count=99)
        assert post.word_count == 99

    def test_default_tone(self):
        post = BlogPost(title="Test", content="content")
        assert post.tone == "professional"

    def test_default_seo_score(self):
        post = BlogPost(title="Test", content="content")
        assert post.seo_score == 0.0

    def test_created_at_populated(self):
        post = BlogPost(title="Test", content="content")
        assert post.created_at  # not empty

    def test_keywords_default_empty(self):
        post = BlogPost(title="Test", content="content")
        assert post.keywords == []


# ---------------------------------------------------------------------------
# TestGenerateBlogPost
# ---------------------------------------------------------------------------


class TestGenerateBlogPost:
    @patch("blog_gen.core.chat")
    def test_generate_returns_content(self, mock_chat):
        mock_chat.return_value = "# Test Blog Post\n\nThis is a test blog post."
        result = generate_blog_post("AI", ["ML"], "professional", 800)
        assert "Test Blog Post" in result
        mock_chat.assert_called_once()

    @patch("blog_gen.core.chat")
    def test_generate_passes_system_prompt(self, mock_chat):
        mock_chat.return_value = "# Post"
        generate_blog_post("AI", [], "casual", 500)
        _, kwargs = mock_chat.call_args
        assert "SEO" in kwargs["system_prompt"]


# ---------------------------------------------------------------------------
# TestHelperFunctions
# ---------------------------------------------------------------------------


class TestHelperFunctions:
    def test_extract_title(self):
        assert _extract_title("# My Title\n\nContent") == "My Title"

    def test_extract_title_missing(self):
        assert _extract_title("No heading here") == "Untitled"

    def test_extract_meta(self):
        assert _extract_meta_description("> This is the meta\n\nContent") == "This is the meta"

    def test_extract_meta_missing(self):
        assert _extract_meta_description("No blockquote") == ""

    def test_parse_blog_post(self):
        post = parse_blog_post(SAMPLE_BLOG_POST, keywords=["AI"], tone="technical")
        assert post.title == "AI in Healthcare: Transforming Patient Care"
        assert post.tone == "technical"
        assert post.seo_score > 0
        assert post.word_count > 0
        assert post.meta_description != ""
