"""Streamlit Web UI for Vocabulary Builder."""

import streamlit as st

# Custom CSS for professional dark theme
st.set_page_config(page_title="Vocabulary Builder", page_icon="🎯", layout="wide")

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
    generate_vocabulary,
    load_vocab_file,
    run_quiz,
    score_quiz,
    create_spaced_repetition_deck,
    check_service,
    VocabularySet,
    ProgressStats,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    st.title("📖 Vocabulary Builder")
    st.caption("Powered by Local LLM — Learn, Quiz & Track Progress")

    if not check_service():
        st.error("⚠️ Ollama is not running. Start it with: `ollama serve`")
        return

    if "vocab_set" not in st.session_state:
        st.session_state.vocab_set = None
    if "quiz_data" not in st.session_state:
        st.session_state.quiz_data = None
    if "progress" not in st.session_state:
        st.session_state.progress = ProgressStats()

    tab_learn, tab_quiz, tab_cards, tab_progress = st.tabs(
        ["📚 Learn Mode", "🎯 Quiz Mode", "🃏 Word Cards", "📊 Progress"]
    )

    # ------------------------------------------------------------------
    # Tab 1: Learn Mode
    # ------------------------------------------------------------------
    with tab_learn:
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            topic = st.text_input("Topic", placeholder="e.g., SAT words, medical terminology")
        with col2:
            count = st.slider("Number of words", 3, 20, 10)
        with col3:
            level = st.selectbox("Level", ["", "beginner", "intermediate", "advanced", "GRE", "SAT"])

        if st.button("📚 Generate Vocabulary", type="primary", use_container_width=True):
            if topic.strip():
                with st.spinner("Building vocabulary..."):
                    try:
                        vs = generate_vocabulary(topic, count, level)
                        st.session_state.vocab_set = vs
                        st.session_state.progress.total_words += len(vs.words)
                    except Exception as e:
                        st.error(f"Error: {e}")

        if st.session_state.vocab_set:
            _display_word_list(st.session_state.vocab_set)

    # ------------------------------------------------------------------
    # Tab 2: Quiz Mode
    # ------------------------------------------------------------------
    with tab_quiz:
        if st.session_state.vocab_set is None:
            st.info("Generate vocabulary in Learn Mode first!")
        else:
            vs = st.session_state.vocab_set
            quiz_data = run_quiz(vs.words)

            st.subheader(f"🎯 Quiz: {vs.topic} ({quiz_data['total']} words)")

            answers = []
            for i, q in enumerate(quiz_data["questions"]):
                st.markdown(f"**Q{i+1}.** {q['definition']} *({q['part_of_speech']})*")
                user_answer = st.text_input(f"Your answer", key=f"quiz_{i}", placeholder="Type the word...")
                answers.append({"word": q["word"], "user_answer": user_answer})

            if st.button("📝 Submit Quiz", use_container_width=True):
                result = score_quiz(answers)
                st.session_state.progress.quiz_scores.append(result["percentage"])
                color = "🟢" if result["percentage"] >= 80 else "🟡" if result["percentage"] >= 60 else "🔴"
                st.markdown(f"### {color} Score: {result['score']}/{result['total']} ({result['percentage']:.0f}%)")

                for i, (q, a) in enumerate(zip(quiz_data["questions"], answers)):
                    is_correct = a["user_answer"].lower() == q["word"].lower()
                    if is_correct:
                        st.success(f"Q{i+1}: ✅ Correct — {q['word']}")
                    else:
                        st.error(f"Q{i+1}: ❌ Your answer: '{a['user_answer']}' | Correct: **{q['word']}**")
                        if q.get("mnemonic"):
                            st.info(f"💡 Mnemonic: {q['mnemonic']}")

    # ------------------------------------------------------------------
    # Tab 3: Word Cards
    # ------------------------------------------------------------------
    with tab_cards:
        if st.session_state.vocab_set is None:
            st.info("Generate vocabulary in Learn Mode first!")
        else:
            vs = st.session_state.vocab_set
            st.subheader("🃏 Flashcard View")
            for i, w in enumerate(vs.words):
                with st.expander(f"📝 Card {i+1}: Click to reveal", expanded=False):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"### {w.word}")
                        st.markdown(f"*{w.part_of_speech}*")
                        if w.etymology:
                            st.caption(f"Etymology: {w.etymology}")
                    with col2:
                        st.markdown(f"**Definition:** {w.definition}")
                        st.markdown(f'**Example:** *"{w.example_sentence}"*')
                        if w.synonyms:
                            st.markdown(f"**Synonyms:** {', '.join(w.synonyms)}")
                        if w.word_family:
                            st.markdown(f"**Word Family:** {', '.join(w.word_family)}")

    # ------------------------------------------------------------------
    # Tab 4: Progress Dashboard
    # ------------------------------------------------------------------
    with tab_progress:
        stats = st.session_state.progress
        st.subheader("📊 Progress Dashboard")
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Words Studied", stats.total_words)
        col2.metric("Quiz Average", f"{stats.avg_score:.0f}%")
        col3.metric("Quizzes Taken", len(stats.quiz_scores))

        if stats.quiz_scores:
            st.line_chart(stats.quiz_scores)


# ---------------------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------------------


def _display_word_list(vs: VocabularySet) -> None:
    st.divider()
    st.subheader(f"📖 {vs.topic} — {vs.level}")

    for w in vs.words:
        with st.expander(f"**{w.word}** ({w.part_of_speech}) — {w.difficulty}", expanded=False):
            st.markdown(f"**Definition:** {w.definition}")
            st.markdown(f'**Example:** *"{w.example_sentence}"*')
            if w.etymology:
                st.markdown(f"**Etymology:** {w.etymology}")
            if w.synonyms:
                st.markdown(f"**Synonyms:** {', '.join(w.synonyms)}")
            if w.antonyms:
                st.markdown(f"**Antonyms:** {', '.join(w.antonyms)}")
            if w.word_family:
                st.markdown(f"**Word Family:** {', '.join(w.word_family)}")
            if w.context_sentences:
                st.markdown("**Context Sentences:**")
                for s in w.context_sentences:
                    st.markdown(f'- *"{s}"*')
            if w.mnemonic:
                st.info(f"💡 **Mnemonic:** {w.mnemonic}")

    st.download_button("📥 Download Vocabulary (JSON)", json.dumps(vs.to_dict(), indent=2),
                       file_name=f"vocab_{vs.topic.lower().replace(' ', '_')}.json",
                       mime="application/json")


if __name__ == "__main__":
    main()
