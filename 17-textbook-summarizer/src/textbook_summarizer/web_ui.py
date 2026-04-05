"""Streamlit web interface for the Textbook Summarizer."""

import streamlit as st

from .core import (
    read_chapter_file,
    detect_chapter_info,
    summarize_chapter,
    generate_glossary,
    generate_concept_map,
    generate_study_questions,
    STYLE_PROMPTS,
)
from .config import load_config
from .utils import setup_sys_path, count_words, split_chapters

setup_sys_path()
from common.llm_client import check_ollama_running


def run():
    """Launch the Streamlit web UI."""
    config = load_config()

    # Custom CSS for professional dark theme
    st.set_page_config(page_title="Textbook Summarizer", page_icon="🎯", layout="wide")

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
    st.title("📚 Textbook Summarizer")
    st.markdown("Generate structured summaries with concept maps, glossaries, and study questions.")

    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")

        if check_ollama_running():
            st.success("✅ Ollama is running")
        else:
            st.error("❌ Ollama is not running. Start with: `ollama serve`")
            return

        style = st.selectbox("Summary Style", options=list(STYLE_PROMPTS.keys()), index=0)

        st.subheader("Summary Depth")
        depth = st.slider("Detail Level", min_value=1, max_value=10, value=5,
                          help="1=Brief, 10=Very detailed")

        st.subheader("Study Aids")
        show_glossary = st.checkbox("Generate Glossary", value=True)
        show_concept_map = st.checkbox("Generate Concept Map", value=True)
        show_quiz = st.checkbox("Generate Study Questions", value=True)
        num_questions = st.number_input("Number of Questions", min_value=3, max_value=15, value=5)

    # Main content
    st.subheader("📁 Chapter Upload")
    uploaded_file = st.file_uploader("Upload a text file", type=["txt", "md"])

    if uploaded_file is not None:
        text = uploaded_file.read().decode("utf-8")
        word_count = count_words(text)
        chapter_info = detect_chapter_info(text)

        col1, col2, col3 = st.columns(3)
        col1.metric("Words", f"{word_count:,}")
        col2.metric("Chapter", chapter_info)
        col3.metric("Style", style.title())

        with st.expander("📄 Chapter Preview", expanded=False):
            st.text(text[:2000])

        # Detect chapters
        chapters = split_chapters(text)
        if len(chapters) > 1:
            st.info(f"Detected {len(chapters)} chapters")
            selected_chapter = st.selectbox(
                "Select chapter",
                options=[c["title"] for c in chapters],
            )
            chapter_text = next(c["content"] for c in chapters if c["title"] == selected_chapter)
        else:
            chapter_text = text

        if st.button("🚀 Generate Summary", type="primary", use_container_width=True):
            with st.spinner(f"Generating {style} summary..."):
                summary = summarize_chapter(chapter_text, style=style, config=config)

            st.success("✅ Summary generated!")
            st.markdown("---")
            st.subheader("📝 Summary")
            st.markdown(summary)

            # Concept map
            if show_concept_map:
                with st.spinner("Generating concept map..."):
                    concept_text = generate_concept_map(chapter_text, config=config)
                st.markdown("---")
                st.subheader("🗺️ Concept Map")
                st.markdown(concept_text)

            # Glossary
            if show_glossary:
                with st.spinner("Generating glossary..."):
                    glossary_text = generate_glossary(chapter_text, config=config)
                st.markdown("---")
                st.subheader("📖 Key Terms Glossary")
                st.markdown(glossary_text)

            # Quiz
            if show_quiz:
                with st.spinner(f"Generating {num_questions} study questions..."):
                    quiz_text = generate_study_questions(chapter_text, num_questions=int(num_questions), config=config)
                st.markdown("---")
                st.subheader("❓ Study Questions")
                st.markdown(quiz_text)

            # Download
            st.download_button(
                "📥 Download Summary",
                data=summary,
                file_name=f"summary_{style}.md",
                mime="text/markdown",
            )
    else:
        st.info("👆 Upload a textbook chapter file to get started.")


if __name__ == "__main__":
    run()
