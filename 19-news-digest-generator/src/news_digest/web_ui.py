"""Streamlit web interface for the News Digest Generator."""

import streamlit as st
import os

from .core import (
    read_news_files,
    categorize_articles,
    generate_digest,
    analyze_sentiment,
    save_output,
)
from .config import load_config
from .utils import setup_sys_path

setup_sys_path()
from common.llm_client import check_ollama_running


def run():
    """Launch the Streamlit web UI."""
    config = load_config()

    # Custom CSS for professional dark theme
    st.set_page_config(page_title="News Digest Generator", page_icon="🎯", layout="wide")

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
    st.title("📰 News Digest Generator")
    st.markdown("Aggregate, categorize, and summarize news articles with AI.")

    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")

        if check_ollama_running():
            st.success("✅ Ollama is running")
        else:
            st.error("❌ Ollama is not running. Start with: `ollama serve`")
            return

        num_topics = st.slider("Number of Topics", min_value=1, max_value=20, value=5)

        digest_format = st.selectbox("Digest Format", options=["daily", "weekly"], index=0)

        st.subheader("Features")
        show_sentiment = st.checkbox("Sentiment Analysis", value=True)

        st.subheader("Category Filters")
        categories = config.get("digest", {}).get("categories", [])
        selected_categories = st.multiselect("Filter categories", options=categories, default=categories)

    # Main content
    st.subheader("📁 Source Selection")

    input_method = st.radio("Input Method", ["Upload Files", "Select Folder Path"])

    articles = []

    if input_method == "Upload Files":
        uploaded_files = st.file_uploader("Upload news articles (.txt)", type=["txt"], accept_multiple_files=True)
        if uploaded_files:
            for uf in uploaded_files:
                content = uf.read().decode("utf-8").strip()
                if content:
                    articles.append({"filename": uf.name, "content": content})
    else:
        folder_path = st.text_input("Folder path containing .txt files")
        if folder_path and os.path.isdir(folder_path):
            try:
                articles = read_news_files(folder_path)
                st.success(f"Loaded {len(articles)} articles from {folder_path}")
            except (FileNotFoundError, ValueError) as e:
                st.error(str(e))

    if articles:
        # Preview
        st.subheader(f"📄 Articles ({len(articles)})")
        for a in articles:
            with st.expander(f"📰 {a['filename']} ({len(a['content']):,} chars)"):
                st.text(a["content"][:500])

        if st.button("🚀 Generate Digest", type="primary", use_container_width=True):
            with st.spinner("Categorizing articles..."):
                categorization = categorize_articles(articles, num_topics, config=config)

            with st.spinner(f"Generating {digest_format} digest..."):
                digest = generate_digest(articles, categorization, digest_format=digest_format, config=config)

            st.success("✅ Digest generated!")

            # Digest preview
            st.markdown("---")
            st.subheader("📋 News Digest")
            st.markdown(digest)

            # Categorization
            with st.expander("🏷️ Topic Categorization", expanded=False):
                st.markdown(categorization)

            # Sentiment
            if show_sentiment:
                with st.spinner("Analyzing sentiment..."):
                    sentiment_text = analyze_sentiment(articles, config=config)
                st.subheader("📊 Sentiment Analysis")
                st.markdown(sentiment_text)

            # Download
            st.download_button(
                "📥 Download Digest",
                data=f"# News Digest\n\n{digest}\n\n---\n\n## Categorization\n\n{categorization}",
                file_name=f"news_digest_{digest_format}.md",
                mime="text/markdown",
            )
    else:
        st.info("👆 Upload news articles or select a folder to get started.")


if __name__ == "__main__":
    run()
