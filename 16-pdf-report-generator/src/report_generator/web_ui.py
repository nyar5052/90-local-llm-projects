"""Streamlit web interface for the Report Generator."""

import streamlit as st
import pandas as pd
import os
import sys

from .core import summarize_data, generate_report, save_report, REPORT_TEMPLATES
from .config import load_config
from .utils import setup_sys_path

setup_sys_path()
from common.llm_client import check_ollama_running


def run():
    """Launch the Streamlit web UI."""
    config = load_config()

    # Custom CSS for professional dark theme
    st.set_page_config(page_title="PDF Report Generator", page_icon="🎯", layout="wide")

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
    st.title("📊 Report Generator")
    st.markdown("Generate professional reports from CSV data using a local LLM.")

    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Configuration")

        # Check Ollama status
        if check_ollama_running():
            st.success("✅ Ollama is running")
        else:
            st.error("❌ Ollama is not running. Start with: `ollama serve`")
            return

        template = st.selectbox(
            "Report Template",
            options=list(REPORT_TEMPLATES.keys()),
            index=0,
            help="Choose the report style",
        )

        fmt = st.selectbox(
            "Output Format",
            options=["markdown", "html", "text"],
            index=0,
        )

        preview_length = st.slider(
            "Preview Length",
            min_value=500,
            max_value=5000,
            value=config.get("report", {}).get("preview_length", 2000),
            step=500,
        )

    # Main content
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("📁 Data Upload")
        uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])
        topic = st.text_input("Report Topic", placeholder="e.g., Q4 Sales Analysis")

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)

        with col2:
            st.subheader("📋 Data Preview")
            st.dataframe(df.head(10), use_container_width=True)
            st.caption(f"{len(df)} rows × {len(df.columns)} columns")

        # Convert to headers/rows format
        headers = list(df.columns)
        rows = df.to_dict("records")

        # Data summary
        with st.expander("📊 Data Summary", expanded=False):
            summary = summarize_data(headers, rows)
            st.code(summary)

        # Generate report
        if topic and st.button("🚀 Generate Report", type="primary", use_container_width=True):
            data_summary = summarize_data(headers, rows)

            with st.spinner(f"Generating {template} report..."):
                report_content = generate_report(
                    topic, data_summary, template=template, config=config
                )

            st.success("✅ Report generated!")

            # Report preview
            st.subheader("📄 Report Preview")
            st.markdown(report_content[:preview_length])
            if len(report_content) > preview_length:
                st.caption(f"Showing first {preview_length} of {len(report_content)} characters")

            # Download buttons
            st.subheader("⬇️ Download")
            col_dl1, col_dl2, col_dl3 = st.columns(3)

            with col_dl1:
                st.download_button(
                    "📥 Download Markdown",
                    data=report_content,
                    file_name=f"{topic.replace(' ', '_')}_report.md",
                    mime="text/markdown",
                )
            with col_dl2:
                st.download_button(
                    "📥 Download Text",
                    data=report_content,
                    file_name=f"{topic.replace(' ', '_')}_report.txt",
                    mime="text/plain",
                )
            with col_dl3:
                st.download_button(
                    "📥 Download HTML",
                    data=f"<html><body><pre>{report_content}</pre></body></html>",
                    file_name=f"{topic.replace(' ', '_')}_report.html",
                    mime="text/html",
                )
    else:
        st.info("👆 Upload a CSV file to get started.")


if __name__ == "__main__":
    run()
