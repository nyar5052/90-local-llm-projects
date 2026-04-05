#!/usr/bin/env python3
"""Streamlit Web UI for Social Media Writer."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))

import streamlit as st

from social_writer.core import (
    PLATFORMS,
    TONES,
    generate_posts,
    generate_hashtags,
    suggest_schedule,
    generate_ab_variants,
    format_for_platform,
    preview_post,
    validate_char_count,
    load_config,
    setup_logging,
    SocialPost,
    _get_platform_config,
)
from common.llm_client import check_ollama_running

# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Social Media Writer",
    page_icon="✍️",
    layout="wide",
)

setup_logging()

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

st.sidebar.title("✨ Social Media Writer")
st.sidebar.markdown("Create platform-specific social media posts using a local LLM.")

if not check_ollama_running():
    st.sidebar.error("⚠️ Ollama is not running. Start it with: `ollama serve`")
    st.stop()
else:
    st.sidebar.success("✅ Ollama is running")

st.sidebar.markdown("---")
topic = st.sidebar.text_area("📝 Post Topic", placeholder="Enter your post topic here...", height=100)
tone = st.sidebar.selectbox("🎨 Tone", TONES, index=0)
num_variants = st.sidebar.slider("📊 Number of Variants", min_value=1, max_value=5, value=2)

st.sidebar.markdown("---")
st.sidebar.markdown("### ⚙️ Options")
show_schedule = st.sidebar.checkbox("📅 Show best posting times", value=True)
generate_tags_only = st.sidebar.checkbox("#️⃣ Hashtag generator mode")
ab_test_mode = st.sidebar.checkbox("🔬 A/B test mode")

# ---------------------------------------------------------------------------
# Helper rendering functions
# ---------------------------------------------------------------------------


def _char_count_bar(count: int, limit: int) -> None:
    """Render a character count progress bar."""
    ratio = count / limit if limit else 0
    if ratio <= 0.8:
        color = "green"
    elif ratio <= 1.0:
        color = "orange"
    else:
        color = "red"
    st.progress(min(ratio, 1.0))
    st.markdown(
        f"<span style='color:{color};font-weight:bold;'>{count} / {limit} characters</span>",
        unsafe_allow_html=True,
    )


def _render_twitter_card(content: str) -> None:
    """Render a Twitter-style preview card."""
    preview = preview_post(content, "twitter")
    st.markdown(
        f"""
        <div style="background:#15202b;color:#fff;padding:16px;border-radius:16px;
                    font-family:-apple-system,sans-serif;max-width:500px;margin-bottom:12px;">
            <div style="display:flex;align-items:center;margin-bottom:8px;">
                <div style="width:40px;height:40px;border-radius:50%;background:#1da1f2;
                            display:flex;align-items:center;justify-content:center;
                            font-weight:bold;margin-right:10px;">SM</div>
                <div><b>Social Writer</b> <span style="color:#8899a6;">@social_writer</span></div>
            </div>
            <div style="white-space:pre-wrap;line-height:1.4;">{content}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    _char_count_bar(preview["char_count"], 280)


def _render_linkedin_card(content: str) -> None:
    """Render a LinkedIn-style preview card."""
    preview = preview_post(content, "linkedin")
    st.markdown(
        f"""
        <div style="background:#fff;color:#000;padding:16px;border-radius:8px;
                    border:1px solid #e0e0e0;max-width:550px;margin-bottom:12px;
                    font-family:-apple-system,sans-serif;">
            <div style="display:flex;align-items:center;margin-bottom:12px;">
                <div style="width:48px;height:48px;border-radius:50%;background:#0a66c2;
                            display:flex;align-items:center;justify-content:center;
                            color:#fff;font-weight:bold;margin-right:12px;">SM</div>
                <div>
                    <div style="font-weight:bold;">Social Media Writer</div>
                    <div style="color:#666;font-size:12px;">Social Media Marketing Expert</div>
                </div>
            </div>
            <div style="white-space:pre-wrap;line-height:1.6;">{content}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    _char_count_bar(preview["char_count"], 3000)


def _render_instagram_card(content: str) -> None:
    """Render an Instagram-style preview card."""
    preview = preview_post(content, "instagram")
    st.markdown(
        f"""
        <div style="background:#fff;color:#262626;padding:16px;border-radius:8px;
                    border:1px solid #dbdbdb;max-width:500px;margin-bottom:12px;
                    font-family:-apple-system,sans-serif;">
            <div style="display:flex;align-items:center;margin-bottom:12px;">
                <div style="width:32px;height:32px;border-radius:50%;
                            background:linear-gradient(45deg,#f09433,#e6683c,#dc2743,#cc2366,#bc1888);
                            display:flex;align-items:center;justify-content:center;
                            color:#fff;font-weight:bold;margin-right:10px;font-size:12px;">SM</div>
                <div style="font-weight:bold;">social_writer</div>
            </div>
            <div style="background:#fafafa;height:200px;border-radius:4px;
                        display:flex;align-items:center;justify-content:center;
                        margin-bottom:12px;color:#999;">📸 Image Placeholder</div>
            <div style="white-space:pre-wrap;line-height:1.5;">{content}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    _char_count_bar(preview["char_count"], 2200)

    # Hashtag cloud
    import re
    tags = re.findall(r"#\w+", content)
    if tags:
        st.markdown("**Hashtag Cloud:**")
        tag_html = " ".join(
            f"<span style='background:#e1f5fe;color:#0277bd;padding:4px 8px;"
            f"border-radius:16px;margin:2px;display:inline-block;font-size:13px;'>{t}</span>"
            for t in tags
        )
        st.markdown(tag_html, unsafe_allow_html=True)


def _render_metrics(content: str, platform: str) -> None:
    """Render post metrics in columns."""
    preview = preview_post(content, platform)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Characters", preview["char_count"])
    c2.metric("Valid", "✅" if preview["is_valid"] else "❌")
    c3.metric("Hashtags", preview["hashtag_count"])
    c4.metric("Reach Score", f"{preview['estimated_reach_score']}/100")


# ---------------------------------------------------------------------------
# Main content
# ---------------------------------------------------------------------------

st.title("✍️ Social Media Writer")

tab_twitter, tab_linkedin, tab_instagram = st.tabs(["🐦 Twitter/X", "💼 LinkedIn", "📸 Instagram"])

platform_tabs = {
    "twitter": tab_twitter,
    "linkedin": tab_linkedin,
    "instagram": tab_instagram,
}

card_renderers = {
    "twitter": _render_twitter_card,
    "linkedin": _render_linkedin_card,
    "instagram": _render_instagram_card,
}

for platform, tab in platform_tabs.items():
    config = _get_platform_config(platform)

    with tab:
        st.header(f"{config['name']} Posts")

        # Best posting times
        if show_schedule:
            times = suggest_schedule(platform)
            cols = st.columns(len(times))
            for i, t in enumerate(times):
                cols[i].info(f"🕐 {t}")

        if not topic:
            st.info("👈 Enter a topic in the sidebar to get started.")
            continue

        # Hashtag-only mode
        if generate_tags_only:
            if st.button(f"Generate {config['name']} Hashtags", key=f"tags_{platform}"):
                with st.spinner(f"Generating hashtags for {config['name']}..."):
                    tags = generate_hashtags(topic, platform)
                st.subheader("Suggested Hashtags")
                st.code(tags, language=None)
            continue

        # A/B Test mode
        if ab_test_mode:
            if st.button(f"Generate {config['name']} A/B Variants", key=f"ab_{platform}"):
                with st.spinner(f"Generating A/B variants for {config['name']}..."):
                    ab_result = generate_ab_variants(topic, platform, tone, num_variants)

                formatted = format_for_platform(ab_result, platform)
                st.subheader("A/B Test Variants")

                # Split variants for side-by-side display
                import re
                variant_parts = re.split(r"(?=Variant [A-Z]:)", formatted)
                variant_parts = [v.strip() for v in variant_parts if v.strip()]

                if len(variant_parts) >= 2:
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.markdown("**Variant A**")
                        card_renderers[platform](variant_parts[0])
                        _render_metrics(variant_parts[0], platform)
                        st.code(variant_parts[0], language=None)
                    with col_b:
                        st.markdown("**Variant B**")
                        card_renderers[platform](variant_parts[1])
                        _render_metrics(variant_parts[1], platform)
                        st.code(variant_parts[1], language=None)
                    for extra in variant_parts[2:]:
                        st.markdown("---")
                        card_renderers[platform](extra)
                        _render_metrics(extra, platform)
                        st.code(extra, language=None)
                else:
                    card_renderers[platform](formatted)
                    _render_metrics(formatted, platform)
                    st.code(formatted, language=None)
            continue

        # Standard generation
        if st.button(f"Generate {config['name']} Posts", key=f"gen_{platform}"):
            with st.spinner(f"Generating {config['name']} posts..."):
                result = generate_posts(platform, topic, tone, num_variants)

            formatted = format_for_platform(result, platform)

            st.subheader("Generated Posts")
            card_renderers[platform](formatted)
            _render_metrics(formatted, platform)

            st.subheader("📋 Copy Post")
            st.code(formatted, language=None)
