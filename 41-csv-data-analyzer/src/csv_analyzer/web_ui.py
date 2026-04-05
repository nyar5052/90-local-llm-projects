"""Streamlit Web UI for CSV Data Analyzer."""

import sys
import os
import json
import logging

import streamlit as st
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.csv_analyzer.core import (
    load_config,
    detect_column_types,
    generate_statistical_summary,
    compute_correlations,
    suggest_charts,
    analyze_data,
    export_insights,
)

logger = logging.getLogger(__name__)

st.set_page_config(page_title="CSV Data Analyzer", page_icon="📊", layout="wide")


def render_header():
    """Render the application header."""
    st.title("📊 CSV Data Analyzer")
    st.markdown("*Ask natural language questions about your CSV data — powered by local LLM*")
    st.divider()


def render_upload_section() -> pd.DataFrame | None:
    """Render CSV upload section and return DataFrame."""
    st.sidebar.header("📁 Upload Data")
    uploaded_file = st.sidebar.file_uploader("Choose a CSV file", type=["csv"])

    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            if df.empty:
                st.sidebar.error("CSV file is empty.")
                return None
            st.sidebar.success(f"✅ Loaded: {df.shape[0]} rows × {df.shape[1]} columns")
            return df
        except Exception as e:
            st.sidebar.error(f"Error reading CSV: {e}")
            return None
    return None


def render_data_preview(df: pd.DataFrame):
    """Render data preview table."""
    with st.expander("📋 Data Preview", expanded=True):
        st.dataframe(df.head(20), use_container_width=True)
        col1, col2, col3 = st.columns(3)
        col1.metric("Rows", df.shape[0])
        col2.metric("Columns", df.shape[1])
        col3.metric("Missing Values", int(df.isnull().sum().sum()))


def render_column_types(df: pd.DataFrame):
    """Render auto-detected column types."""
    with st.expander("🔍 Column Types", expanded=False):
        column_types = detect_column_types(df)
        type_emoji = {
            "numeric": "🔢", "categorical": "🏷️", "datetime": "📅",
            "text": "📝", "boolean": "✅",
        }
        cols = st.columns(min(len(column_types), 4))
        for i, (col, ctype) in enumerate(column_types.items()):
            emoji = type_emoji.get(ctype, "❓")
            cols[i % len(cols)].info(f"{emoji} **{col}**\n\n{ctype}")


def render_statistics(df: pd.DataFrame):
    """Render statistical summaries."""
    with st.expander("📈 Statistical Summary", expanded=False):
        stats = generate_statistical_summary(df)
        tab1, tab2 = st.tabs(["Numeric Stats", "Categorical Stats"])

        with tab1:
            numeric_cols = df.select_dtypes(include=["number"])
            if not numeric_cols.empty:
                st.dataframe(numeric_cols.describe(), use_container_width=True)
                if "skewness" in stats:
                    st.markdown("**Skewness:**")
                    skew_df = pd.DataFrame([stats["skewness"]], index=["Skewness"])
                    st.dataframe(skew_df, use_container_width=True)
            else:
                st.info("No numeric columns found.")

        with tab2:
            if "categorical_stats" in stats:
                for col, info in stats["categorical_stats"].items():
                    st.markdown(f"**{col}** — {info['unique_count']} unique values")
                    if info["top_values"]:
                        st.bar_chart(pd.Series(info["top_values"]))
            else:
                st.info("No categorical columns found.")


def render_correlations(df: pd.DataFrame):
    """Render correlation analysis."""
    with st.expander("🔗 Correlation Analysis", expanded=False):
        correlations = compute_correlations(df)
        if correlations:
            corr_df = pd.DataFrame(correlations["matrix"])
            st.dataframe(corr_df.style.background_gradient(cmap="RdBu_r", vmin=-1, vmax=1),
                         use_container_width=True)
            if correlations["strong_correlations"]:
                st.markdown("**Strong Correlations:**")
                for c in correlations["strong_correlations"]:
                    direction = "📈" if c["correlation"] > 0 else "📉"
                    st.markdown(f"- {direction} **{c['col1']}** ↔ **{c['col2']}**: "
                                f"`{c['correlation']:.4f}` ({c['strength']})")
        else:
            st.info("Need at least 2 numeric columns for correlation analysis.")


def render_chart_suggestions(df: pd.DataFrame):
    """Render chart area with suggested visualizations."""
    with st.expander("📊 Charts & Visualizations", expanded=False):
        column_types = detect_column_types(df)
        suggestions = suggest_charts(df, column_types)
        numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()

        if suggestions:
            selected = st.selectbox(
                "Select a chart",
                options=range(len(suggestions)),
                format_func=lambda i: f"{suggestions[i]['type'].title()} — {suggestions[i]['reason']}",
            )
            s = suggestions[selected]
            if s["type"] == "histogram" and s["columns"][0] in df.columns:
                st.bar_chart(df[s["columns"][0]].value_counts().head(20))
            elif s["type"] == "scatter" and len(s["columns"]) >= 2:
                st.scatter_chart(df, x=s["columns"][0], y=s["columns"][1])
            elif s["type"] == "line" and len(s["columns"]) >= 2:
                st.line_chart(df.set_index(s["columns"][0])[s["columns"][1]])
            elif s["type"] == "bar" and len(s["columns"]) >= 2:
                chart_data = df.groupby(s["columns"][0])[s["columns"][1]].mean()
                st.bar_chart(chart_data)

        if len(numeric_cols) >= 2:
            st.markdown("**Custom Scatter Plot:**")
            col1, col2 = st.columns(2)
            x_col = col1.selectbox("X axis", numeric_cols, key="scatter_x")
            y_col = col2.selectbox("Y axis", numeric_cols, index=min(1, len(numeric_cols) - 1), key="scatter_y")
            st.scatter_chart(df, x=x_col, y=y_col)


def render_query_section(df: pd.DataFrame):
    """Render natural language query section."""
    st.subheader("💬 Ask Questions About Your Data")
    query = st.text_input("Enter your question:", placeholder="What trends do you see in the data?")

    if st.button("🔍 Analyze", type="primary") and query:
        with st.spinner("Analyzing data with LLM..."):
            try:
                answer = analyze_data(df, query)
                st.markdown("### 📈 Analysis Result")
                st.markdown(answer)
            except Exception as e:
                st.error(f"Analysis failed: {e}")

    st.divider()
    if st.button("📥 Export Insights as JSON"):
        with st.spinner("Exporting..."):
            output_path = "csv_insights_export.json"
            export_insights(df, output_path)
            with open(output_path, "r") as f:
                st.download_button("Download Insights", f.read(),
                                   file_name="csv_insights.json", mime="application/json")


def main():
    """Main Streamlit application."""
    load_config()
    render_header()

    df = render_upload_section()

    if df is not None:
        render_data_preview(df)
        render_column_types(df)
        render_statistics(df)
        render_correlations(df)
        render_chart_suggestions(df)
        render_query_section(df)
    else:
        st.info("👈 Upload a CSV file to get started!")
        st.markdown("""
        ### Features
        - 🔍 **Auto-detect column types** — numeric, categorical, datetime, text
        - 📈 **Statistical summaries** — descriptive stats, skewness, kurtosis
        - 🔗 **Correlation analysis** — find relationships between variables
        - 📊 **Chart suggestions** — intelligent visualization recommendations
        - 💬 **Natural language queries** — ask questions about your data
        - 📥 **Export insights** — download analysis as JSON
        """)


if __name__ == "__main__":
    main()
