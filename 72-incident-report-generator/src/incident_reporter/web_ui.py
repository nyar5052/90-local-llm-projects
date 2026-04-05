"""Streamlit Web UI for Incident Report Generator."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))

import streamlit as st

from src.incident_reporter.core import (
    generate_report,
    generate_timeline,
    build_timeline,
    calculate_impact,
    generate_lessons_learned,
    get_template,
    Priority,
    INCIDENT_TYPES,
)
from src.incident_reporter.config import load_config

st.set_page_config(
    page_title="📋 Incident Report Generator",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded",
)

config = load_config()


def main():
    st.title("📋 Incident Report Generator")
    st.caption("Professional Incident Documentation, Timeline Building & Impact Analysis")

    with st.sidebar:
        st.header("⚙️ Settings")
        incident_type = st.selectbox("Incident Type", list(INCIDENT_TYPES.keys()), index=0)
        priority = st.selectbox("Priority Level", ["P1", "P2", "P3", "P4"], index=1)
        report_title = st.text_input("Report Title (optional)")
        st.divider()
        template = get_template(Priority(priority))
        st.markdown(f"**{template['label']}**")
        st.markdown(f"⏱️ Response: {template['response_time']}")
        st.markdown(f"📢 Updates: {template['update_frequency']}")
        st.markdown(f"📞 Escalation: {template['escalation']}")

    tab_form, tab_timeline, tab_report, tab_impact = st.tabs(
        ["📝 Incident Form", "⏱️ Timeline", "📄 Generated Report", "📊 Impact Assessment"]
    )

    with tab_form:
        st.subheader("Enter Incident Data")
        log_data = st.text_area(
            "Paste raw logs or incident description:",
            height=250,
            placeholder=(
                "2024-01-15 10:23:45 ALERT: Unauthorized SSH login from 192.168.1.100\n"
                "2024-01-15 10:24:01 WARN: Multiple failed auth attempts detected\n"
                "2024-01-15 10:25:30 CRITICAL: Root access gained from external IP"
            ),
        )
        uploaded = st.file_uploader("Or upload a log file", type=["txt", "log", "json", "csv"])
        if uploaded:
            log_data = uploaded.read().decode("utf-8", errors="replace")
            st.success(f"Loaded {uploaded.name}")

        col1, col2, col3 = st.columns(3)
        with col1:
            affected_users = st.number_input("Affected Users", min_value=0, value=0)
        with col2:
            downtime_min = st.number_input("Downtime (minutes)", min_value=0, value=0)
        with col3:
            st.markdown("&nbsp;")

        col_a, col_b, col_c = st.columns(3)
        with col_a:
            gen_report_btn = st.button("📄 Generate Report", type="primary", use_container_width=True)
        with col_b:
            gen_timeline_btn = st.button("⏱️ Build Timeline", use_container_width=True)
        with col_c:
            gen_lessons_btn = st.button("📚 Lessons Learned", use_container_width=True)

        if gen_report_btn and log_data.strip():
            with st.spinner("Generating incident report..."):
                result = generate_report(log_data, incident_type, report_title, Priority(priority))
            st.session_state["report"] = result
            st.success("Report generated!")

        if gen_timeline_btn and log_data.strip():
            entries = build_timeline(log_data)
            st.session_state["timeline_entries"] = entries
            with st.spinner("Generating AI timeline..."):
                ai_timeline = generate_timeline(log_data)
            st.session_state["ai_timeline"] = ai_timeline
            st.success(f"Found {len(entries)} timeline entries")

        if gen_lessons_btn and log_data.strip():
            with st.spinner("Generating lessons learned..."):
                result = generate_lessons_learned(log_data, incident_type)
            st.session_state["lessons"] = result
            st.success("Lessons learned generated!")

        # Impact calculation
        if log_data.strip():
            assessment = calculate_impact(log_data, affected_users, downtime_min)
            st.session_state["impact"] = assessment

    with tab_timeline:
        st.subheader("⏱️ Incident Timeline")
        if "timeline_entries" in st.session_state:
            entries = st.session_state["timeline_entries"]
            if entries:
                for e in entries:
                    icon = {"critical": "🔴", "error": "🟠", "alert": "🟠",
                            "warn": "🟡", "warning": "🟡", "info": "🔵"}.get(e.severity, "⚪")
                    st.markdown(f"{icon} **{e.timestamp}** — {e.event}")
            else:
                st.info("No structured timeline entries found in logs.")
        if "ai_timeline" in st.session_state:
            st.divider()
            st.markdown("### AI-Generated Timeline")
            st.markdown(st.session_state["ai_timeline"])
        if "timeline_entries" not in st.session_state:
            st.info("Build a timeline from the Incident Form tab.")

    with tab_report:
        st.subheader("📄 Generated Incident Report")
        if "report" in st.session_state:
            st.markdown(st.session_state["report"])
            st.download_button(
                "📥 Download Report",
                st.session_state["report"],
                file_name="incident_report.md",
                mime="text/markdown",
            )
        elif "lessons" in st.session_state:
            st.markdown("### 📚 Lessons Learned")
            st.markdown(st.session_state["lessons"])
        else:
            st.info("Generate a report from the Incident Form tab.")

    with tab_impact:
        st.subheader("📊 Impact Assessment")
        if "impact" in st.session_state:
            a = st.session_state["impact"]
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Severity Score", f"{a.severity_score}/10")
            with col2:
                st.metric("Severity", a.severity_label)
            with col3:
                st.metric("Data Compromised", "⚠️ YES" if a.data_compromised else "✅ No")

            col4, col5 = st.columns(2)
            with col4:
                st.metric("Affected Users", a.affected_users)
                st.metric("Downtime", f"{a.downtime_minutes} min")
            with col5:
                st.metric("Revenue Impact", a.revenue_impact)
                if a.affected_systems:
                    st.markdown("**Affected Systems:** " + ", ".join(a.affected_systems))
        else:
            st.info("Enter incident data in the Incident Form tab.")


if __name__ == "__main__":
    main()
