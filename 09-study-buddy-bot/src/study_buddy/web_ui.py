"""Streamlit web interface for Study Buddy Bot."""

import time
import streamlit as st
from .core import (
    generate_quiz, explain_concept, create_study_plan, generate_flashcards,
    ask_question, record_study_session, get_study_stats,
    load_saved_flashcards, check_ollama_running,
    MODES,
)
from .utils import setup_logging

setup_logging()


def main():
    """Main Streamlit application."""
    # Custom CSS for professional dark theme
    st.set_page_config(page_title="Study Buddy Bot", page_icon="🎯", layout="wide")

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
    st.title("📚 Study Buddy Bot")
    st.caption("Your AI exam preparation assistant")

    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")
        subject = st.text_input("Subject", value="Biology")
        topic = st.text_input("Topic", value="Cell Division")
        mode = st.selectbox("Study Mode", list(MODES.keys()),
                            format_func=lambda x: f"{x.capitalize()} - {MODES[x]}")

        st.divider()
        st.header("📊 Quick Stats")
        stats = get_study_stats()
        col1, col2 = st.columns(2)
        col1.metric("Sessions", stats["total_sessions"])
        col2.metric("Hours", stats["total_hours"])

        st.divider()
        if not check_ollama_running():
            st.error("❌ Ollama is not running")
            return

    tab_study, tab_quiz, tab_flashcards, tab_timer, tab_progress = st.tabs(
        ["📖 Study", "📝 Quiz", "🃏 Flashcards", "⏱️ Timer", "📊 Progress"]
    )

    # --- Study Tab ---
    with tab_study:
        col1, col2 = st.columns([3, 1])
        with col1:
            if st.button("🎓 Start Study Session", type="primary"):
                with st.spinner(f"Preparing {mode}..."):
                    if mode == "quiz":
                        result = generate_quiz(subject, topic)
                    elif mode == "explain":
                        result = explain_concept(subject, topic)
                    elif mode == "plan":
                        result = create_study_plan(subject, topic)
                    elif mode == "summarize":
                        result = explain_concept(subject, topic, depth="summary")
                    elif mode == "flashcards":
                        result = generate_flashcards(subject, topic)
                    else:
                        result = "Unknown mode"
                st.markdown(result)
                record_study_session(subject, topic, mode, 5)

        # Interactive Q&A
        if "study_history" not in st.session_state:
            st.session_state.study_history = []
        if "study_messages" not in st.session_state:
            st.session_state.study_messages = []

        st.divider()
        st.subheader("❓ Ask Follow-up Questions")

        for msg in st.session_state.study_messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        if q := st.chat_input("Ask a question about the topic..."):
            st.session_state.study_messages.append({"role": "user", "content": q})
            with st.chat_message("user"):
                st.markdown(q)

            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    answer = ask_question(subject, topic, q, st.session_state.study_history)
                st.markdown(answer)

            st.session_state.study_history.append({"role": "user", "content": q})
            st.session_state.study_history.append({"role": "assistant", "content": answer})
            st.session_state.study_messages.append({"role": "assistant", "content": answer})

    # --- Quiz Tab ---
    with tab_quiz:
        st.subheader("📝 Quiz Mode")
        num_questions = st.slider("Number of questions", 3, 15, 5)
        if st.button("Generate Quiz"):
            with st.spinner("Generating quiz..."):
                quiz = generate_quiz(subject, topic, num_questions)
            st.markdown(quiz)
            record_study_session(subject, topic, "quiz", 5)

    # --- Flashcards Tab ---
    with tab_flashcards:
        st.subheader("🃏 Flashcards")
        card_count = st.slider("Number of flashcards", 5, 20, 10)
        if st.button("Generate Flashcards"):
            with st.spinner("Creating flashcards..."):
                cards = generate_flashcards(subject, topic, card_count)
            st.markdown(cards)

        saved = load_saved_flashcards()
        if saved:
            st.divider()
            st.subheader("📦 Saved Flashcard Sets")
            st.dataframe(
                [{"Subject": d["subject"], "Topic": d["topic"],
                  "Cards": len(d.get("cards", [])), "Created": d["created_date"][:10]}
                 for d in saved.values()],
                use_container_width=True,
            )

    # --- Timer Tab ---
    with tab_timer:
        st.subheader("⏱️ Pomodoro Study Timer")
        timer_minutes = st.slider("Session duration (minutes)", 5, 60, 25)
        if "timer_running" not in st.session_state:
            st.session_state.timer_running = False

        if st.button("▶️ Start Timer"):
            st.session_state.timer_running = True
            placeholder = st.empty()
            for remaining in range(timer_minutes * 60, 0, -1):
                if not st.session_state.timer_running:
                    break
                mins, secs = divmod(remaining, 60)
                placeholder.markdown(f"## ⏱️ {mins:02d}:{secs:02d}")
                time.sleep(1)
            placeholder.markdown("## 🎉 Time's up!")
            st.success(f"Great session! You studied for {timer_minutes} minutes.")
            record_study_session(subject, topic, "timed", timer_minutes)

    # --- Progress Tab ---
    with tab_progress:
        st.subheader("📊 Study Progress")
        stats = get_study_stats()
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Sessions", stats["total_sessions"])
        col2.metric("Total Hours", stats["total_hours"])
        col3.metric("Subjects", len(stats.get("subjects", {})))

        subjects = stats.get("subjects", {})
        if subjects:
            st.subheader("Subject Breakdown")
            st.dataframe(
                [{"Subject": k.capitalize(), "Sessions": v["session_count"],
                  "Minutes": v["total_minutes"], "Topics": ", ".join(v.get("topics", [])[:3])}
                 for k, v in subjects.items()],
                use_container_width=True,
            )


if __name__ == "__main__":
    main()
