"""
EHR De-Identifier Web UI - Streamlit interface for PII removal.

╔══════════════════════════════════════════════════════════════════════╗
║  ⛔ CRITICAL DISCLAIMER ⛔                                         ║
║                                                                      ║
║  This tool is for EDUCATIONAL and RESEARCH purposes ONLY.            ║
║  It is NOT certified for HIPAA compliance. Do NOT use on real        ║
║  patient data. ALWAYS use certified tools for real PHI.              ║
╚══════════════════════════════════════════════════════════════════════╝
"""

import os
import sys
import json
import copy

import streamlit as st

# Ensure imports work from project root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.ehr_deidentifier.core import (
    HIPAA_IDENTIFIERS,
    DEFAULT_PII_RULES,
    AuditLog,
    ValidationReport,
    check_ollama_running,
    deidentify_text,
    configurable_regex_preprocess,
    read_file,
    write_file,
)


# =========================================================================
# Session state initialization
# =========================================================================
def _init_session_state():
    if "audit" not in st.session_state:
        st.session_state.audit = AuditLog()
    if "results_history" not in st.session_state:
        st.session_state.results_history = []
    if "pii_rules" not in st.session_state:
        st.session_state.pii_rules = copy.deepcopy(DEFAULT_PII_RULES)


# =========================================================================
# Disclaimer banner
# =========================================================================
def _show_disclaimer():
    st.error(
        "⛔ **CRITICAL DISCLAIMER** ⛔\n\n"
        "This tool is for **EDUCATIONAL and RESEARCH purposes ONLY**. "
        "It is **NOT** certified for **HIPAA compliance**. "
        "Do **NOT** use this tool on real patient data. "
        "**ALWAYS** use certified, validated de-identification tools "
        "for real Protected Health Information (PHI). "
        "This is **NOT** medical or legal advice.\n\n"
        "**Using this tool on real patient data could violate HIPAA "
        "regulations and result in serious legal consequences.**"
    )


# =========================================================================
# Sidebar
# =========================================================================
def _render_sidebar():
    with st.sidebar:
        st.title("⚙️ Settings")

        st.warning(
            "⚠️ **NOT HIPAA Certified**\n\n"
            "Educational use only."
        )

        # Ollama status
        ollama_ok = check_ollama_running()
        if ollama_ok:
            st.success("✅ Ollama is running")
        else:
            st.error("❌ Ollama is not running. Start it with: `ollama serve`")

        st.divider()
        st.subheader("PII Rule Toggles")

        for rule_name, rule in st.session_state.pii_rules.items():
            rule["enabled"] = st.checkbox(
                f"{rule['description']}",
                value=rule["enabled"],
                key=f"rule_{rule_name}",
            )

        st.divider()
        st.caption(
            "⚠️ This tool is for educational purposes only. "
            "NOT certified for HIPAA compliance."
        )


# =========================================================================
# Tab: Single Text
# =========================================================================
def _tab_single_text():
    st.header("📝 Single Text De-Identification")

    _show_disclaimer()

    input_text = st.text_area(
        "Enter medical text to de-identify:",
        height=200,
        placeholder="Patient John Smith, SSN 123-45-6789, DOB 01/15/1980...",
    )

    if st.button("🛡️ De-identify", type="primary", key="btn_single"):
        if not input_text.strip():
            st.warning("Please enter some text.")
            return

        if not check_ollama_running():
            st.error("❌ Ollama is not running. Please start it first.")
            return

        with st.spinner("De-identifying text..."):
            result = deidentify_text(input_text)

        st.session_state.audit.log_operation(
            "single_text", "<web_ui>", result["regex_replacements"], "success"
        )
        st.session_state.results_history.append(result)

        # Side-by-side display
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📄 Original")
            st.text_area(
                "Original text",
                result["original"],
                height=300,
                disabled=True,
                label_visibility="collapsed",
            )

        with col2:
            st.subheader("🛡️ De-Identified")
            st.text_area(
                "De-identified text",
                result["final"],
                height=300,
                disabled=True,
                label_visibility="collapsed",
            )

        # Replacements table
        if result["regex_replacements"]:
            st.subheader("🔍 Regex-Detected PII")
            st.table(
                [
                    {
                        "Type": r["type"],
                        "Original": r["original"],
                        "Replaced With": r["placeholder"],
                    }
                    for r in result["regex_replacements"]
                ]
            )

        # Validation
        report = ValidationReport(
            result["original"], result["final"], result["regex_replacements"]
        )
        st.text(report.generate_report())

        st.error(
            "⚠️ **REMINDER**: This output has NOT been validated for "
            "HIPAA compliance. Manual review is ALWAYS required."
        )


# =========================================================================
# Tab: File Upload
# =========================================================================
def _tab_file_upload():
    st.header("📁 File Upload De-Identification")

    _show_disclaimer()

    uploaded_file = st.file_uploader(
        "Upload a medical record file",
        type=["txt", "csv", "md", "text"],
        key="file_upload_single",
    )

    if uploaded_file is not None:
        text = uploaded_file.getvalue().decode("utf-8")
        st.text_area(
            "File contents:",
            text,
            height=150,
            disabled=True,
        )

        if st.button("🛡️ De-identify File", type="primary", key="btn_file"):
            if not check_ollama_running():
                st.error("❌ Ollama is not running. Please start it first.")
                return

            with st.spinner("De-identifying file contents..."):
                result = deidentify_text(text)

            st.session_state.audit.log_operation(
                "file_upload",
                uploaded_file.name,
                result["regex_replacements"],
                "success",
            )
            st.session_state.results_history.append(result)

            st.subheader("🛡️ De-Identified Result")
            st.text_area(
                "Result",
                result["final"],
                height=300,
                disabled=True,
                label_visibility="collapsed",
            )

            # Download button
            st.download_button(
                "📥 Download De-identified File",
                data=result["final"],
                file_name=f"deidentified_{uploaded_file.name}",
                mime="text/plain",
            )

            if result["regex_replacements"]:
                st.subheader("🔍 PII Detected")
                st.table(
                    [
                        {
                            "Type": r["type"],
                            "Original": r["original"],
                            "Replaced With": r["placeholder"],
                        }
                        for r in result["regex_replacements"]
                    ]
                )

            st.error(
                "⚠️ **REMINDER**: Manual review is ALWAYS required. "
                "This tool is NOT certified for HIPAA compliance."
            )


# =========================================================================
# Tab: Batch Processing
# =========================================================================
def _tab_batch():
    st.header("📦 Batch Processing")

    _show_disclaimer()

    uploaded_files = st.file_uploader(
        "Upload multiple medical record files",
        type=["txt", "csv", "md", "text"],
        accept_multiple_files=True,
        key="file_upload_batch",
    )

    if uploaded_files and st.button(
        "🛡️ Process All Files", type="primary", key="btn_batch"
    ):
        if not check_ollama_running():
            st.error("❌ Ollama is not running. Please start it first.")
            return

        progress = st.progress(0)
        results = []

        for idx, ufile in enumerate(uploaded_files):
            with st.spinner(f"Processing {ufile.name}..."):
                text = ufile.getvalue().decode("utf-8")
                result = deidentify_text(text)
                result["source_file"] = ufile.name
                result["status"] = "success"
                results.append(result)

                st.session_state.audit.log_operation(
                    "batch_upload",
                    ufile.name,
                    result["regex_replacements"],
                    "success",
                )
                st.session_state.results_history.append(result)

            progress.progress((idx + 1) / len(uploaded_files))

        st.success(f"✅ Processed {len(results)} file(s)")

        for r in results:
            with st.expander(f"📄 {r['source_file']}"):
                st.text_area(
                    "De-identified",
                    r["final"],
                    height=200,
                    disabled=True,
                    key=f"batch_result_{r['source_file']}",
                )
                st.download_button(
                    f"📥 Download {r['source_file']}",
                    data=r["final"],
                    file_name=f"deidentified_{r['source_file']}",
                    mime="text/plain",
                    key=f"dl_{r['source_file']}",
                )

        st.error(
            "⚠️ **REMINDER**: ALL output requires manual review. "
            "NOT certified for HIPAA compliance."
        )


# =========================================================================
# Tab: Audit Log
# =========================================================================
def _tab_audit():
    st.header("📋 Audit Log")

    st.warning(
        "⚠️ This audit log is for educational purposes only. "
        "It is NOT a HIPAA-compliant audit trail."
    )

    log = st.session_state.audit.get_log()

    if not log:
        st.info("No audit log entries yet. Process some text to generate entries.")
        return

    summary = st.session_state.audit.get_summary()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Operations", summary["total_operations"])
    col2.metric("Total PII Found", summary.get("total_pii_found", 0))
    col3.metric("Successes", summary.get("success_count", 0))
    col4.metric("Errors", summary.get("error_count", 0))

    st.divider()

    st.dataframe(
        [
            {
                "Timestamp": e["timestamp"],
                "Operation": e["operation"],
                "Source": e["input_source"],
                "PII Count": e["pii_count"],
                "PII Types": ", ".join(e["pii_types_found"]),
                "Status": e["status"],
            }
            for e in log
        ],
        use_container_width=True,
    )

    # Export button
    export_data = json.dumps(log, indent=2)
    st.download_button(
        "📥 Export Audit Log (JSON)",
        data=export_data,
        file_name="audit_log.json",
        mime="application/json",
    )


# =========================================================================
# Tab: PII Statistics
# =========================================================================
def _tab_statistics():
    st.header("📊 PII Statistics")

    _show_disclaimer()

    history = st.session_state.results_history

    if not history:
        st.info(
            "No data yet. Process some text or files to see statistics."
        )
        return

    # Aggregate PII types
    pii_counts: dict[str, int] = {}
    total_replacements = 0

    for result in history:
        for r in result.get("regex_replacements", []):
            pii_type = r["type"]
            pii_counts[pii_type] = pii_counts.get(pii_type, 0) + 1
            total_replacements += 1

    col1, col2 = st.columns(2)
    col1.metric("Total Records Processed", len(history))
    col2.metric("Total PII Items Replaced", total_replacements)

    if pii_counts:
        st.subheader("PII Type Distribution")
        st.bar_chart(pii_counts)

        st.subheader("Detailed Counts")
        st.table(
            [
                {"PII Type": k, "Count": v}
                for k, v in sorted(
                    pii_counts.items(), key=lambda x: x[1], reverse=True
                )
            ]
        )


# =========================================================================
# Main
# =========================================================================
def main():
    st.set_page_config(
        page_title="🛡️ EHR De-Identifier",
        page_icon="🛡️",
        layout="wide",
    )

    _init_session_state()

    st.title("🛡️ EHR De-Identifier")

    # Top-level disclaimer – VERY prominent
    _show_disclaimer()

    _render_sidebar()

    tab_single, tab_file, tab_batch, tab_audit, tab_stats = st.tabs(
        [
            "📝 Single Text",
            "📁 File Upload",
            "📦 Batch Processing",
            "📋 Audit Log",
            "📊 PII Statistics",
        ]
    )

    with tab_single:
        _tab_single_text()

    with tab_file:
        _tab_file_upload()

    with tab_batch:
        _tab_batch()

    with tab_audit:
        _tab_audit()

    with tab_stats:
        _tab_statistics()

    # Footer disclaimer
    st.divider()
    st.error(
        "⛔ **FINAL REMINDER**: This tool is for EDUCATIONAL purposes ONLY. "
        "It is NOT certified for HIPAA compliance. Do NOT use on real patient data. "
        "ALWAYS have qualified professionals review de-identified records."
    )


if __name__ == "__main__":
    main()
