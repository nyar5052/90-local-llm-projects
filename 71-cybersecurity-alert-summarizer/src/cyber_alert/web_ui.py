"""Streamlit Web UI for Cybersecurity Alert Summarizer."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))

import streamlit as st

from src.cyber_alert.core import (
    summarize_alert,
    prioritize_alerts,
    extract_iocs,
    extract_cves,
    calculate_threat_score,
    Severity,
)
from src.cyber_alert.config import load_config

# ---------------------------------------------------------------------------
# Page Config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="🛡️ Cybersecurity Alert Summarizer",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

config = load_config()


def main():
    st.title("🛡️ Cybersecurity Alert Summarizer")
    st.caption("AI-Powered Threat Analysis, IOC Extraction & CVE Lookup")

    # --- Sidebar ---
    with st.sidebar:
        st.header("⚙️ Settings")
        severity_filter = st.selectbox(
            "Severity Filter",
            ["all", "critical", "high", "medium", "low"],
            index=0,
        )
        analysis_mode = st.radio(
            "Analysis Mode",
            ["Summarize", "Prioritize", "Score Only"],
            index=0,
        )
        st.divider()
        st.markdown("### 📊 Quick Stats")
        if "alert_count" not in st.session_state:
            st.session_state.alert_count = 0
        st.metric("Alerts Analyzed", st.session_state.alert_count)

    # --- Main Content ---
    tab_input, tab_ioc, tab_dashboard, tab_recs = st.tabs(
        ["📥 Alert Input", "🔍 IOC Table", "📊 Severity Dashboard", "💡 Recommendations"]
    )

    with tab_input:
        st.subheader("Enter Security Alert Data")
        alert_text = st.text_area(
            "Paste alert text, CVE reports, or log entries:",
            height=250,
            placeholder=(
                "CVE-2024-3094: XZ Utils backdoor discovered...\n"
                "Source IP: 192.168.1.100\n"
                "Hash: a1b2c3d4e5f6..."
            ),
        )

        uploaded = st.file_uploader("Or upload an alert file", type=["txt", "log", "json", "csv"])
        if uploaded:
            alert_text = uploaded.read().decode("utf-8", errors="replace")
            st.success(f"Loaded {uploaded.name} ({len(alert_text)} chars)")

        col1, col2 = st.columns(2)
        with col1:
            analyze_btn = st.button("🔬 Analyze Alert", type="primary", use_container_width=True)
        with col2:
            extract_btn = st.button("🔍 Extract IOCs & CVEs", use_container_width=True)

        if analyze_btn and alert_text.strip():
            st.session_state.alert_count += 1
            with st.spinner("Analyzing alert with AI..."):
                if analysis_mode == "Summarize":
                    result = summarize_alert(alert_text, severity_filter)
                elif analysis_mode == "Prioritize":
                    result = prioritize_alerts(alert_text)
                else:
                    score = calculate_threat_score(alert_text)
                    st.session_state["threat_score"] = score
                    result = None

                if result:
                    st.session_state["analysis_result"] = result

            if result:
                st.markdown("### 📋 Analysis Results")
                st.markdown(result)
            elif "threat_score" in st.session_state:
                score = st.session_state["threat_score"]
                color_map = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "🟢", "INFO": "⚪"}
                st.markdown(f"### {color_map.get(score.label, '⚪')} Threat Score: {score.overall_score}/10.0 — {score.label}")
                st.progress(min(score.overall_score / 10.0, 1.0))

        if extract_btn and alert_text.strip():
            iocs = extract_iocs(alert_text)
            cves = extract_cves(alert_text)
            st.session_state["iocs"] = iocs
            st.session_state["cves"] = cves
            st.success(f"Found {len(iocs)} IOCs and {len(cves)} CVEs")

    with tab_ioc:
        st.subheader("🔍 Indicators of Compromise")
        if "iocs" in st.session_state and st.session_state["iocs"]:
            iocs = st.session_state["iocs"]
            ioc_data = [{"Type": i.ioc_type, "Value": i.value, "Context": i.context[:80]} for i in iocs]
            st.dataframe(ioc_data, use_container_width=True)
        else:
            st.info("Extract IOCs from the Alert Input tab first.")

        st.divider()
        st.subheader("📛 CVE Lookup Results")
        if "cves" in st.session_state and st.session_state["cves"]:
            cves = st.session_state["cves"]
            cve_data = [{
                "CVE ID": c.cve_id,
                "CVSS": c.cvss if c.found_in_db else "N/A",
                "Severity": c.severity if c.found_in_db else "unknown",
                "Description": c.description[:60] if c.found_in_db else "Not in local DB",
                "In DB": "✅" if c.found_in_db else "❌",
            } for c in cves]
            st.dataframe(cve_data, use_container_width=True)
        else:
            st.info("Extract CVEs from the Alert Input tab first.")

    with tab_dashboard:
        st.subheader("📊 Severity Dashboard")
        if "threat_score" in st.session_state:
            score = st.session_state["threat_score"]
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Overall Score", f"{score.overall_score}/10")
            with col2:
                st.metric("Severity", score.label)
            with col3:
                st.metric("Confidence", f"{score.confidence * 100:.0f}%")

            st.divider()
            st.markdown("#### Factor Breakdown")
            for k, v in score.factors.items():
                if k != "weights":
                    st.progress(min(v / 10.0, 1.0), text=f"{k}: {v:.2f}/10.0")
        else:
            st.info("Run a 'Score Only' analysis from the Alert Input tab.")

    with tab_recs:
        st.subheader("💡 Recommendations")
        if "analysis_result" in st.session_state:
            st.markdown(st.session_state["analysis_result"])
        else:
            st.info("Run an analysis from the Alert Input tab to see recommendations.")


if __name__ == "__main__":
    main()
