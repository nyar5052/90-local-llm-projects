"""Email Campaign Writer - Generate marketing email sequences using a local LLM."""

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
)

__all__ = [
    "Email",
    "Campaign",
    "CAMPAIGN_TYPES",
    "build_prompt",
    "generate_campaign",
    "build_email_sequence",
    "generate_subject_variants",
    "extract_personalization_tokens",
    "preview_html",
    "render_email",
    "calculate_sequence_timeline",
    "estimate_campaign_metrics",
]
