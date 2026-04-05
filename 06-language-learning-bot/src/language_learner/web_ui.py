"""Streamlit web interface for Language Learning Bot."""

import streamlit as st
from .core import (
    get_response, get_lesson, get_pronunciation_tips, generate_lesson_plan,
    get_vocabulary_quiz, add_vocabulary_word, load_vocabulary,
    load_progress, record_session, check_ollama_running,
    LANGUAGES, LEVELS,
)
from .utils import setup_logging

setup_logging()


def main():
    """Main Streamlit application."""
    st.set_page_config(page_title="🌍 Language Learning Bot", page_icon="🌍", layout="wide")
    st.title("🌍 Language Learning Bot")
    st.caption("Practice conversations in your target language with AI")

    # Sidebar settings
    with st.sidebar:
        st.header("⚙️ Settings")
        language = st.selectbox("Target Language", [l.capitalize() for l in LANGUAGES], index=0)
        language = language.lower()
        level = st.selectbox("Proficiency Level", [l.capitalize() for l in LEVELS], index=0)
        level = level.lower()

        st.divider()
        st.header("📊 Progress")
        progress = load_progress(language)
        sessions = progress.get("sessions", [])
        total_min = progress.get("total_time_minutes", 0)
        vocab_count = len(load_vocabulary(language))
        col1, col2 = st.columns(2)
        col1.metric("Sessions", len(sessions))
        col2.metric("Vocabulary", vocab_count)
        st.metric("Total Time", f"{total_min // 60}h {total_min % 60}m")

        st.divider()
        if not check_ollama_running():
            st.error("❌ Ollama is not running. Start it with: `ollama serve`")
            return

    # Tabs
    tab_chat, tab_vocab, tab_lessons, tab_progress = st.tabs(
        ["💬 Chat", "📖 Vocabulary", "📚 Lessons", "📊 Progress"]
    )

    # --- Chat Tab ---
    with tab_chat:
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
        if "messages" not in st.session_state:
            st.session_state.messages = []

        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        if prompt := st.chat_input(f"Practice {language.capitalize()}..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = get_response(
                        prompt, st.session_state.chat_history, language, level
                    )
                st.markdown(response)

            st.session_state.chat_history.append({"role": "user", "content": prompt})
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            st.session_state.messages.append({"role": "assistant", "content": response})

    # --- Vocabulary Tab ---
    with tab_vocab:
        st.subheader(f"📖 {language.capitalize()} Vocabulary")

        col1, col2, col3 = st.columns(3)
        with col1:
            new_word = st.text_input("Word", key="new_word")
        with col2:
            new_translation = st.text_input("Translation", key="new_trans")
        with col3:
            new_notes = st.text_input("Notes (optional)", key="new_notes")

        if st.button("➕ Add Word") and new_word and new_translation:
            add_vocabulary_word(language, new_word, new_translation, notes=new_notes)
            st.success(f"Added: {new_word} = {new_translation}")
            st.rerun()

        vocab = load_vocabulary(language)
        if vocab:
            st.dataframe(
                [{"Word": v["word"], "Translation": v["translation"],
                  "Notes": v.get("notes", ""), "Added": v["added_date"][:10]}
                 for v in vocab],
                use_container_width=True,
            )

            if st.button("📝 Vocabulary Quiz"):
                with st.spinner("Generating quiz..."):
                    quiz_content = get_vocabulary_quiz(language)
                st.markdown(quiz_content)
        else:
            st.info("No vocabulary words saved yet. Add some above!")

        st.subheader("🗣️ Pronunciation Tips")
        pron_word = st.text_input("Enter a word for pronunciation tips")
        if st.button("Get Tips") and pron_word:
            with st.spinner("Getting pronunciation tips..."):
                tips = get_pronunciation_tips(pron_word, language)
            st.markdown(tips)

    # --- Lessons Tab ---
    with tab_lessons:
        st.subheader("📚 Mini Lessons")
        lesson_topic = st.text_input("Lesson topic (e.g., greetings, food, travel)")
        if st.button("Generate Lesson") and lesson_topic:
            with st.spinner(f"Preparing lesson on {lesson_topic}..."):
                lesson = get_lesson(lesson_topic, language, level)
            st.markdown(lesson)

        st.divider()
        st.subheader("📋 Lesson Plan Generator")
        weeks = st.slider("Plan duration (weeks)", 1, 12, 4)
        if st.button("Generate Lesson Plan"):
            with st.spinner("Creating lesson plan..."):
                plan = generate_lesson_plan(language, level, weeks)
            st.markdown(plan)

    # --- Progress Tab ---
    with tab_progress:
        st.subheader("📊 Learning Progress")
        progress = load_progress(language)
        sessions = progress.get("sessions", [])

        if sessions:
            st.metric("Total Sessions", len(sessions))
            st.metric("Total Time", f"{progress.get('total_time_minutes', 0)} minutes")

            st.subheader("Recent Sessions")
            st.dataframe(
                [{"Date": s["date"][:10], "Level": s["level"],
                  "Duration": f"{s['duration_minutes']}m", "Topic": s.get("topic", "N/A")}
                 for s in sessions[-20:]],
                use_container_width=True,
            )
        else:
            st.info("No sessions recorded yet. Start a chat to track progress!")


if __name__ == "__main__":
    main()
