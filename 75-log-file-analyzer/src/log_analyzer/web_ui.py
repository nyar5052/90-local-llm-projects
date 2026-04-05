"""Streamlit Web UI for Log File Analyzer."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))

import streamlit as st


# Custom CSS for professional dark theme
st.set_page_config(page_title="Log File Analyzer", page_icon="🎯", layout="wide")

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

from src.log_analyzer.core import (
    read_log_file,
    analyze_logs,
    cluster_errors,
    match_patterns,
    detect_anomalies,
    cluster_errors_local,
    build_timeline,
    evaluate_alert_rules,
    LogLevel,
    FOCUS_AREAS,
)
from src.log_analyzer.config import load_config

LEVEL_ICONS = {
    LogLevel.CRITICAL: "🔴",
    LogLevel.ERROR: "🟠",
    LogLevel.WARNING: "🟡",
    LogLevel.INFO: "🔵",
    LogLevel.DEBUG: "⚪",
}

config = load_config()


def main():
    st.title("📊 Log File Analyzer")
    st.caption("Pattern Detection, Anomaly Analysis, Error Clustering & Timeline Visualization")

    with st.sidebar:
        st.header("⚙️ Settings")
        focus = st.selectbox("Analysis Focus", list(FOCUS_AREAS.keys()), index=0)
        last_n = st.number_input("Last N Lines (0=all)", min_value=0, value=0)
        system_context = st.text_input("System Context (optional)")
        st.divider()
        st.markdown("### 📊 Log Stats")
        if "line_count" in st.session_state:
            st.metric("Lines", st.session_state["line_count"])
        if "pattern_count" in st.session_state:
            st.metric("Pattern Matches", st.session_state["pattern_count"])

    tab_upload, tab_errors, tab_patterns, tab_timeline = st.tabs(
        ["📤 Log Upload", "❌ Error Table", "🔍 Pattern Matches", "📈 Timeline Chart"]
    )

    with tab_upload:
        st.subheader("Upload or Paste Log Data")
        log_content = st.text_area(
            "Paste log content:",
            height=250,
            placeholder=(
                "2024-01-15 10:00:01 ERROR: Database connection timeout after 30s\n"
                "2024-01-15 10:00:05 ERROR: Database connection timeout after 30s\n"
                "2024-01-15 10:00:10 WARN: High memory usage: 92%"
            ),
        )
        uploaded = st.file_uploader("Or upload a log file", type=["txt", "log", "json", "csv"])
        if uploaded:
            log_content = uploaded.read().decode("utf-8", errors="replace")
            st.success(f"Loaded {uploaded.name} ({len(log_content)} chars)")

        if log_content.strip():
            ln = last_n if last_n > 0 else None
            if ln:
                lines = log_content.splitlines()
                log_content = "\n".join(lines[-ln:])

            st.session_state["log_content"] = log_content
            st.session_state["line_count"] = log_content.count("\n") + 1

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            analyze_btn = st.button("🔬 AI Analyze", type="primary", use_container_width=True)
        with col2:
            pattern_btn = st.button("🔍 Match Patterns", use_container_width=True)
        with col3:
            anomaly_btn = st.button("⚡ Detect Anomalies", use_container_width=True)
        with col4:
            alert_btn = st.button("🚨 Check Alerts", use_container_width=True)

        if analyze_btn and log_content.strip():
            with st.spinner("Analyzing logs with AI..."):
                result = analyze_logs(log_content, focus, system_context or None)
            st.session_state["analysis"] = result
            st.markdown("### 📋 AI Analysis")
            st.markdown(result)

        if pattern_btn and log_content.strip():
            matches = match_patterns(log_content)
            st.session_state["patterns"] = matches
            st.session_state["pattern_count"] = len(matches)
            st.success(f"Found {len(matches)} pattern matches")

        if anomaly_btn and log_content.strip():
            anoms = detect_anomalies(log_content)
            st.session_state["anomalies"] = anoms
            if anoms:
                for a in anoms:
                    icon = LEVEL_ICONS.get(a.severity, "⚪")
                    st.warning(f"{icon} **{a.anomaly_type}:** {a.description} (score: {a.score:.2f})")
            else:
                st.success("No anomalies detected!")

        if alert_btn and log_content.strip():
            rules = evaluate_alert_rules(log_content)
            for r in rules:
                if r.triggered:
                    st.error(f"🚨 **{r.name}:** {r.condition} (current: {r.current_value})")
                else:
                    st.success(f"✅ **{r.name}:** OK (current: {r.current_value})")

    with tab_errors:
        st.subheader("❌ Error Table & Clusters")
        if "log_content" in st.session_state:
            clusters = cluster_errors_local(st.session_state["log_content"])
            if clusters:
                data = [{
                    "Cluster": c.cluster_id,
                    "Count": c.count,
                    "Severity": f"{LEVEL_ICONS.get(c.severity, '⚪')} {c.severity.value}",
                    "Pattern": c.pattern[:60],
                    "First Seen": c.first_seen,
                    "Last Seen": c.last_seen,
                } for c in clusters]
                st.dataframe(data, use_container_width=True)

                # Show examples
                selected = st.selectbox("View cluster examples", [f"Cluster {c.cluster_id} ({c.count} errors)" for c in clusters])
                if selected:
                    idx = int(selected.split()[1])
                    cluster = next((c for c in clusters if c.cluster_id == idx), None)
                    if cluster:
                        for ex in cluster.example_lines:
                            st.code(ex, language="log")
            else:
                st.info("No error clusters found.")
        else:
            st.info("Upload logs from the Log Upload tab.")

    with tab_patterns:
        st.subheader("🔍 Pattern Library Matches")
        if "patterns" in st.session_state:
            matches = st.session_state["patterns"]
            if matches:
                data = [{
                    "Line": m.line_number,
                    "Pattern": m.pattern_name,
                    "Category": m.category,
                    "Severity": f"{LEVEL_ICONS.get(m.severity, '⚪')} {m.severity.value}",
                    "Description": m.description,
                } for m in matches]
                st.dataframe(data, use_container_width=True)

                # Category breakdown
                cats = {}
                for m in matches:
                    cats[m.category] = cats.get(m.category, 0) + 1
                st.bar_chart(cats)
            else:
                st.info("No patterns matched.")
        else:
            st.info("Run pattern matching from the Log Upload tab.")

    with tab_timeline:
        st.subheader("📈 Event Timeline")
        if "log_content" in st.session_state:
            events = build_timeline(st.session_state["log_content"])
            if events:
                level_icons = {"CRITICAL": "🔴", "FATAL": "🔴", "ERROR": "🟠", "ERR": "🟠",
                               "WARN": "🟡", "WARNING": "🟡", "INFO": "🔵", "DEBUG": "⚪"}
                for e in events[:200]:
                    icon = level_icons.get(e.level, "⚪")
                    st.markdown(f"{icon} **{e.timestamp}** `{e.level}` — {e.message[:100]}")
            else:
                st.info("No timestamped events found.")
        else:
            st.info("Upload logs from the Log Upload tab.")


if __name__ == "__main__":
    main()
