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

# Custom CSS for professional dark theme
st.set_page_config(page_title="Story Outline Generator", page_icon="🎯", layout="wide")

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
