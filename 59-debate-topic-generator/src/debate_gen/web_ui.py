"""Streamlit Web UI for Debate Topic Generator."""

import streamlit as st
import json
import logging

from .core import (
    generate_debate_topics,
    generate_moderator_guide,
    check_service,
    DebateSet,
    DebateTopic,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.set_page_config(page_title="🎙️ Debate Topic Generator", page_icon="🎙️", layout="wide")

STRENGTH_EMOJIS = {"weak": "🔴", "moderate": "🟡", "strong": "🟢"}


def main():
    st.title("🎙️ Debate Topic Generator")
    st.caption("Powered by Local LLM — Balanced arguments with evidence ratings")

    if not check_service():
        st.error("⚠️ Ollama is not running. Start it with: `ollama serve`")
        return

    tab_gen, tab_evidence, tab_moderator = st.tabs(
        ["🎯 Generate Topics", "📊 Evidence Panel", "📋 Moderator Notes"]
    )

    # ------------------------------------------------------------------
    # Tab 1: Generate Topics
    # ------------------------------------------------------------------
    with tab_gen:
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            subject = st.text_input("Subject area", placeholder="e.g., technology, education, ethics")
        with col2:
            complexity = st.selectbox("Complexity", ["basic", "intermediate", "advanced"])
        with col3:
            num_topics = st.slider("Number of topics", 1, 5, 3)

        if st.button("🚀 Generate Debate Topics", type="primary", use_container_width=True):
            if subject.strip():
                with st.spinner("Crafting debate topics..."):
                    try:
                        ds = generate_debate_topics(subject, complexity, num_topics)
                        st.session_state.debate_set = ds
                    except Exception as e:
                        st.error(f"Error: {e}")

        if "debate_set" in st.session_state:
            _display_debate_set(st.session_state.debate_set)

    # ------------------------------------------------------------------
    # Tab 2: Evidence Panel
    # ------------------------------------------------------------------
    with tab_evidence:
        if "debate_set" not in st.session_state:
            st.info("Generate debate topics first!")
        else:
            ds = st.session_state.debate_set
            st.subheader("📊 Evidence Strength Analysis")
            for topic in ds.topics:
                with st.expander(f"Topic {topic.number}: {topic.motion}", expanded=True):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("**PRO Evidence:**")
                        for arg in topic.pro_arguments:
                            emoji = STRENGTH_EMOJIS.get(arg.strength, "⚪")
                            st.markdown(f"{emoji} **{arg.point}**: {arg.evidence}")
                    with col2:
                        st.markdown("**CON Evidence:**")
                        for arg in topic.con_arguments:
                            emoji = STRENGTH_EMOJIS.get(arg.strength, "⚪")
                            st.markdown(f"{emoji} **{arg.point}**: {arg.evidence}")

    # ------------------------------------------------------------------
    # Tab 3: Moderator Notes
    # ------------------------------------------------------------------
    with tab_moderator:
        motion = st.text_input("Debate motion", placeholder="Enter the debate motion/resolution")
        if st.button("📋 Generate Moderator Guide", use_container_width=True):
            if motion.strip():
                with st.spinner("Creating moderator guide..."):
                    try:
                        guide = generate_moderator_guide(motion)
                        _display_moderator_guide(guide)
                    except Exception as e:
                        st.error(f"Error: {e}")


# ---------------------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------------------


def _display_debate_set(ds: DebateSet) -> None:
    st.divider()
    for topic in ds.topics:
        st.subheader(f"Topic {topic.number}: {topic.motion}")
        st.markdown(f"*{topic.context}*")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### ✅ PRO Arguments")
            for arg in topic.pro_arguments:
                emoji = STRENGTH_EMOJIS.get(arg.strength, "⚪")
                st.markdown(f"**{emoji} {arg.point}**")
                st.markdown(f"{arg.explanation}")
                if arg.evidence:
                    st.caption(f"📎 Evidence: {arg.evidence}")
        with col2:
            st.markdown("### ❌ CON Arguments")
            for arg in topic.con_arguments:
                emoji = STRENGTH_EMOJIS.get(arg.strength, "⚪")
                st.markdown(f"**{emoji} {arg.point}**")
                st.markdown(f"{arg.explanation}")
                if arg.evidence:
                    st.caption(f"📎 Evidence: {arg.evidence}")

        if topic.counterargument_pairs:
            with st.expander("⚔️ Counterargument Pairs"):
                for pair in topic.counterargument_pairs:
                    st.markdown(f"**Argument:** {pair.argument}")
                    st.markdown(f"**Counter:** {pair.counterargument}")
                    if pair.rebuttal:
                        st.markdown(f"**Rebuttal:** {pair.rebuttal}")
                    st.divider()

        if topic.judging_criteria:
            with st.expander("📋 Judging Criteria"):
                for c in topic.judging_criteria:
                    st.markdown(f"**{c.criterion}** ({c.weight}%): {c.description}")

        if topic.key_questions:
            with st.expander("❓ Key Questions"):
                for q in topic.key_questions:
                    st.markdown(f"- {q}")

        st.divider()

    st.download_button("📥 Download Topics (JSON)", json.dumps(ds.to_dict(), indent=2),
                       file_name="debate_topics.json", mime="application/json")


def _display_moderator_guide(guide) -> None:
    st.subheader("📋 Moderator Guide")
    st.markdown(f"**Opening Statement:** {guide.opening_statement}")
    st.markdown(f"**Time Allocation:** {guide.time_allocation}")
    if guide.key_questions:
        st.markdown("**Key Questions:**")
        for q in guide.key_questions:
            st.markdown(f"- {q}")
    st.markdown(f"**Closing Instructions:** {guide.closing_instructions}")


if __name__ == "__main__":
    main()
