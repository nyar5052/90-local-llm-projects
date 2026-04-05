#!/usr/bin/env python3
"""Streamlit Web UI for Blog Post Generator."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
from datetime import datetime, timezone

from blog_gen.core import (
    TONES,
    generate_blog_post,
    generate_outline,
    generate_multiple_drafts,
    score_seo,
    analyze_tone,
    export_markdown,
    parse_blog_post,
    load_config,
    setup_logging,
)
from common.llm_client import check_ollama_running

setup_logging()

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------

# Custom CSS for professional dark theme
st.set_page_config(page_title="Blog Post Generator", page_icon="🎯", layout="wide")

st.markdown("""
<style>
    .main { background-color: #0e1117; }
    .stApp { background: linear-gradient(180deg, #0e1117 0%, #1a1a2e 100%); }
    h1 { background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 2.5rem !important; }
    h2 { color: #667eea !important; }
    h3 { color: #a78bfa !important; }
    .stButton>button { background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); color: white; border: none; border-radius: 8px; padding: 0.5rem 2rem; font-weight: 600; transition: transform 0.2s; }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4); }
    .stTextInput>div>div>input, .stTextArea>div>div>textarea { background-color: #1a1a2e; border: 1px solid #333; color: #e0e0e0; border-radius: 8px; }
    .stSelectbox>div>div { background-color: #1a1a2e; border: 1px solid #333; }
    .stMetric { background: linear-gradient(135deg, #1a1a2e, #16213e); padding: 1rem; border-radius: 10px; border: 1px solid #333; }
    .css-1d391kg { background-color: #1a1a2e; }
    div[data-testid="stSidebar"] { background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%); }
    .stSuccess { background-color: rgba(102, 126, 234, 0.1); border: 1px solid #667eea; }
    footer { visibility: hidden; }
    .block-container { padding-top: 2rem; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Session state defaults
# ---------------------------------------------------------------------------

if "history" not in st.session_state:
    st.session_state.history = []
if "current_post" not in st.session_state:
    st.session_state.current_post = None
if "current_outline" not in st.session_state:
    st.session_state.current_outline = None
if "drafts" not in st.session_state:
    st.session_state.drafts = []

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

with st.sidebar:
    st.header("⚙️ Settings")
    config = load_config()

    ollama_status = check_ollama_running()
    if ollama_status:
        st.success("✅ Ollama is running")
    else:
        st.error("❌ Ollama is not running. Start it with `ollama serve`")

    st.subheader("Model Configuration")
    llm_cfg = config.get("llm", {})
    model_name = st.text_input("Model", value=llm_cfg.get("model", "llama3"))
    temperature = st.slider("Temperature", 0.0, 1.0, value=llm_cfg.get("temperature", 0.7), step=0.05)

    st.divider()

    st.subheader("📜 History")
    if st.session_state.history:
        for idx, entry in enumerate(reversed(st.session_state.history)):
            with st.expander(f"{entry['topic'][:40]}… ({entry['time']})"):
                st.write(f"**Tone:** {entry['tone']}  |  **Words:** {entry['word_count']}")
                st.write(f"**SEO Score:** {entry['seo_score']}")
                if st.button("Load", key=f"load_{idx}"):
                    st.session_state.current_post = entry["content"]
    else:
        st.caption("No posts generated yet.")

# ---------------------------------------------------------------------------
# Main area
# ---------------------------------------------------------------------------

st.title("📝 Blog Post Generator")
st.markdown("Generate SEO-friendly blog posts powered by a local LLM.")

col_input, col_options = st.columns([2, 1])

with col_input:
    topic = st.text_input("📌 Topic", placeholder="e.g., AI in Healthcare")
    keywords_raw = st.text_input("🔑 Keywords (comma-separated)", placeholder="e.g., ML, diagnosis, patient care")

with col_options:
    tone = st.selectbox("🎨 Tone", options=TONES, index=0)
    length = st.slider("📏 Length (words)", min_value=300, max_value=2000, value=800, step=50)
    num_drafts = st.slider("📄 Number of Drafts", min_value=1, max_value=5, value=1)

keywords_list = [k.strip() for k in keywords_raw.split(",") if k.strip()] if keywords_raw else []

# ---------------------------------------------------------------------------
# Action buttons
# ---------------------------------------------------------------------------

btn_col1, btn_col2 = st.columns(2)

with btn_col1:
    generate_outline_btn = st.button("📋 Generate Outline", use_container_width=True)

with btn_col2:
    generate_post_btn = st.button("🚀 Generate Post", type="primary", use_container_width=True)

# ---------------------------------------------------------------------------
# Outline generation
# ---------------------------------------------------------------------------

if generate_outline_btn:
    if not topic:
        st.warning("Please enter a topic first.")
    elif not ollama_status:
        st.error("Ollama is not running.")
    else:
        with st.spinner("Generating outline..."):
            outline = generate_outline(topic, keywords_list, tone)
            st.session_state.current_outline = outline

if st.session_state.current_outline:
    st.subheader("📋 Outline Preview")
    st.markdown(st.session_state.current_outline)
    st.divider()

# ---------------------------------------------------------------------------
# Post generation
# ---------------------------------------------------------------------------

if generate_post_btn:
    if not topic:
        st.warning("Please enter a topic first.")
    elif not ollama_status:
        st.error("Ollama is not running.")
    else:
        with st.spinner(f"Generating {'post' if num_drafts == 1 else f'{num_drafts} drafts'}..."):
            if num_drafts > 1:
                drafts_list = generate_multiple_drafts(topic, keywords_list, tone, length, num_drafts)
                st.session_state.drafts = drafts_list
                st.session_state.current_post = drafts_list[0]
            else:
                post = generate_blog_post(topic, keywords_list, tone, length)
                st.session_state.current_post = post
                st.session_state.drafts = [post]

        # Save to history
        content = st.session_state.current_post
        seo = score_seo(content, keywords_list)
        st.session_state.history.append({
            "topic": topic,
            "tone": tone,
            "word_count": len(content.split()),
            "seo_score": seo["total"],
            "content": content,
            "time": datetime.now(timezone.utc).strftime("%H:%M:%S"),
        })

# ---------------------------------------------------------------------------
# Display generated content
# ---------------------------------------------------------------------------

if st.session_state.current_post:
    content = st.session_state.current_post

    # Draft tabs
    if len(st.session_state.drafts) > 1:
        tabs = st.tabs([f"Draft {i+1}" for i in range(len(st.session_state.drafts))])
        for idx, tab in enumerate(tabs):
            with tab:
                draft = st.session_state.drafts[idx]
                _show_post(draft, keywords_list) if False else None  # noqa – handled below
                st.markdown(draft)
                draft_seo = score_seo(draft, keywords_list)
                st.metric("SEO Score", f"{draft_seo['total']:.0f}/100")
                st.metric("Word Count", len(draft.split()))
    else:
        st.subheader("📄 Generated Blog Post")
        st.markdown(content)

    st.divider()

    # Metrics row
    seo = score_seo(content, keywords_list)
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("🎯 SEO Score", f"{seo['total']:.0f}/100")
    m2.metric("📏 Word Count", len(content.split()))
    m3.metric("📑 Headings", f"{seo['heading_structure']:.0f}/25")
    m4.metric("🔑 Keywords", f"{seo['keyword_density']:.0f}/30")

    # Detailed SEO breakdown
    with st.expander("📊 Detailed SEO Analysis"):
        seo_col1, seo_col2 = st.columns(2)
        with seo_col1:
            st.progress(min(seo["keyword_density"] / 30, 1.0), text=f"Keyword Density: {seo['keyword_density']:.1f}/30")
            st.progress(min(seo["heading_structure"] / 25, 1.0), text=f"Heading Structure: {seo['heading_structure']:.1f}/25")
        with seo_col2:
            st.progress(min(seo["meta_description"] / 20, 1.0), text=f"Meta Description: {seo['meta_description']:.1f}/20")
            st.progress(min(seo["content_length"] / 25, 1.0), text=f"Content Length: {seo['content_length']:.1f}/25")

    # Tone analysis
    with st.expander("🎨 Tone Analysis"):
        tone_result = analyze_tone(content)
        for t in TONES:
            conf = tone_result.get(t, 0)
            st.progress(min(conf, 1.0), text=f"{t.capitalize()}: {conf:.0%}")
        st.info(f"**Dominant tone:** {tone_result.get('dominant_tone', 'N/A').capitalize()}")

    # Export / Download
    st.divider()
    st.subheader("💾 Export")
    dl_col1, dl_col2 = st.columns(2)
    with dl_col1:
        st.download_button(
            label="⬇️ Download Markdown",
            data=content,
            file_name="blog_post.md",
            mime="text/markdown",
            use_container_width=True,
        )
    with dl_col2:
        blog_post = parse_blog_post(content, keywords_list, tone)
        frontmatter = (
            f"---\n"
            f"title: \"{blog_post.title}\"\n"
            f"date: \"{datetime.now(timezone.utc).strftime('%Y-%m-%d')}\"\n"
            f"keywords: {keywords_list}\n"
            f"seo_score: {seo['total']}\n"
            f"---\n\n"
        )
        st.download_button(
            label="⬇️ Download with Frontmatter",
            data=frontmatter + content,
            file_name="blog_post_frontmatter.md",
            mime="text/markdown",
            use_container_width=True,
        )
