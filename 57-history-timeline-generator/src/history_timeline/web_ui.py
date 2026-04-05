"""Streamlit Web UI for History Timeline Generator."""

import streamlit as st

# Custom CSS for professional dark theme
st.set_page_config(page_title="History Timeline Generator", page_icon="🎯", layout="wide")

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

import json
import logging

from .core import (
    generate_timeline,
    get_figure_profiles,
    get_cause_effect_chains,
    check_service,
    Timeline,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CATEGORY_COLORS = {
    "political": "🔵", "military": "🔴", "social": "🟣",
    "economic": "🟡", "cultural": "🔵", "scientific": "🟢",
}


def main():
    st.title("📜 History Timeline Generator")
    st.caption("Powered by Local LLM — Interactive historical timelines")

    if not check_service():
        st.error("⚠️ Ollama is not running. Start it with: `ollama serve`")
        return

    tab_timeline, tab_figures, tab_cause = st.tabs(
        ["📅 Timeline", "👤 Key Figures", "🔗 Cause & Effect"]
    )

    # ------------------------------------------------------------------
    # Tab 1: Timeline
    # ------------------------------------------------------------------
    with tab_timeline:
        col1, col2 = st.columns([3, 1])
        with col1:
            topic = st.text_input("Historical topic", placeholder="e.g., American Civil War")
        with col2:
            detail = st.selectbox("Detail level", ["brief", "medium", "detailed"])

        col3, col4 = st.columns(2)
        with col3:
            start_year = st.text_input("Start year (optional)", "")
        with col4:
            end_year = st.text_input("End year (optional)", "")

        if st.button("🚀 Generate Timeline", type="primary", use_container_width=True):
            if not topic.strip():
                st.warning("Please enter a historical topic.")
            else:
                with st.spinner("Researching history..."):
                    try:
                        tl = generate_timeline(topic, detail, start_year, end_year)
                        _display_timeline(tl)
                    except Exception as e:
                        st.error(f"Error: {e}")

    # ------------------------------------------------------------------
    # Tab 2: Key Figures
    # ------------------------------------------------------------------
    with tab_figures:
        fig_topic = st.text_input("Topic for key figures", placeholder="e.g., Renaissance", key="fig_topic")
        if st.button("👤 Get Figure Profiles", use_container_width=True):
            if fig_topic.strip():
                with st.spinner("Researching key figures..."):
                    try:
                        profiles = get_figure_profiles(fig_topic)
                        _display_figures(profiles)
                    except Exception as e:
                        st.error(f"Error: {e}")

    # ------------------------------------------------------------------
    # Tab 3: Cause & Effect
    # ------------------------------------------------------------------
    with tab_cause:
        ce_topic = st.text_input("Topic for cause-effect analysis", placeholder="e.g., French Revolution", key="ce_topic")
        if st.button("🔗 Analyze Cause-Effect Chains", use_container_width=True):
            if ce_topic.strip():
                with st.spinner("Analyzing..."):
                    try:
                        chains = get_cause_effect_chains(ce_topic)
                        _display_cause_effect(chains)
                    except Exception as e:
                        st.error(f"Error: {e}")


def _display_timeline(tl: Timeline) -> None:
    st.divider()
    st.subheader(tl.title)
    st.markdown(f"**Period:** {tl.period}")
    st.markdown(tl.overview)

    if tl.eras:
        st.subheader("🏛️ Eras")
        for era in tl.eras:
            st.markdown(f"**{era.get('name', '')}** ({era.get('start', '')}–{era.get('end', '')}): {era.get('description', '')}")

    st.subheader("📅 Events")
    for event in tl.events:
        icon = CATEGORY_COLORS.get(event.category, "⚪")
        with st.expander(f"{icon} {event.date} — {event.event}", expanded=False):
            st.markdown(event.description)
            if event.key_figures:
                st.markdown(f"**Key Figures:** {', '.join(event.key_figures)}")
            st.info(f"**Significance:** {event.significance}")

    if tl.key_themes:
        st.subheader("🔑 Key Themes")
        for t in tl.key_themes:
            st.markdown(f"- {t}")

    if tl.legacy:
        st.subheader("🏛️ Legacy")
        st.markdown(tl.legacy)

    st.download_button("📥 Download Timeline (JSON)", json.dumps(tl.to_dict(), indent=2),
                       file_name="timeline.json", mime="application/json")


def _display_figures(figures) -> None:
    for fig in figures:
        with st.expander(f"👤 {fig.name} — {fig.role}", expanded=True):
            st.markdown(f"**Era:** {fig.era}")
            st.markdown(fig.summary)
            if fig.key_contributions:
                st.markdown("**Key Contributions:**")
                for c in fig.key_contributions:
                    st.markdown(f"- {c}")


def _display_cause_effect(chains) -> None:
    for i, chain in enumerate(chains):
        st.markdown(f"### Chain {i+1}")
        col1, col2, col3 = st.columns(3)
        col1.warning(f"**Cause:** {chain.cause}")
        col2.info(f"**Event:** {chain.event}")
        col3.success(f"**Effect:** {chain.effect}")
        st.markdown(f"**Long-term Impact:** {chain.long_term_impact}")
        st.divider()


if __name__ == "__main__":
    main()
