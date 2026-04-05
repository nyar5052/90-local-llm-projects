#!/usr/bin/env python3
"""Streamlit web UI for Email Campaign Writer."""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))

import streamlit as st

from email_campaign.core import (
    CAMPAIGN_TYPES,
    Campaign,
    build_email_sequence,
    calculate_sequence_timeline,
    estimate_campaign_metrics,
    extract_personalization_tokens,
    generate_subject_variants,
    preview_html,
    render_email,
    setup_logging,
)
from common.llm_client import check_ollama_running  # noqa: E402

setup_logging()

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(page_title="Email Campaign Writer", page_icon="📧", layout="wide")
st.title("📧 Email Campaign Writer")
st.caption("Generate professional marketing email sequences using a local LLM")

# ---------------------------------------------------------------------------
# Sidebar – inputs
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("Campaign Settings")

    if not check_ollama_running():
        st.error("⚠️ Ollama is not running. Start it with `ollama serve`.")

    product = st.text_input("Product / Service", placeholder="e.g. SaaS Analytics Tool")
    audience = st.text_input("Target Audience", placeholder="e.g. startup founders")
    campaign_type = st.selectbox("Campaign Type", CAMPAIGN_TYPES, index=1)
    num_emails = st.slider("Number of Emails", min_value=1, max_value=10, value=3)

    generate_btn = st.button("🚀 Generate Campaign", type="primary", use_container_width=True)

    st.divider()
    st.subheader("Subject Line A/B Testing")
    num_variants = st.number_input("Variants", min_value=2, max_value=6, value=3)
    subject_btn = st.button("🔀 Generate Subject Variants", use_container_width=True)

# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------
if "campaign" not in st.session_state:
    st.session_state.campaign = None
if "subject_variants" not in st.session_state:
    st.session_state.subject_variants = []

# ---------------------------------------------------------------------------
# Generate campaign
# ---------------------------------------------------------------------------
if generate_btn:
    if not product or not audience:
        st.warning("Please enter a product and audience.")
    else:
        with st.spinner("Generating campaign…"):
            campaign = build_email_sequence(product, audience, num_emails, campaign_type)
            st.session_state.campaign = campaign
        st.success("Campaign generated!")

# ---------------------------------------------------------------------------
# Generate subject variants
# ---------------------------------------------------------------------------
if subject_btn:
    if not product or not audience:
        st.warning("Please enter a product and audience.")
    else:
        with st.spinner("Generating subject line variants…"):
            variants = generate_subject_variants(product, audience, num_variants)
            st.session_state.subject_variants = variants
        st.success(f"Generated {len(variants)} subject line variants!")

# ---------------------------------------------------------------------------
# Display subject variants
# ---------------------------------------------------------------------------
if st.session_state.subject_variants:
    st.subheader("🔀 Subject Line A/B Variants")
    cols = st.columns(2)
    for idx, variant in enumerate(st.session_state.subject_variants):
        with cols[idx % 2]:
            st.info(f"**Variant {idx + 1}:** {variant}")

# ---------------------------------------------------------------------------
# Display campaign
# ---------------------------------------------------------------------------
campaign: Campaign | None = st.session_state.campaign

if campaign:
    tab_preview, tab_timeline, tab_metrics, tab_html, tab_tokens, tab_json = st.tabs(
        ["📨 Preview", "📅 Timeline", "📊 Metrics", "🌐 HTML", "🔑 Tokens", "💾 JSON"]
    )

    # ---- Preview tab ----
    with tab_preview:
        st.subheader("Email Preview")
        for idx, email in enumerate(campaign.emails):
            with st.expander(f"Email {idx + 1} — {email.subject_a}", expanded=(idx == 0)):
                col_a, col_b = st.columns(2)
                with col_a:
                    st.markdown(f"**Subject A:** {email.subject_a}")
                with col_b:
                    st.markdown(f"**Subject B:** {email.subject_b}")
                st.markdown(f"**Preview Text:** {email.preview_text}")
                st.markdown(f"**CTA:** {email.cta_text}")
                st.markdown(f"**Send Day:** {email.send_day}")
                st.divider()
                st.markdown(email.body)

    # ---- Timeline tab ----
    with tab_timeline:
        st.subheader("Sequence Timeline")
        tl = calculate_sequence_timeline(campaign)
        for day, subj in tl:
            st.markdown(f"**Day {day}** → {subj}")

    # ---- Metrics tab ----
    with tab_metrics:
        st.subheader("Estimated Metrics")
        metrics = estimate_campaign_metrics(campaign)

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Avg Open Rate", f"{metrics['avg_open_rate']:.1%}")
        with col2:
            st.metric("Avg Click Rate", f"{metrics['avg_click_rate']:.1%}")

        st.divider()
        for em in metrics["per_email"]:
            st.markdown(
                f"**Email {em['email_number']}** — "
                f"Open: {em['estimated_open_rate']:.1%}  |  "
                f"Click: {em['estimated_click_rate']:.1%}"
            )

    # ---- HTML preview tab ----
    with tab_html:
        st.subheader("HTML Email Preview")
        if campaign.emails:
            html = preview_html(campaign.emails[0].body)
            with st.expander("View HTML source"):
                st.code(html, language="html")
            st.components.v1.html(html, height=600, scrolling=True)

    # ---- Personalization tokens tab ----
    with tab_tokens:
        st.subheader("Personalization Tokens")
        all_tokens: set[str] = set()
        for email in campaign.emails:
            all_tokens.update(email.personalization_tokens)
        if all_tokens:
            st.write("Tokens found:", ", ".join(f"`{{{{{t}}}}}`" for t in sorted(all_tokens)))
            st.divider()
            st.markdown("**Preview with custom data**")
            user_data: dict[str, str] = {}
            for tok in sorted(all_tokens):
                user_data[tok] = st.text_input(f"{{{{{tok}}}}}", value=tok.replace("_", " ").title(), key=f"tok_{tok}")
            if st.button("Apply Personalization"):
                rendered = render_email(campaign.emails[0], user_data)
                st.markdown(rendered)
        else:
            st.info("No personalization tokens detected in the campaign emails.")

    # ---- JSON download tab ----
    with tab_json:
        st.subheader("Download Campaign")
        campaign_dict = {
            "name": campaign.name,
            "product": campaign.product,
            "audience": campaign.audience,
            "campaign_type": campaign.campaign_type,
            "created_at": campaign.created_at,
            "emails": [
                {
                    "subject_a": e.subject_a,
                    "subject_b": e.subject_b,
                    "preview_text": e.preview_text,
                    "body": e.body,
                    "cta_text": e.cta_text,
                    "cta_url": e.cta_url,
                    "send_day": e.send_day,
                    "personalization_tokens": e.personalization_tokens,
                }
                for e in campaign.emails
            ],
        }
        json_str = json.dumps(campaign_dict, indent=2)
        st.download_button(
            "⬇️ Download Campaign JSON",
            data=json_str,
            file_name="campaign.json",
            mime="application/json",
            use_container_width=True,
        )
        with st.expander("View JSON"):
            st.json(campaign_dict)
