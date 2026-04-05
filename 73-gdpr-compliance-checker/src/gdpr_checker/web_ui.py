"""Streamlit Web UI for GDPR Compliance Checker."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))

import streamlit as st

from src.gdpr_checker.core import (
    check_compliance,
    generate_checklist,
    build_article_checklist,
    map_data_flows,
    generate_dpo_recommendations,
    ComplianceStatus,
    CHECK_TYPES,
)
from src.gdpr_checker.config import load_config

st.set_page_config(
    page_title="🔒 GDPR Compliance Checker",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="expanded",
)

STATUS_ICONS = {
    ComplianceStatus.COMPLIANT: "✅",
    ComplianceStatus.PARTIALLY_COMPLIANT: "⚠️",
    ComplianceStatus.NON_COMPLIANT: "❌",
    ComplianceStatus.NOT_ADDRESSED: "❓",
}

config = load_config()


def main():
    st.title("🔒 GDPR Compliance Checker")
    st.caption("Article-by-Article Analysis, Data Flow Mapping & DPO Recommendations")

    with st.sidebar:
        st.header("⚙️ Settings")
        check_type = st.selectbox("Check Focus", list(CHECK_TYPES.keys()), index=0)
        st.divider()
        st.markdown("### 📊 Compliance Summary")
        if "checklist" in st.session_state:
            items = st.session_state["checklist"]
            compliant = sum(1 for i in items if i.status == ComplianceStatus.COMPLIANT)
            partial = sum(1 for i in items if i.status == ComplianceStatus.PARTIALLY_COMPLIANT)
            non_comp = sum(1 for i in items if i.status == ComplianceStatus.NON_COMPLIANT)
            st.metric("Compliant", f"{compliant}/{len(items)}")
            st.metric("Partially Compliant", partial)
            st.metric("Non-Compliant", non_comp)

    tab_upload, tab_checklist, tab_flows, tab_audit = st.tabs(
        ["📄 Document Upload", "✅ Compliance Checklist", "🔀 Data Flow Diagram", "📋 Audit Log"]
    )

    with tab_upload:
        st.subheader("Upload Document for Analysis")
        content = st.text_area(
            "Paste privacy policy, code, or document content:",
            height=250,
            placeholder="We collect user email addresses for marketing purposes...",
        )
        uploaded = st.file_uploader("Or upload a document", type=["txt", "md", "py", "html", "json"])
        if uploaded:
            content = uploaded.read().decode("utf-8", errors="replace")
            st.success(f"Loaded {uploaded.name}")

        col1, col2, col3 = st.columns(3)
        with col1:
            check_btn = st.button("🔍 Check Compliance", type="primary", use_container_width=True)
        with col2:
            article_btn = st.button("📋 Article Checklist", use_container_width=True)
        with col3:
            flow_btn = st.button("🔀 Map Data Flows", use_container_width=True)

        if check_btn and content.strip():
            with st.spinner("Analyzing GDPR compliance..."):
                result = check_compliance(content, check_type)
            st.session_state["compliance_result"] = result
            st.markdown("### 📋 Compliance Report")
            st.markdown(result)

        if article_btn and content.strip():
            items = build_article_checklist(content)
            st.session_state["checklist"] = items
            recs = generate_dpo_recommendations(items)
            st.session_state["dpo_recs"] = recs
            st.success(f"Analyzed {len(items)} GDPR articles")
            st.rerun()

        if flow_btn and content.strip():
            flows = map_data_flows(content)
            st.session_state["data_flows"] = flows
            st.success(f"Found {len(flows)} data flows")

    with tab_checklist:
        st.subheader("✅ GDPR Article-by-Article Checklist")
        if "checklist" in st.session_state:
            items = st.session_state["checklist"]
            for item in items:
                icon = STATUS_ICONS.get(item.status, "❓")
                with st.expander(f"{icon} {item.article}: {item.title}"):
                    st.markdown(f"**Description:** {item.description}")
                    st.markdown(f"**Status:** {item.status.value.replace('_', ' ').title()}")
                    st.markdown(f"**Findings:** {item.findings}")
                    if item.recommendation:
                        st.markdown(f"**Recommendation:** {item.recommendation}")

            if "dpo_recs" in st.session_state:
                st.divider()
                st.markdown("### 🧑‍⚖️ DPO Recommendations")
                for r in st.session_state["dpo_recs"]:
                    prio_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(r.priority, "⚪")
                    st.markdown(f"{prio_icon} **[{r.priority.upper()}] {r.article}:** {r.recommendation}")
        else:
            st.info("Run an Article Checklist analysis from the Document Upload tab.")

    with tab_flows:
        st.subheader("🔀 Data Flow Mapping")
        if "data_flows" in st.session_state:
            flows = st.session_state["data_flows"]
            if flows:
                flow_data = [{
                    "Data Type": f.data_type,
                    "Source": f.source,
                    "Destination": f.destination,
                    "Purpose": f.purpose,
                    "Cross-Border": "⚠️ Yes" if f.cross_border else "No",
                } for f in flows]
                st.dataframe(flow_data, use_container_width=True)
            else:
                st.info("No data flows detected in the document.")
        else:
            st.info("Map data flows from the Document Upload tab.")

    with tab_audit:
        st.subheader("📋 Audit Log")
        if "audit_log" not in st.session_state:
            st.session_state["audit_log"] = []
        if st.session_state["audit_log"]:
            audit_data = [{
                "Timestamp": e.timestamp,
                "Action": e.action,
                "Article": e.article,
                "Status": e.status,
            } for e in st.session_state["audit_log"]]
            st.dataframe(audit_data, use_container_width=True)
        else:
            st.info("Audit entries will appear here as you perform compliance checks.")


if __name__ == "__main__":
    main()
