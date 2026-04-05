"""Streamlit Web UI for Reading Comprehension Builder."""

import streamlit as st

# Custom CSS for professional dark theme
st.set_page_config(page_title="Reading Comprehension Builder", page_icon="🎯", layout="wide")

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
    generate_comprehension,
    score_exercise,
    get_answer_key,
    check_service,
    ReadingExercise,
    DEFAULT_RUBRIC,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    st.title("📚 Reading Comprehension Builder")
    st.caption("Powered by Local LLM — Interactive reading exercises with scoring")

    if not check_service():
        st.error("⚠️ Ollama is not running. Start it with: `ollama serve`")
        return

    if "exercise" not in st.session_state:
        st.session_state.exercise = None
    if "score_result" not in st.session_state:
        st.session_state.score_result = None

    tab_generate, tab_exercise, tab_score = st.tabs(
        ["📝 Generate Exercise", "📖 Take Exercise", "📊 Score & Review"]
    )

    # ------------------------------------------------------------------
    # Tab 1: Generate
    # ------------------------------------------------------------------
    with tab_generate:
        col1, col2 = st.columns([3, 1])
        with col1:
            topic = st.text_input("Topic", placeholder="e.g., Climate Change, Space Exploration")
        with col2:
            level = st.selectbox("Reading level", ["elementary", "middle school", "high school", "college"])

        col3, col4, col5 = st.columns(3)
        with col3:
            num_questions = st.slider("Questions", 3, 10, 5)
        with col4:
            passage_length = st.selectbox("Passage length", ["short", "medium", "long"])
        with col5:
            show_answers = st.checkbox("Show answers immediately")

        if st.button("🚀 Generate Exercise", type="primary", use_container_width=True):
            if topic.strip():
                with st.spinner("Building exercise..."):
                    try:
                        ex = generate_comprehension(topic, level, num_questions, passage_length)
                        st.session_state.exercise = ex
                        st.session_state.score_result = None
                    except Exception as e:
                        st.error(f"Error: {e}")

        if st.session_state.exercise:
            _display_exercise(st.session_state.exercise, show_answers)

    # ------------------------------------------------------------------
    # Tab 2: Interactive Exercise
    # ------------------------------------------------------------------
    with tab_exercise:
        if st.session_state.exercise is None:
            st.info("Generate an exercise first!")
        else:
            ex = st.session_state.exercise
            st.subheader(f"📖 {ex.title}")
            st.markdown(ex.passage)

            if ex.vocabulary_words:
                with st.expander("📝 Key Vocabulary"):
                    for v in ex.vocabulary_words:
                        st.markdown(f"**{v.word}**: {v.definition}")

            st.divider()
            st.subheader("❓ Answer the Questions")

            user_answers = {}
            for q in ex.questions:
                st.markdown(f"**Q{q.number}** [{q.type}] ({q.difficulty})")
                st.markdown(f"{q.question}")

                options = ["Select answer..."] + q.options
                choice = st.selectbox(
                    f"Answer for Q{q.number}",
                    options,
                    key=f"answer_{q.number}",
                    label_visibility="collapsed",
                )
                if choice != "Select answer...":
                    user_answers[q.number] = choice[0]  # Get letter (A, B, C, D)

            if st.button("📝 Submit Answers", type="primary", use_container_width=True):
                if len(user_answers) < len(ex.questions):
                    st.warning("Please answer all questions before submitting.")
                else:
                    result = score_exercise(ex, user_answers)
                    st.session_state.score_result = result
                    st.rerun()

    # ------------------------------------------------------------------
    # Tab 3: Score & Review
    # ------------------------------------------------------------------
    with tab_score:
        if st.session_state.score_result is None:
            st.info("Take the exercise first to see your score!")
        else:
            result = st.session_state.score_result
            _display_score(result)

            if st.session_state.exercise:
                with st.expander("📋 Full Answer Key"):
                    key = get_answer_key(st.session_state.exercise)
                    for item in key:
                        st.markdown(f"**Q{item['number']}** [{item['type']}]: {item['question']}")
                        st.markdown(f"✅ **Answer:** {item['answer']}")
                        st.markdown(f"📝 {item['explanation']}")
                        if item.get("annotation"):
                            st.caption(f"📎 Passage reference: {item['annotation']}")
                        st.divider()


# ---------------------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------------------


def _display_exercise(ex: ReadingExercise, show_answers: bool) -> None:
    st.divider()
    col1, col2, col3 = st.columns(3)
    col1.metric("Reading Level", ex.reading_level.title())
    col2.metric("Word Count", f"~{ex.word_count}")
    col3.metric("Questions", len(ex.questions))

    st.subheader(f"📖 {ex.title}")
    st.markdown(ex.passage)

    if ex.vocabulary_words:
        with st.expander("📝 Key Vocabulary"):
            for v in ex.vocabulary_words:
                st.markdown(f"**{v.word}**: {v.definition}")

    st.subheader("❓ Questions")
    for q in ex.questions:
        with st.expander(f"Q{q.number} [{q.type}] ({q.difficulty})", expanded=False):
            st.markdown(q.question)
            for opt in q.options:
                st.markdown(f"  {opt}")
            if show_answers:
                st.success(f"✅ Answer: {q.answer}")
                st.info(f"📝 {q.explanation}")

    if show_answers and ex.summary:
        st.subheader("📋 Summary")
        st.markdown(ex.summary)

    st.download_button("📥 Download Exercise (JSON)", json.dumps(ex.to_dict(), indent=2),
                       file_name="reading_exercise.json", mime="application/json")


def _display_score(result: dict) -> None:
    pct = result["percentage"]
    color = "🟢" if pct >= 70 else "🟡" if pct >= 50 else "🔴"

    st.markdown(f"### {color} Score: {result['score']}/{result['total']} ({pct:.0f}%)")
    st.markdown(f"**Level:** {result.get('level', 'N/A')}")
    st.markdown(f"**Feedback:** {result.get('feedback', '')}")

    st.divider()
    for d in result.get("details", []):
        if d["correct"]:
            st.success(f"Q{d['number']}: ✅ Correct ({d['correct_answer']})")
        else:
            st.error(f"Q{d['number']}: ❌ Your answer: {d['user_answer']} | Correct: {d['correct_answer']}")
            st.info(f"📝 {d['explanation']}")


if __name__ == "__main__":
    main()
