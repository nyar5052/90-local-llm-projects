"""Tests for sales_email_gen.core module."""

import pytest
from unittest.mock import patch, MagicMock

from src.sales_email_gen.core import (
    TONE_DESCRIPTIONS,
    TEMPLATE_LIBRARY,
    generate_email,
    generate_variants,
    research_prospect,
    generate_follow_up_sequence,
    score_personalization,
    get_template,
    list_templates,
    load_config,
    _parse_email_response,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

MOCK_CHAT = "src.sales_email_gen.core.chat"
MOCK_CONFIG = "src.sales_email_gen.core.load_config"


def _fake_config(*_args, **_kwargs):
    return {
        "model": {"name": "gemma3", "temperature": 0.7, "max_tokens": 2000},
        "sequence": {"default_emails": 4, "delay_days": [0, 3, 7, 14]},
    }


# ---------------------------------------------------------------------------
# TestGenerateEmail
# ---------------------------------------------------------------------------


class TestGenerateEmail:
    @patch(MOCK_CONFIG, side_effect=_fake_config)
    @patch(MOCK_CHAT)
    def test_generate_professional_email(self, mock_chat, _cfg):
        mock_chat.return_value = (
            "Subject: Elevate Your AI Strategy with Our Platform\n\n"
            "Dear CTO,\n\n"
            "I noticed your startup is making waves in the AI space..."
        )
        result = generate_email("CTO at startup", "AI Platform", "professional")
        assert result["subject"] == "Elevate Your AI Strategy with Our Platform"
        assert len(result["body"]) > 0

    @patch(MOCK_CONFIG, side_effect=_fake_config)
    @patch(MOCK_CHAT)
    def test_generate_follow_up_email(self, mock_chat, _cfg):
        mock_chat.return_value = (
            "Subject: Following Up on Our AI Platform Discussion\n\n"
            "Hi,\n\nI wanted to follow up on our previous conversation..."
        )
        result = generate_email(
            "CTO at startup", "AI Platform", "professional", follow_up=True
        )
        assert "subject" in result
        assert "body" in result

    @patch(MOCK_CONFIG, side_effect=_fake_config)
    @patch(MOCK_CHAT)
    def test_email_without_subject_line(self, mock_chat, _cfg):
        mock_chat.return_value = "Dear CTO,\n\nI'd like to introduce our platform..."
        result = generate_email("CTO", "Product", "casual")
        assert result["subject"] == "Follow Up"
        assert len(result["body"]) > 0

    @patch(MOCK_CONFIG, side_effect=_fake_config)
    @patch(MOCK_CHAT)
    def test_email_with_context(self, mock_chat, _cfg):
        mock_chat.return_value = "Subject: Test\n\nBody here"
        generate_email("VP Eng", "Tool", "professional", context="Met at conference")
        call_args = mock_chat.call_args
        messages = call_args[0][0]
        assert "conference" in messages[0]["content"]


# ---------------------------------------------------------------------------
# TestGenerateVariants
# ---------------------------------------------------------------------------


class TestGenerateVariants:
    @patch(MOCK_CHAT)
    def test_generate_multiple_variants(self, mock_chat):
        mock_chat.return_value = "Subject: Test Variant\n\nBody content here"
        variants = generate_variants("CTO", "Product", "professional", count=3)
        assert len(variants) == 3
        assert mock_chat.call_count == 3


# ---------------------------------------------------------------------------
# TestToneDescriptions
# ---------------------------------------------------------------------------


class TestToneDescriptions:
    def test_all_tones_defined(self):
        for tone in ["professional", "casual", "persuasive", "consultative"]:
            assert tone in TONE_DESCRIPTIONS


# ---------------------------------------------------------------------------
# TestResearchProspect
# ---------------------------------------------------------------------------


class TestResearchProspect:
    @patch(MOCK_CHAT)
    def test_research_returns_profile(self, mock_chat):
        mock_chat.return_value = (
            "PAIN_POINTS:\n"
            "- Scaling infrastructure is expensive\n"
            "- Talent acquisition in AI is difficult\n"
            "TALKING_POINTS:\n"
            "- Recent Series B funding\n"
            "- Expanding into EU market\n"
            "INDUSTRY_CONTEXT:\n"
            "The AI SaaS market is growing rapidly."
        )
        result = research_prospect("CTO at AI startup, Series B, 200 employees")
        assert len(result["pain_points"]) == 2
        assert len(result["talking_points"]) == 2
        assert "AI SaaS" in result["industry_context"]

    @patch(MOCK_CHAT)
    def test_research_empty_response(self, mock_chat):
        mock_chat.return_value = ""
        result = research_prospect("Unknown prospect")
        assert result["pain_points"] == []
        assert result["talking_points"] == []
        assert result["industry_context"] == ""


# ---------------------------------------------------------------------------
# TestGenerateFollowUpSequence
# ---------------------------------------------------------------------------


class TestGenerateFollowUpSequence:
    @patch(MOCK_CONFIG, side_effect=_fake_config)
    @patch(MOCK_CHAT)
    def test_sequence_length(self, mock_chat, _cfg):
        mock_chat.return_value = "Subject: Follow Up\n\nBody here"
        seq = generate_follow_up_sequence("CTO", "Product", "professional", num_emails=4)
        assert len(seq) == 4
        assert mock_chat.call_count == 4

    @patch(MOCK_CONFIG, side_effect=_fake_config)
    @patch(MOCK_CHAT)
    def test_sequence_has_steps(self, mock_chat, _cfg):
        mock_chat.return_value = "Subject: Step Email\n\nContent"
        seq = generate_follow_up_sequence("CTO", "Product", "professional", num_emails=3)
        steps = [e["step"] for e in seq]
        assert steps == ["intro", "value_add", "case_study"]

    @patch(MOCK_CONFIG, side_effect=_fake_config)
    @patch(MOCK_CHAT)
    def test_sequence_has_delay_days(self, mock_chat, _cfg):
        mock_chat.return_value = "Subject: Delay\n\nBody"
        seq = generate_follow_up_sequence("CTO", "Product", "professional", num_emails=4)
        assert seq[0]["delay_days"] == 0
        assert seq[1]["delay_days"] == 3


# ---------------------------------------------------------------------------
# TestScorePersonalization
# ---------------------------------------------------------------------------


class TestScorePersonalization:
    @patch(MOCK_CHAT)
    def test_score_returns_dict(self, mock_chat):
        mock_chat.return_value = (
            "SCORE: 75\n"
            "SUGGESTIONS:\n"
            "- Mention the prospect's recent funding round\n"
            "- Reference specific product features relevant to their stack"
        )
        result = score_personalization("Hello, I'd like to show you our product.", "CTO at startup")
        assert result["score"] == 75
        assert len(result["suggestions"]) == 2

    @patch(MOCK_CHAT)
    def test_score_caps_at_100(self, mock_chat):
        mock_chat.return_value = "SCORE: 150\nSUGGESTIONS:\n- none"
        result = score_personalization("body", "info")
        assert result["score"] == 100


# ---------------------------------------------------------------------------
# TestTemplates
# ---------------------------------------------------------------------------


class TestTemplates:
    def test_list_templates(self):
        names = list_templates()
        assert "cold_outreach" in names
        assert "follow_up" in names
        assert "demo_request" in names
        assert "case_study" in names
        assert "break_up" in names

    def test_get_template(self):
        tmpl = get_template("cold_outreach")
        assert "description" in tmpl
        assert "word_count" in tmpl
        assert "structure" in tmpl

    def test_get_template_not_found(self):
        with pytest.raises(KeyError, match="not found"):
            get_template("nonexistent_template")


# ---------------------------------------------------------------------------
# TestParseEmailResponse
# ---------------------------------------------------------------------------


class TestParseEmailResponse:
    def test_parse_with_subject(self):
        resp = "Subject: Hello World\n\nDear Friend,\nHow are you?"
        result = _parse_email_response(resp)
        assert result["subject"] == "Hello World"
        assert "Dear Friend" in result["body"]

    def test_parse_without_subject(self):
        resp = "Dear Friend,\nHow are you?"
        result = _parse_email_response(resp)
        assert result["subject"] == "Follow Up"
        assert "Dear Friend" in result["body"]

    def test_parse_custom_fallback(self):
        resp = "Just a body"
        result = _parse_email_response(resp, fallback_subject="Custom")
        assert result["subject"] == "Custom"


# ---------------------------------------------------------------------------
# TestLoadConfig
# ---------------------------------------------------------------------------


class TestLoadConfig:
    def test_load_config_missing_file(self):
        config = load_config("nonexistent_path_12345.yaml")
        assert config == {}
