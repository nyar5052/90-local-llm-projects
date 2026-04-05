"""
Quiz Generator Web UI — Streamlit-based interactive interface.

Run with:  streamlit run src/quiz_gen/web_ui.py
"""

import sys
import os
import json
import time

import streamlit as st

# Ensure the common module is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))

from quiz_gen.core import (  # noqa: E402
    generate_quiz,
    score_quiz,
    export_quiz_json,
    export_quiz_pdf_ready,
    validate_quiz_data,
    check_ollama_running,
    ConfigManager,
    QuestionBank,
    QuizResult,
    ScoreTracker,
    QUIZ_TYPES,
)

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------

st.set_page_config(page_title="Quiz Generator", page_icon="📝", layout="wide")

cfg = ConfigManager()

# ---------------------------------------------------------------------------
# Session state initialisation
# ---------------------------------------------------------------------------

if "quiz_data" not in st.session_state:
    st.session_state.quiz_data = None
if "user_answers" not in st.session_state:
    st.session_state.user_answers = {}
if "quiz_submitted" not in st.session_state:
    st.session_state.quiz_submitted = False
if "quiz_start_time" not in st.session_state:
    st.session_state.quiz_start_time = None

# ---------------------------------------------------------------------------
# Sidebar — Quiz settings
# ---------------------------------------------------------------------------

with st.sidebar:
    st.header("⚙️ Quiz Settings")
    topic = st.text_input("Topic", placeholder="e.g. World War II")
    num_questions = st.slider(
        "Number of questions",
        min_value=1,
        max_value=cfg.get("quiz", "max_questions", default=50),
        value=cfg.get("quiz", "default_num_questions", default=5),
    )
    quiz_type = st.selectbox("Question type", QUIZ_TYPES, index=0)
    difficulty = st.select_slider("Difficulty", options=["easy", "medium", "hard"], value="medium")
    enable_timer = st.checkbox("Enable timer", value=False)

    st.divider()
    ollama_ok = check_ollama_running()
    st.metric("Ollama status", "🟢 Running" if ollama_ok else "🔴 Offline")

# ---------------------------------------------------------------------------
# Tabs
# ---------------------------------------------------------------------------

tab_gen, tab_take, tab_bank, tab_history = st.tabs(
    ["📝 Generate Quiz", "🎯 Take Quiz", "🗂️ Question Bank", "📊 Score History"]
)

# ---- Generate Quiz ----

with tab_gen:
    st.header("Generate a Quiz")
    if st.button("🚀 Generate", disabled=not topic, use_container_width=True):
        if not ollama_ok:
            st.error("Ollama is not running. Start it with `ollama serve`.")
        else:
            with st.spinner("Generating quiz…"):
                try:
                    quiz = generate_quiz(topic, num_questions, quiz_type, difficulty, config=cfg)
                    st.session_state.quiz_data = quiz
                    st.session_state.user_answers = {}
                    st.session_state.quiz_submitted = False
                    st.session_state.quiz_start_time = time.time()
                except Exception as exc:
                    st.error(f"Generation failed: {exc}")

    quiz = st.session_state.quiz_data
    if quiz:
        st.subheader(quiz.get("title", "Quiz"))
        st.caption(f"Topic: {quiz.get('topic', 'N/A')}")
        for q in quiz.get("questions", []):
            with st.expander(f"Q{q.get('number', '?')} — {q.get('question', '')[:80]}"):
                st.write(q.get("question", ""))
                if q.get("options"):
                    for opt in q["options"]:
                        st.write(f"  • {opt}")
                with st.container():
                    st.success(f"**Answer:** {q.get('answer', 'N/A')}")
                    if q.get("explanation"):
                        st.info(q["explanation"])

        col1, col2 = st.columns(2)
        with col1:
            json_str = json.dumps(quiz, indent=2, ensure_ascii=False)
            st.download_button("⬇️ Download JSON", json_str, "quiz.json", "application/json")
        with col2:
            md_str = export_quiz_pdf_ready(quiz)
            st.download_button("⬇️ Download Markdown", md_str, "quiz.md", "text/markdown")

# ---- Take Quiz ----

with tab_take:
    st.header("Take the Quiz")
    quiz = st.session_state.quiz_data
    if quiz is None:
        st.info("Generate a quiz first using the **Generate Quiz** tab.")
    else:
        questions = quiz.get("questions", [])

        if enable_timer and st.session_state.quiz_start_time:
            elapsed = time.time() - st.session_state.quiz_start_time
            st.metric("⏱ Elapsed", f"{elapsed:.0f}s")

        with st.form("quiz_form"):
            for q in questions:
                key = f"q_{q.get('number', 0)}"
                st.markdown(f"**Q{q.get('number', '?')}** [{q.get('type', '')}] {q.get('question', '')}")
                if q.get("type") == "multiple-choice" and q.get("options"):
                    st.session_state.user_answers[key] = st.radio(
                        "Select:", q["options"], key=f"radio_{key}", label_visibility="collapsed"
                    )
                elif q.get("type") == "true-false" and q.get("options"):
                    st.session_state.user_answers[key] = st.radio(
                        "Select:", q["options"], key=f"radio_{key}", label_visibility="collapsed"
                    )
                else:
                    st.session_state.user_answers[key] = st.text_input(
                        "Your answer:", key=f"text_{key}", label_visibility="collapsed"
                    )
                st.divider()

            submitted = st.form_submit_button("Submit Answers", use_container_width=True)

        if submitted:
            st.session_state.quiz_submitted = True
            user_ans_list: list[str] = []
            for q in questions:
                key = f"q_{q.get('number', 0)}"
                raw = st.session_state.user_answers.get(key, "")
                # For radio buttons the full option string is returned; extract letter
                if q.get("type") in ("multiple-choice",) and raw and ")" in raw:
                    raw = raw.split(")")[0].strip()
                user_ans_list.append(raw)

            result = score_quiz(questions, user_ans_list)
            result.topic = quiz.get("topic", "")

            color = "🟢" if result.percentage >= 70 else "🟡" if result.percentage >= 50 else "🔴"
            st.markdown(f"### {color} Score: {result.score}/{result.total} ({result.percentage:.0f}%)")

            for q, ua in zip(questions, user_ans_list):
                correct = ua.strip().lower() == q.get("answer", "").strip().lower()
                icon = "✅" if correct else "❌"
                st.write(f"{icon} Q{q.get('number')}: Your answer **{ua}** — Correct answer **{q.get('answer')}**")
                if q.get("explanation"):
                    st.caption(q["explanation"])

            # Persist score
            tracker = ScoreTracker(cfg.get("scoring", "history_file", default="quiz_scores.json"))
            tracker.record(result)

# ---- Question Bank ----

with tab_bank:
    st.header("Question Bank")
    bank_path = cfg.get("question_bank", "storage_file", default="question_bank.json")
    qb = QuestionBank(bank_path)

    col1, col2 = st.columns([3, 1])
    with col1:
        filter_topic = st.text_input("Filter by topic", key="bank_filter")
    with col2:
        if st.button("🗑️ Clear Bank"):
            qb.clear()
            st.rerun()

    quiz = st.session_state.quiz_data
    if quiz and st.button("➕ Add current quiz to bank"):
        added = qb.add_from_quiz(quiz)
        st.success(f"Added {added} questions.")
        st.rerun()

    questions = qb.filter(topic=filter_topic) if filter_topic else qb.all()
    if questions:
        for i, q in enumerate(questions, 1):
            st.markdown(f"**{i}.** [{q.q_type}] {q.question}")
    else:
        st.info("No questions in the bank yet.")

# ---- Score History ----

with tab_history:
    st.header("Score History")
    tracker = ScoreTracker(cfg.get("scoring", "history_file", default="quiz_scores.json"))
    history = tracker.history()

    if history:
        st.metric("Average score", f"{tracker.average_score():.1f}%")
        best = tracker.best_score()
        if best:
            st.metric("Best score", f"{best.get('percentage', 0):.0f}%", delta=best.get("topic", ""))

        chart_data = [{"attempt": i + 1, "percentage": h.get("percentage", 0)} for i, h in enumerate(history)]
        st.line_chart(chart_data, x="attempt", y="percentage")

        if st.button("🗑️ Clear History"):
            tracker.clear()
            st.rerun()
    else:
        st.info("No scores recorded yet. Take a quiz to see your history.")
