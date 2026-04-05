#!/usr/bin/env python3
"""Streamlit Web UI for the Trend Analysis Tool.

Launch with:
    streamlit run src/trend_analyzer/web_ui.py
"""

import json
import os
import sys
from pathlib import Path

import streamlit as st


# Custom CSS for professional dark theme
st.set_page_config(page_title="Trend Analysis Tool", page_icon="🎯", layout="wide")

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

# Ensure project root is on the path so common.llm_client can be imported
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))

from src.trend_analyzer.core import (
    analyze_sentiment_trends,
    detect_emerging_topics,
    extract_topics,
    generate_alert_report,
    load_config,
    load_text_files,
    setup_logging,
    track_topic_evolution,
)

try:
    from common.llm_client import check_ollama_running
except ImportError:
    def check_ollama_running() -> bool:
        return False


# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

st.sidebar.title("📈 Trend Analyzer")
config_path = st.sidebar.text_input("Config file", value="config.yaml")
config = load_config(config_path)
setup_logging(config)

source_folder = st.sidebar.text_input("📁 Source folder", placeholder="/path/to/articles")
timeframe = st.sidebar.selectbox(
    "⏱️ Timeframe",
    ["recent", "last week", "last month", "last quarter", "last year", "custom"],
)
run_sentiment = st.sidebar.checkbox("💭 Include sentiment analysis", value=True)
emerging_threshold = st.sidebar.slider("🚨 Emerging threshold", 0.0, 1.0, 0.7, 0.05)
run_analysis = st.sidebar.button("▶️ Run Analysis", type="primary")

# Ollama status
ollama_ok = check_ollama_running()
st.sidebar.markdown("---")
if ollama_ok:
    st.sidebar.success("✅ Ollama is running")
else:
    st.sidebar.error("❌ Ollama is not running — start with `ollama serve`")


# ---------------------------------------------------------------------------
# Tabs
# ---------------------------------------------------------------------------

tab_source, tab_topics, tab_timeline, tab_emerging = st.tabs(
    ["📂 Source Input", "🔍 Topic Cards", "📊 Timeline Chart", "🚨 Emerging Alerts"]
)

# ---------------------------------------------------------------------------
# Session state defaults
# ---------------------------------------------------------------------------
for key in ("documents", "topics", "sentiments", "emerging_list"):
    if key not in st.session_state:
        st.session_state[key] = None


# ---------------------------------------------------------------------------
# Tab 1 — Source Input
# ---------------------------------------------------------------------------

with tab_source:
    st.header("📂 Source Documents")
    if source_folder:
        folder = Path(source_folder)
        if folder.exists() and folder.is_dir():
            extensions = set(config.get("file_extensions", [".txt", ".md"]))
            files = sorted(
                f for f in folder.iterdir()
                if f.is_file() and f.suffix.lower() in extensions
            )
            st.metric("Documents found", len(files))
            if files:
                st.dataframe(
                    [
                        {"File": f.name, "Size (bytes)": f.stat().st_size}
                        for f in files
                    ],
                    use_container_width=True,
                )
            else:
                st.warning("No supported text files found in this directory.")
        else:
            st.error(f"Directory `{source_folder}` does not exist.")
    else:
        st.info("Enter a source folder in the sidebar to get started.")


# ---------------------------------------------------------------------------
# Run analysis
# ---------------------------------------------------------------------------

if run_analysis and source_folder:
    if not ollama_ok:
        st.error("Ollama must be running to perform analysis.")
    else:
        try:
            with st.spinner("Loading documents..."):
                docs = load_text_files(source_folder, config)
            st.session_state["documents"] = docs

            with st.spinner("Extracting topics..."):
                topics = extract_topics(docs, config)
            st.session_state["topics"] = topics

            if run_sentiment:
                with st.spinner("Analyzing sentiment..."):
                    sentiments = analyze_sentiment_trends(docs, config)
                st.session_state["sentiments"] = sentiments
            else:
                st.session_state["sentiments"] = None

            with st.spinner("Detecting emerging topics..."):
                emg = detect_emerging_topics(
                    topics, threshold=emerging_threshold, config=config
                )
            st.session_state["emerging_list"] = emg

            st.success(f"✅ Analysis complete — {len(docs)} documents processed.")
        except (FileNotFoundError, ValueError) as exc:
            st.error(str(exc))


# ---------------------------------------------------------------------------
# Tab 2 — Topic Cards
# ---------------------------------------------------------------------------

with tab_topics:
    st.header("🔍 Topics")
    topics_data = st.session_state.get("topics")
    if topics_data and topics_data.get("topics"):
        cols = st.columns(3)
        trend_colors = {
            "emerging": "🟢",
            "growing": "🔵",
            "stable": "🟡",
            "declining": "🔴",
        }
        for idx, topic in enumerate(topics_data["topics"]):
            with cols[idx % 3]:
                badge = trend_colors.get(topic.get("trend", "stable"), "⚪")
                freq = topic.get("frequency", "low").title()
                st.markdown(
                    f"### {badge} {topic.get('name', 'N/A')}\n"
                    f"**Frequency:** {freq}  \n"
                    f"**Trend:** {topic.get('trend', 'stable').title()}  \n"
                    f"{topic.get('description', '')}"
                )
                related = topic.get("related_docs", [])
                if related:
                    st.caption("Related: " + ", ".join(related))
                st.divider()

        overall = topics_data.get("overall_theme", "")
        if overall:
            st.info(f"**Overall Theme:** {overall}")
    else:
        st.info("Run an analysis to see topic cards.")


# ---------------------------------------------------------------------------
# Tab 3 — Timeline Chart
# ---------------------------------------------------------------------------

with tab_timeline:
    st.header("📊 Timeline")
    topics_data = st.session_state.get("topics")
    sentiments_data = st.session_state.get("sentiments")

    if topics_data and topics_data.get("topics"):
        import pandas as pd

        freq_map = {"high": 3, "medium": 2, "low": 1}
        chart_data = pd.DataFrame(
            [
                {
                    "Topic": t.get("name", "?"),
                    "Frequency Score": freq_map.get(t.get("frequency", "low"), 1),
                }
                for t in topics_data["topics"]
            ]
        )
        st.subheader("Topic Frequency")
        st.bar_chart(chart_data.set_index("Topic"))

    if sentiments_data:
        st.subheader("Sentiment Distribution")
        dist = sentiments_data.get("sentiment_distribution", {})
        if dist:
            import pandas as pd

            sent_df = pd.DataFrame(
                [{"Sentiment": k.title(), "Count": v} for k, v in dist.items()]
            )
            st.bar_chart(sent_df.set_index("Sentiment"))

        shifts = sentiments_data.get("sentiment_shifts", [])
        if shifts:
            st.subheader("Sentiment Shifts")
            for shift in shifts:
                st.markdown(f"- {shift}")
    elif not topics_data:
        st.info("Run an analysis to see timeline charts.")


# ---------------------------------------------------------------------------
# Tab 4 — Emerging Alerts
# ---------------------------------------------------------------------------

with tab_emerging:
    st.header("🚨 Emerging Topics")
    emg_list = st.session_state.get("emerging_list")
    if emg_list:
        for topic in emg_list:
            with st.container():
                st.error(
                    f"**{topic['name']}** — Score: {topic['score']}  |  "
                    f"Trend: {topic['trend']}  |  Frequency: {topic.get('frequency', 'N/A')}"
                )
                st.markdown(topic.get("description", ""))
                st.divider()

        alert_md = generate_alert_report(emg_list)
        with st.expander("📄 Full Alert Report (Markdown)"):
            st.markdown(alert_md)
    else:
        st.info("Run an analysis to detect emerging topics.")
