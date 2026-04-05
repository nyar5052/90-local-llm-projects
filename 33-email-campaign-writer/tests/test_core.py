"""Tests for email_campaign.core module."""

import pytest
from unittest.mock import patch, MagicMock
from email_campaign.core import (
    Email,
    Campaign,
    CAMPAIGN_TYPES,
    build_prompt,
    generate_campaign,
    build_email_sequence,
    generate_subject_variants,
    extract_personalization_tokens,
    preview_html,
    render_email,
    calculate_sequence_timeline,
    estimate_campaign_metrics,
    load_config,
)


# ---------------------------------------------------------------------------
# CAMPAIGN_TYPES
# ---------------------------------------------------------------------------


class TestCampaignTypes:
    def test_campaign_types_list(self):
        assert isinstance(CAMPAIGN_TYPES, list)
        assert len(CAMPAIGN_TYPES) == 5

    def test_contains_expected_types(self):
        for ct in ["welcome", "promotional", "nurture", "re-engagement", "product-launch"]:
            assert ct in CAMPAIGN_TYPES


# ---------------------------------------------------------------------------
# build_prompt
# ---------------------------------------------------------------------------


class TestBuildPrompt:
    def test_prompt_contains_product(self):
        prompt = build_prompt("SaaS Tool", "developers", 3, "promotional")
        assert "SaaS Tool" in prompt

    def test_prompt_contains_audience(self):
        prompt = build_prompt("SaaS Tool", "developers", 3, "promotional")
        assert "developers" in prompt

    def test_prompt_contains_email_count(self):
        prompt = build_prompt("SaaS Tool", "developers", 5, "promotional")
        assert "5" in prompt

    def test_prompt_contains_campaign_type(self):
        prompt = build_prompt("App", "users", 3, "welcome")
        assert "welcome" in prompt

    def test_prompt_requests_subject_lines(self):
        prompt = build_prompt("App", "users", 3, "nurture")
        assert "Subject Line" in prompt

    def test_prompt_mentions_ab_variants(self):
        prompt = build_prompt("X", "Y", 1, "promotional")
        assert "A/B" in prompt

    def test_prompt_mentions_cta(self):
        prompt = build_prompt("X", "Y", 1, "promotional")
        assert "Call to Action" in prompt


# ---------------------------------------------------------------------------
# Email dataclass
# ---------------------------------------------------------------------------


class TestEmailDataclass:
    def test_creation(self):
        email = Email(
            subject_a="Subject A",
            subject_b="Subject B",
            preview_text="Preview",
            body="Hello {{first_name}}, check out {{product}}!",
            cta_text="Buy Now",
        )
        assert email.subject_a == "Subject A"
        assert email.cta_text == "Buy Now"

    def test_auto_extracts_tokens(self):
        email = Email(
            subject_a="A",
            subject_b="B",
            preview_text="P",
            body="Hi {{first_name}}, your {{company}} account is ready.",
            cta_text="Go",
        )
        assert "first_name" in email.personalization_tokens
        assert "company" in email.personalization_tokens

    def test_default_send_day(self):
        email = Email(subject_a="A", subject_b="B", preview_text="P", body="body", cta_text="Go")
        assert email.send_day == 0

    def test_custom_send_day(self):
        email = Email(subject_a="A", subject_b="B", preview_text="P", body="body", cta_text="Go", send_day=7)
        assert email.send_day == 7


# ---------------------------------------------------------------------------
# Campaign dataclass
# ---------------------------------------------------------------------------


class TestCampaignDataclass:
    def test_creation(self):
        c = Campaign(name="Test", product="P", audience="A", campaign_type="welcome")
        assert c.name == "Test"
        assert c.emails == []
        assert c.created_at  # should be auto-set

    def test_with_emails(self):
        emails = [
            Email(subject_a="A1", subject_b="B1", preview_text="P1", body="body1", cta_text="CTA1"),
            Email(subject_a="A2", subject_b="B2", preview_text="P2", body="body2", cta_text="CTA2"),
        ]
        c = Campaign(name="C", product="P", audience="A", campaign_type="nurture", emails=emails)
        assert len(c.emails) == 2


# ---------------------------------------------------------------------------
# generate_campaign
# ---------------------------------------------------------------------------


class TestGenerateCampaign:
    @patch("email_campaign.core.chat")
    def test_generate_returns_content(self, mock_chat):
        mock_chat.return_value = "## Email 1\n**Subject:** Welcome!\n\nBody content..."
        result = generate_campaign("SaaS Tool", "developers", 3, "promotional")
        assert "Email 1" in result
        mock_chat.assert_called_once()

    @patch("email_campaign.core.chat")
    def test_generate_uses_correct_max_tokens(self, mock_chat):
        mock_chat.return_value = "Campaign content"
        generate_campaign("SaaS Tool", "developers", 3, "promotional")
        _, kwargs = mock_chat.call_args
        assert kwargs["max_tokens"] == 4096


# ---------------------------------------------------------------------------
# build_email_sequence
# ---------------------------------------------------------------------------


class TestBuildEmailSequence:
    @patch("email_campaign.core.chat")
    def test_returns_campaign(self, mock_chat):
        mock_chat.return_value = "## Email 1\nSubject: Test\n\nBody"
        campaign = build_email_sequence("SaaS Tool", "developers", 3, "promotional")
        assert isinstance(campaign, Campaign)
        assert len(campaign.emails) == 3

    @patch("email_campaign.core.chat")
    def test_emails_have_send_days(self, mock_chat):
        mock_chat.return_value = "Campaign content"
        campaign = build_email_sequence("Tool", "devs", 3, "welcome")
        days = [e.send_day for e in campaign.emails]
        assert days == [0, 1, 3]

    @patch("email_campaign.core.chat")
    def test_campaign_name(self, mock_chat):
        mock_chat.return_value = "Content"
        campaign = build_email_sequence("Acme", "users", 2, "nurture")
        assert "Acme" in campaign.name
        assert "Nurture" in campaign.name


# ---------------------------------------------------------------------------
# generate_subject_variants
# ---------------------------------------------------------------------------


class TestGenerateSubjectVariants:
    @patch("email_campaign.core.chat")
    def test_returns_list(self, mock_chat):
        mock_chat.return_value = "1. First subject\n2. Second subject\n3. Third subject"
        variants = generate_subject_variants("Tool", "devs", 3)
        assert isinstance(variants, list)
        assert len(variants) == 3

    @patch("email_campaign.core.chat")
    def test_strips_numbering(self, mock_chat):
        mock_chat.return_value = "1. First subject\n2. Second subject"
        variants = generate_subject_variants("Tool", "devs", 2)
        assert not variants[0].startswith("1.")
        assert not variants[1].startswith("2.")


# ---------------------------------------------------------------------------
# extract_personalization_tokens
# ---------------------------------------------------------------------------


class TestExtractPersonalizationTokens:
    def test_finds_tokens(self):
        text = "Hello {{first_name}}, welcome to {{company}}!"
        tokens = extract_personalization_tokens(text)
        assert tokens == ["company", "first_name"]

    def test_deduplicates(self):
        text = "{{name}} and {{name}} again"
        tokens = extract_personalization_tokens(text)
        assert tokens == ["name"]

    def test_no_tokens(self):
        text = "Plain text with no placeholders."
        tokens = extract_personalization_tokens(text)
        assert tokens == []

    def test_multiple_tokens(self):
        text = "{{a}} {{b}} {{c}} {{d}}"
        tokens = extract_personalization_tokens(text)
        assert tokens == ["a", "b", "c", "d"]

    def test_ignores_non_word_chars(self):
        text = "{{first name}} {{first_name}}"
        tokens = extract_personalization_tokens(text)
        assert "first_name" in tokens


# ---------------------------------------------------------------------------
# preview_html
# ---------------------------------------------------------------------------


class TestPreviewHtml:
    def test_returns_html(self):
        html = preview_html("Hello World")
        assert "<!DOCTYPE html>" in html
        assert "Hello World" in html

    def test_escapes_html_entities(self):
        html = preview_html("Use <b>bold</b> & more")
        assert "&lt;b&gt;" in html
        assert "&amp;" in html

    def test_wraps_in_table(self):
        html = preview_html("Test")
        assert "<table" in html
        assert "600" in html

    def test_multiline(self):
        html = preview_html("Line 1\nLine 2\nLine 3")
        assert "Line 1" in html
        assert "Line 3" in html


# ---------------------------------------------------------------------------
# render_email
# ---------------------------------------------------------------------------


class TestRenderEmail:
    def test_replaces_tokens(self):
        email = Email(
            subject_a="A", subject_b="B", preview_text="P",
            body="Hello {{first_name}}, welcome to {{company}}!",
            cta_text="Go",
        )
        result = render_email(email, {"first_name": "Jane", "company": "Acme"})
        assert "Jane" in result
        assert "Acme" in result
        assert "{{first_name}}" not in result

    def test_leaves_unknown_tokens(self):
        email = Email(
            subject_a="A", subject_b="B", preview_text="P",
            body="Hello {{first_name}}, your {{unknown_field}}.",
            cta_text="Go",
        )
        result = render_email(email, {"first_name": "Bob"})
        assert "Bob" in result
        assert "{{unknown_field}}" in result

    def test_empty_user_data(self):
        email = Email(
            subject_a="A", subject_b="B", preview_text="P",
            body="Hello {{first_name}}!",
            cta_text="Go",
        )
        result = render_email(email, {})
        assert "{{first_name}}" in result


# ---------------------------------------------------------------------------
# calculate_sequence_timeline
# ---------------------------------------------------------------------------


class TestCalculateSequenceTimeline:
    def test_returns_list_of_tuples(self):
        emails = [
            Email(subject_a="Intro", subject_b="B", preview_text="P", body="b", cta_text="Go", send_day=0),
            Email(subject_a="Follow up", subject_b="B", preview_text="P", body="b", cta_text="Go", send_day=3),
        ]
        campaign = Campaign(name="C", product="P", audience="A", campaign_type="welcome", emails=emails)
        tl = calculate_sequence_timeline(campaign)
        assert tl == [(0, "Intro"), (3, "Follow up")]

    def test_empty_campaign(self):
        campaign = Campaign(name="C", product="P", audience="A", campaign_type="welcome")
        tl = calculate_sequence_timeline(campaign)
        assert tl == []


# ---------------------------------------------------------------------------
# estimate_campaign_metrics
# ---------------------------------------------------------------------------


class TestEstimateCampaignMetrics:
    def test_returns_dict(self):
        emails = [
            Email(subject_a="A", subject_b="B", preview_text="P", body="b", cta_text="Go"),
        ]
        campaign = Campaign(name="C", product="P", audience="A", campaign_type="welcome", emails=emails)
        metrics = estimate_campaign_metrics(campaign)
        assert "avg_open_rate" in metrics
        assert "avg_click_rate" in metrics
        assert "per_email" in metrics

    def test_per_email_count(self):
        emails = [
            Email(subject_a="A", subject_b="B", preview_text="P", body="b", cta_text="Go"),
            Email(subject_a="A2", subject_b="B2", preview_text="P2", body="b2", cta_text="Go2"),
        ]
        campaign = Campaign(name="C", product="P", audience="A", campaign_type="promotional", emails=emails)
        metrics = estimate_campaign_metrics(campaign)
        assert len(metrics["per_email"]) == 2

    def test_rates_are_positive(self):
        emails = [
            Email(subject_a="A", subject_b="B", preview_text="P", body="b", cta_text="Go"),
        ]
        campaign = Campaign(name="C", product="P", audience="A", campaign_type="nurture", emails=emails)
        metrics = estimate_campaign_metrics(campaign)
        assert metrics["avg_open_rate"] > 0
        assert metrics["avg_click_rate"] > 0

    def test_empty_campaign_metrics(self):
        campaign = Campaign(name="C", product="P", audience="A", campaign_type="welcome")
        metrics = estimate_campaign_metrics(campaign)
        assert metrics["num_emails"] == 0
