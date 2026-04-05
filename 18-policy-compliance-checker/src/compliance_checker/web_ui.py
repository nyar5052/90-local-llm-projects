"""Streamlit web interface for the Policy Compliance Checker."""

import streamlit as st
import json

from .core import (
    read_file,
    check_compliance,
    filter_violations,
    get_score_color,
    get_score_label,
    SEVERITY_COLORS,
)
from .config import load_config
from .utils import setup_sys_path

setup_sys_path()
from common.llm_client import check_ollama_running


def run():
    """Launch the Streamlit web UI."""
    config = load_config()

    st.set_page_config(page_title="✅ Compliance Checker", page_icon="✅", layout="wide")
    st.title("✅ Policy Compliance Checker")
    st.markdown("Check documents against policy rules with AI-powered analysis.")

    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")

        if check_ollama_running():
            st.success("✅ Ollama is running")
        else:
            st.error("❌ Ollama is not running. Start with: `ollama serve`")
            return

        severity_filter = st.selectbox(
            "Severity Filter",
            options=["all", "high", "medium", "low"],
            index=0,
        )

        export_format = st.selectbox(
            "Export Format",
            options=["json", "markdown", "csv"],
            index=0,
        )

    # Main content
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📄 Document")
        doc_file = st.file_uploader("Upload document", type=["txt", "md", "pdf"])
        doc_text_input = st.text_area("Or paste document text", height=200)

    with col2:
        st.subheader("📋 Policy")
        policy_file = st.file_uploader("Upload policy file", type=["txt", "md"])
        policy_text_input = st.text_area("Or paste policy rules", height=200)

    # Get text content
    doc_text = ""
    if doc_file:
        doc_text = doc_file.read().decode("utf-8")
    elif doc_text_input:
        doc_text = doc_text_input

    policy_text = ""
    if policy_file:
        policy_text = policy_file.read().decode("utf-8")
    elif policy_text_input:
        policy_text = policy_text_input

    if doc_text and policy_text:
        if st.button("🔍 Check Compliance", type="primary", use_container_width=True):
            with st.spinner("Analyzing compliance..."):
                report = check_compliance(doc_text, policy_text, config=config)

            # Score meter
            score = report.get("compliance_score", 0)
            label = get_score_label(score, config)

            st.markdown("---")
            col_s1, col_s2, col_s3 = st.columns(3)
            col_s1.metric("Compliance Score", f"{score}%")
            col_s2.metric("Status", label)
            col_s3.metric("Violations", len(report.get("violations", [])))

            st.progress(score / 100)

            # Summary
            st.subheader("📊 Summary")
            st.write(report.get("summary", "N/A"))

            # Violations
            violations = filter_violations(report.get("violations", []), severity_filter)
            if violations:
                st.subheader(f"⚠️ Violations ({len(violations)})")
                for v in violations:
                    severity = v.get("severity", "unknown").upper()
                    icon = "🔴" if severity == "HIGH" else "🟡" if severity == "MEDIUM" else "🔵"
                    with st.expander(f"{icon} [{severity}] {v.get('rule', 'N/A')}"):
                        st.write(f"**Description:** {v.get('description', 'N/A')}")
                        st.write(f"**Location:** {v.get('location', 'N/A')}")
                        st.write(f"**Remediation:** {v.get('remediation', 'N/A')}")
            else:
                st.success("✅ No violations found!")

            # Compliant areas
            compliant = report.get("compliant_areas", [])
            if compliant:
                st.subheader("✅ Compliant Areas")
                for c in compliant:
                    st.write(f"- **{c.get('rule', 'N/A')}**: {c.get('description', 'N/A')}")

            # Recommendations
            recommendations = report.get("recommendations", [])
            if recommendations:
                st.subheader("📋 Recommendations")
                for rec in recommendations:
                    st.write(f"- {rec}")

            # Download
            st.download_button(
                "📥 Download Report",
                data=json.dumps(report, indent=2),
                file_name="compliance_report.json",
                mime="application/json",
            )
    else:
        st.info("👆 Upload both a document and policy file to check compliance.")


if __name__ == "__main__":
    run()
