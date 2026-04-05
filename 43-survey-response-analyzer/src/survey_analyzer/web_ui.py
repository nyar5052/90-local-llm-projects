"""Streamlit Web UI for Survey Response Analyzer."""

import sys
import os
import json
import logging

import streamlit as st
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.survey_analyzer.core import (
    load_config,
    identify_text_columns,
    identify_demographic_columns,
    extract_themes,
    cluster_themes,
    highlight_verbatims,
    generate_recommendations,
    generate_insights,
    compute_demographic_crosstabs,
)

logger = logging.getLogger(__name__)

st.set_page_config(page_title="Survey Response Analyzer", page_icon="📋", layout="wide")


def render_header():
    """Render the application header."""
    st.title("📋 Survey Response Analyzer")
    st.markdown("*Extract themes, insights, and recommendations from survey data — powered by local LLM*")
    st.divider()


def render_upload_section():
    """Render CSV upload section."""
    st.sidebar.header("📁 Upload Survey Data")
    uploaded_file = st.sidebar.file_uploader("Choose a CSV file", type=["csv"])

    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            if df.empty:
                st.sidebar.error("CSV file is empty.")
                return None, None
            st.sidebar.success(f"✅ Loaded: {df.shape[0]} responses, {df.shape[1]} columns")

            text_cols = []
            for col in df.columns:
                avg_len = df[col].astype(str).str.len().mean()
                if avg_len > 20:
                    text_cols.append(col)
            if not text_cols:
                text_cols = list(df.columns)

            selected_col = st.sidebar.selectbox("Select text column to analyze", text_cols)
            return df, selected_col
        except Exception as e:
            st.sidebar.error(f"Error reading CSV: {e}")
    return None, None


def render_theme_cards(themes: dict):
    """Render theme cards."""
    st.subheader("🎯 Identified Themes")
    theme_list = themes.get("themes", [])

    if not theme_list:
        st.warning("No themes identified.")
        return

    cols = st.columns(min(len(theme_list), 3))
    sentiment_emoji = {"positive": "😊", "negative": "😞", "mixed": "🤔"}

    for i, theme in enumerate(theme_list):
        with cols[i % len(cols)]:
            sentiment = theme.get("sentiment", "mixed")
            emoji = sentiment_emoji.get(sentiment, "❓")
            st.metric(
                label=f"{emoji} {theme.get('name', 'Theme')}",
                value=f"{theme.get('count', 'N/A')} responses",
            )
            st.caption(theme.get("description", ""))
            if theme.get("representative_quotes"):
                with st.expander("Representative Quotes"):
                    for q in theme["representative_quotes"][:3]:
                        st.markdown(f"> _{q}_")


def render_insight_charts(themes: dict):
    """Render insight visualizations."""
    with st.expander("📊 Theme Distribution", expanded=True):
        theme_list = themes.get("themes", [])
        if theme_list:
            chart_data = pd.DataFrame([
                {"Theme": t.get("name", ""), "Count": t.get("count", 0)}
                for t in theme_list
            ])
            st.bar_chart(chart_data.set_index("Theme"))

            sentiment_data = pd.DataFrame([
                {"Theme": t.get("name", ""), "Sentiment": t.get("sentiment", "mixed")}
                for t in theme_list
            ])
            st.dataframe(sentiment_data, use_container_width=True)


def render_recommendations_panel(responses: list[str], themes: dict):
    """Render recommendations panel."""
    with st.expander("💡 Recommendations", expanded=False):
        if st.button("Generate Recommendations"):
            with st.spinner("Generating recommendations..."):
                recs = generate_recommendations(responses, themes)
                if recs:
                    for i, rec in enumerate(recs, 1):
                        priority = rec.get("priority", "medium")
                        priority_colors = {"high": "🔴", "medium": "🟡", "low": "🟢"}
                        icon = priority_colors.get(priority, "⚪")
                        st.markdown(f"### {icon} {i}. {rec.get('title', 'Recommendation')}")
                        st.markdown(rec.get("description", ""))
                        col1, col2 = st.columns(2)
                        col1.info(f"**Priority:** {priority.title()}")
                        col2.info(f"**Effort:** {rec.get('effort', 'medium').title()}")
                        if rec.get("expected_impact"):
                            st.success(f"**Expected Impact:** {rec['expected_impact']}")
                        st.divider()
                else:
                    st.warning("Could not generate recommendations.")


def render_verbatims(responses: list[str], themes: dict):
    """Render highlighted verbatim quotes."""
    with st.expander("📌 Notable Verbatim Responses", expanded=False):
        if st.button("Find Notable Quotes"):
            with st.spinner("Analyzing responses..."):
                verbatims = highlight_verbatims(responses, themes)
                if verbatims:
                    for v in verbatims:
                        impact = v.get("impact", "medium")
                        st.markdown(f"**{v.get('theme', 'Theme')}** | Impact: `{impact}`")
                        st.info(f'> "{v.get("text", "")}"')
                        st.caption(v.get("reason", ""))
                        st.divider()
                else:
                    st.info("No notable quotes found.")


def main():
    """Main Streamlit application."""
    load_config()
    render_header()

    df, selected_col = render_upload_section()

    if df is not None and selected_col:
        responses = df[selected_col].dropna().astype(str).tolist()
        responses = [r.strip() for r in responses if r.strip()]

        st.info(f"📊 Analyzing **{len(responses)}** responses from column **{selected_col}**")

        if "survey_themes" not in st.session_state or st.sidebar.button("🔄 Re-analyze"):
            with st.spinner("Extracting themes..."):
                themes = extract_themes(responses)
                st.session_state["survey_themes"] = themes
                st.session_state["survey_responses"] = responses

        themes = st.session_state.get("survey_themes", {"themes": []})
        responses = st.session_state.get("survey_responses", responses)

        render_theme_cards(themes)
        st.divider()
        render_insight_charts(themes)
        render_recommendations_panel(responses, themes)
        render_verbatims(responses, themes)
    else:
        st.info("👈 Upload a survey CSV file to get started!")
        st.markdown("""
        ### Features
        - 🎯 **Theme clustering** — automatically identify and group themes
        - 📊 **Demographic cross-tabs** — analyze by demographic groups
        - 📌 **Verbatim highlighting** — surface impactful quotes
        - 💡 **Recommendation engine** — actionable improvement suggestions
        - 📈 **Visual insights** — charts and distribution views
        """)


if __name__ == "__main__":
    main()
