"""Streamlit Web UI for Sentiment Analysis Dashboard."""

import sys
import os
import json
import logging

import streamlit as st
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.sentiment_analyzer.core import (
    load_config,
    analyze_sentiment,
    compute_sentiment_distribution,
    compute_trend_over_time,
    extract_word_cloud_data,
    export_report,
)

logger = logging.getLogger(__name__)

# Custom CSS for professional dark theme
st.set_page_config(page_title="Sentiment Analysis Dashboard", page_icon="🎯", layout="wide")

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


def render_header():
    """Render the application header."""
    st.title("💬 Sentiment Analysis Dashboard")
    st.markdown("*Analyze sentiment of text data — powered by local LLM*")
    st.divider()


def render_upload_section() -> list[str] | None:
    """Render file upload section and return texts."""
    st.sidebar.header("📁 Upload Text Data")
    uploaded_files = st.sidebar.file_uploader("Choose text files", type=["txt", "csv"],
                                               accept_multiple_files=True)
    texts = []
    if uploaded_files:
        for uf in uploaded_files:
            content = uf.read().decode("utf-8")
            lines = [line.strip() for line in content.split("\n") if line.strip()]
            texts.extend(lines)
            st.sidebar.success(f"✅ {uf.name}: {len(lines)} entries")

    if texts:
        st.sidebar.info(f"📊 Total: {len(texts)} text entries")
        return texts
    return None


def render_sentiment_gauge(distribution: dict):
    """Render sentiment gauge metrics."""
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📝 Total", distribution["total"])
    col2.metric("😊 Positive", f"{distribution['positive']} ({distribution['positive_pct']}%)")
    col3.metric("😞 Negative", f"{distribution['negative']} ({distribution['negative_pct']}%)")
    col4.metric("😐 Neutral", f"{distribution['neutral']} ({distribution['neutral_pct']}%)")

    st.progress(distribution["avg_confidence"], text=f"Average Confidence: {distribution['avg_confidence']:.0%}")


def render_results_table(results: list[dict], texts: list[str]):
    """Render results in a data table."""
    with st.expander("📋 Detailed Results", expanded=True):
        data = []
        for text, result in zip(texts, results):
            emoji = {"positive": "😊", "negative": "😞", "neutral": "😐"}.get(
                result.get("sentiment", "neutral").lower(), "❓")
            data.append({
                "Text": text[:100] + ("..." if len(text) > 100 else ""),
                "Sentiment": f"{emoji} {result.get('sentiment', 'neutral').title()}",
                "Confidence": f"{result.get('confidence', 0.5):.0%}",
                "Summary": result.get("summary", "N/A")[:80],
            })
        st.dataframe(pd.DataFrame(data), use_container_width=True)


def render_trend_chart(results: list[dict]):
    """Render sentiment trend chart."""
    with st.expander("📈 Sentiment Trend", expanded=False):
        window = st.slider("Window size", 2, max(5, len(results) // 2), 5)
        trend = compute_trend_over_time(results, window)
        if trend:
            trend_df = pd.DataFrame(trend)
            st.line_chart(trend_df.set_index("window_start")[["positive_pct", "negative_pct", "neutral_pct"]])


def render_word_cloud(results: list[dict]):
    """Render word cloud data as a bar chart."""
    with st.expander("☁️ Key Phrases", expanded=False):
        word_data = extract_word_cloud_data(results)
        if word_data:
            df = pd.DataFrame(list(word_data.items()), columns=["Word", "Frequency"])
            df = df.sort_values("Frequency", ascending=False).head(20)
            st.bar_chart(df.set_index("Word"))
        else:
            st.info("No key phrases extracted yet.")


def render_export_section(results: list[dict], texts: list[str]):
    """Render export section."""
    st.subheader("📥 Export Report")
    if st.button("Generate Report"):
        output_path = "sentiment_report.json"
        export_report(results, texts, output_path)
        with open(output_path, "r") as f:
            st.download_button("Download Report", f.read(),
                               file_name="sentiment_report.json", mime="application/json")


def main():
    """Main Streamlit application."""
    load_config()
    render_header()

    texts = render_upload_section()

    if texts is not None:
        if "sentiment_results" not in st.session_state or st.sidebar.button("🔄 Re-analyze"):
            with st.spinner(f"Analyzing {len(texts)} entries..."):
                results = []
                progress = st.progress(0)
                for i, text in enumerate(texts):
                    results.append(analyze_sentiment(text))
                    progress.progress((i + 1) / len(texts))
                st.session_state["sentiment_results"] = results
                st.session_state["sentiment_texts"] = texts

        results = st.session_state.get("sentiment_results", [])
        texts = st.session_state.get("sentiment_texts", texts)

        if results:
            distribution = compute_sentiment_distribution(results)
            render_sentiment_gauge(distribution)
            st.divider()
            render_results_table(results, texts)
            render_trend_chart(results)
            render_word_cloud(results)
            render_export_section(results, texts)
    else:
        st.info("👈 Upload text files to analyze sentiment!")
        st.markdown("""
        ### Features
        - 📁 **Batch file processing** — upload multiple text files at once
        - 📊 **Sentiment gauge** — real-time distribution overview
        - 📈 **Trend over time** — track sentiment shifts across entries
        - ☁️ **Word cloud data** — key phrases visualization
        - 📥 **Export reports** — download comprehensive JSON reports
        """)


if __name__ == "__main__":
    main()
