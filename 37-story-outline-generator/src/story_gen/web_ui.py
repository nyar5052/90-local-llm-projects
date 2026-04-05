"""Streamlit Web UI for Story Outline Generator."""

import sys
import os
import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))

from story_gen.core import (
    generate_outline,
    generate_character_profile,
    load_config,
    get_character_archetypes,
    get_plot_structures,
    get_worldbuilding_categories,
    visualize_plot_arc,
    DEFAULT_CONFIG,
)

st.set_page_config(page_title="📖 Story Outline Generator", page_icon="📖", layout="wide")


def main():
    st.title("📖 Story Outline Generator")
    st.markdown("*Create detailed story and novel outlines with AI*")

    config = load_config("config.yaml")
    genres = config["story"]["genres"]
    archetypes = get_character_archetypes()
    structures = get_plot_structures()

    tab1, tab2, tab3, tab4 = st.tabs(["🎬 Genre & Premise", "🧑 Character Cards", "📈 Plot Arc", "📚 Chapters"])

    with tab1:
        col1, col2 = st.columns([1, 1])
        with col1:
            st.subheader("Story Setup")
            genre = st.selectbox("Genre", genres)
            premise = st.text_area("Premise / Concept", height=150, placeholder="Describe your story idea...")
            chapters = st.slider("Number of Chapters", 3, 30, 10)
            characters = st.slider("Number of Main Characters", 1, 10, 4)
        with col2:
            st.subheader("Advanced Options")
            structure = st.selectbox("Plot Structure", ["Auto"] + list(structures.keys()),
                                     format_func=lambda x: structures[x]["name"] if x in structures else "Auto-detect")
            worldbuilding = st.checkbox("Include Worldbuilding Details", value=False)
            if structure == "Auto":
                structure = None

        if st.button("🚀 Generate Outline", type="primary", use_container_width=True):
            if not premise:
                st.error("Please enter a story premise.")
            else:
                with st.spinner("Creating your story outline..."):
                    try:
                        result = generate_outline(genre, premise, chapters, characters, structure, worldbuilding, config)
                        st.session_state["outline_result"] = result
                        st.success("Outline generated!")
                    except Exception as e:
                        st.error(f"Error: {e}")

        if "outline_result" in st.session_state:
            st.markdown("---")
            st.markdown(st.session_state["outline_result"])

    with tab2:
        st.subheader("🧑 Character Profile Generator")
        col1, col2 = st.columns(2)
        with col1:
            char_name = st.text_input("Character Name", value="")
            char_role = st.text_input("Role", value="protagonist")
        with col2:
            char_genre = st.selectbox("Genre Context", genres, key="char_genre")
            char_archetype = st.selectbox("Archetype", ["None"] + list(archetypes.keys()),
                                           format_func=lambda x: archetypes[x]["name"] if x in archetypes else "No Archetype")

        if st.button("🎭 Generate Character Profile"):
            if not char_name:
                st.error("Enter a character name.")
            else:
                arch = char_archetype if char_archetype != "None" else None
                with st.spinner("Creating character..."):
                    try:
                        profile = generate_character_profile(char_name, char_role, char_genre, arch, config)
                        st.markdown(profile)
                    except Exception as e:
                        st.error(f"Error: {e}")

        st.markdown("### 🎭 Archetype Reference")
        for key, arch in archetypes.items():
            with st.expander(f"**{arch['name']}** — {arch['description']}"):
                st.markdown(f"**Traits:** {', '.join(arch['traits'])}")

    with tab3:
        st.subheader("📈 Plot Arc Visualization")
        selected_structure = st.selectbox("Structure", list(structures.keys()),
                                           format_func=lambda x: structures[x]["name"], key="arc_structure")
        arc_data = visualize_plot_arc(selected_structure)

        import pandas as pd
        df = pd.DataFrame(arc_data)
        st.line_chart(df.set_index("beat")["tension"])

        st.markdown("### Beat Breakdown")
        for point in arc_data:
            st.markdown(f"**{point['position']}.** {point['beat']} — Tension: {point['tension']}%")

    with tab4:
        st.subheader("📚 Chapter List")
        if "outline_result" in st.session_state:
            st.markdown(st.session_state["outline_result"])
            st.download_button("📄 Download Outline", st.session_state["outline_result"],
                                file_name="story_outline.md", mime="text/markdown")
        else:
            st.info("Generate an outline first to see chapter details.")


if __name__ == "__main__":
    main()
