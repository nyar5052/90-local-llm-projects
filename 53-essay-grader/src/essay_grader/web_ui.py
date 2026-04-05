#!/usr/bin/env python3
"""
Essay Grader Web UI — Streamlit-based interface for essay grading.
"""

import json
from datetime import datetime
from pathlib import Path

import streamlit as st

from src.essay_grader.core import (
    check_ollama_running,
    grade_essay,
    generate_annotations,
    check_plagiarism_indicators,
    export_grade_report,
    calculate_grade_letter,
    validate_grade_data,
    PRESET_RUBRICS,
    Rubric,
    RubricCriterion,
    GradeDistribution,
    ConfigManager,
    setup_logging,
)

# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Essay Grader",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Session state defaults
# ---------------------------------------------------------------------------

if "grade_history" not in st.session_state:
    st.session_state.grade_history = []
if "custom_rubrics" not in st.session_state:
    st.session_state.custom_rubrics = {}
if "distribution" not in st.session_state:
    st.session_state.distribution = GradeDistribution()

cfg = ConfigManager.get_instance()
setup_logging(level=cfg.get("logging", "level", default="INFO"))

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

with st.sidebar:
    st.title("📝 Essay Grader")
    st.markdown("---")

    # Rubric selector
    st.subheader("Rubric")
    all_rubrics = {**PRESET_RUBRICS, **st.session_state.custom_rubrics}
    rubric_names = list(all_rubrics.keys())
    selected_rubric_name = st.selectbox("Select rubric preset", rubric_names, index=0)
    selected_rubric = all_rubrics[selected_rubric_name]

    st.markdown(f"*{selected_rubric.description}*")
    with st.expander("Criteria details"):
        for c in selected_rubric.criteria:
            st.markdown(f"- **{c.name.replace('_', ' ').title()}** (weight {c.weight}) — {c.description}")

    st.markdown("---")

    # Grading options
    st.subheader("Options")
    temperature = st.slider("Temperature", 0.0, 1.0, 0.3, 0.05)
    enable_annotations = st.checkbox("Inline annotations", value=True)
    enable_plagiarism = st.checkbox("Plagiarism check", value=cfg.get("plagiarism", "enabled", default=True))
    context = st.text_area("Assignment context (optional)", height=80)

    st.markdown("---")
    ollama_ok = check_ollama_running()
    if ollama_ok:
        st.success("✅ Ollama is running")
    else:
        st.error("❌ Ollama is not running — start with `ollama serve`")

# ---------------------------------------------------------------------------
# Tabs
# ---------------------------------------------------------------------------

tab_grade, tab_rubric, tab_history, tab_analytics = st.tabs(
    ["Grade Essay", "Rubric Builder", "Grade History", "Analytics"]
)

# ========================== Grade Essay ==========================

with tab_grade:
    st.header("Grade Essay")

    input_method = st.radio("Input method", ["Paste text", "Upload file"], horizontal=True)

    essay_text = ""
    if input_method == "Paste text":
        essay_text = st.text_area("Paste your essay here", height=300)
    else:
        uploaded = st.file_uploader("Upload essay (.txt / .md)", type=["txt", "md"])
        if uploaded is not None:
            essay_text = uploaded.read().decode("utf-8")
            st.text_area("Essay preview", essay_text, height=200, disabled=True)

    col_btn, col_info = st.columns([1, 3])
    with col_btn:
        grade_btn = st.button("🎓 Grade Essay", type="primary", disabled=not ollama_ok)
    with col_info:
        if not ollama_ok:
            st.warning("Start Ollama to enable grading.")

    if grade_btn and essay_text.strip():
        with st.spinner("Grading essay..."):
            grade_data = grade_essay(
                essay_text,
                rubric=selected_rubric,
                context=context,
                temperature=temperature,
            )

        # --- Display results ---
        overall = grade_data.get("overall_score", 0)
        letter = grade_data.get("overall_grade", calculate_grade_letter(overall))
        color = "🟢" if overall >= 7 else "🟡" if overall >= 5 else "🔴"

        st.subheader(f"{color} Overall: {overall}/10 ({letter})")

        # Score breakdown
        st.markdown("### Rubric Scores")
        criteria = grade_data.get("criteria", [])
        if criteria:
            cols = st.columns(min(len(criteria), 5))
            for idx, c in enumerate(criteria):
                with cols[idx % len(cols)]:
                    st.metric(
                        c.get("name", "").replace("_", " ").title(),
                        f"{c.get('score', 0)}/{c.get('max_score', 10)}",
                    )
            for c in criteria:
                with st.expander(c.get("name", "").replace("_", " ").title()):
                    st.write(c.get("feedback", ""))

        # Strengths / Weaknesses / Suggestions
        col_s, col_w, col_sg = st.columns(3)
        with col_s:
            st.markdown("#### ✅ Strengths")
            for s in grade_data.get("strengths", []):
                st.markdown(f"- {s}")
        with col_w:
            st.markdown("#### ❌ Weaknesses")
            for w in grade_data.get("weaknesses", []):
                st.markdown(f"- {w}")
        with col_sg:
            st.markdown("#### 💡 Suggestions")
            for s in grade_data.get("suggestions", []):
                st.markdown(f"- {s}")

        if grade_data.get("summary"):
            st.info(grade_data["summary"])

        # Annotations
        if enable_annotations:
            with st.spinner("Generating annotations..."):
                annotations = generate_annotations(essay_text, temperature=temperature)
            if annotations:
                st.markdown("### 📌 Inline Annotations")
                for a in annotations:
                    icon = {"error": "🔴", "warning": "🟡"}.get(a.severity, "🔵")
                    st.markdown(f'{icon} **[{a.annotation_type}]** "{a.text_segment[:80]}..." — {a.comment}')

        # Plagiarism
        if enable_plagiarism:
            with st.spinner("Checking plagiarism indicators..."):
                plag = check_plagiarism_indicators(essay_text, temperature=temperature)
            st.markdown("### 🔍 Plagiarism Check")
            plag_color = "🟢" if plag.score < 0.3 else "🟡" if plag.score < 0.7 else "🔴"
            st.markdown(f"{plag_color} **Score:** {plag.score:.2f}")
            st.write(plag.explanation)
            if plag.suspicious_passages:
                with st.expander("Suspicious passages"):
                    for p in plag.suspicious_passages:
                        st.markdown(f"- {p}")

        # Download report
        report_json = json.dumps(grade_data, indent=2, ensure_ascii=False)
        st.download_button(
            "📥 Download JSON Report",
            data=report_json,
            file_name="essay_grade.json",
            mime="application/json",
        )

        # Save to history
        st.session_state.grade_history.append({
            "timestamp": datetime.now().isoformat(),
            "rubric": selected_rubric_name,
            "overall_score": overall,
            "grade_letter": letter,
            "data": grade_data,
        })
        st.session_state.distribution.add_score(overall)

# ========================== Rubric Builder ==========================

with tab_rubric:
    st.header("Rubric Builder")
    st.markdown("Create a custom rubric with your own criteria.")

    rubric_name = st.text_input("Rubric name", placeholder="my_custom_rubric")
    rubric_desc = st.text_input("Description", placeholder="Custom rubric for...")
    num_criteria = st.number_input("Number of criteria", min_value=1, max_value=20, value=3)

    custom_criteria: list[RubricCriterion] = []
    for i in range(int(num_criteria)):
        st.markdown(f"**Criterion {i+1}**")
        c1, c2, c3, c4 = st.columns([2, 1, 1, 3])
        with c1:
            cname = st.text_input(f"Name##c{i}", key=f"cname_{i}")
        with c2:
            cweight = st.number_input(f"Weight##c{i}", 0.1, 5.0, 1.0, 0.1, key=f"cw_{i}")
        with c3:
            cmaxs = st.number_input(f"Max##c{i}", 1, 100, 10, key=f"cms_{i}")
        with c4:
            cdesc = st.text_input(f"Description##c{i}", key=f"cdsc_{i}")
        if cname:
            custom_criteria.append(RubricCriterion(cname, cweight, int(cmaxs), cdesc))

    if st.button("💾 Save Rubric") and rubric_name and custom_criteria:
        new_rubric = Rubric(rubric_name, custom_criteria, rubric_desc)
        st.session_state.custom_rubrics[rubric_name] = new_rubric
        st.success(f"Rubric '{rubric_name}' saved with {len(custom_criteria)} criteria!")
        st.rerun()

# ========================== Grade History ==========================

with tab_history:
    st.header("Grade History")

    history = st.session_state.grade_history
    if not history:
        st.info("No grading history yet. Grade an essay to see results here.")
    else:
        for idx, entry in enumerate(reversed(history)):
            color = "🟢" if entry["overall_score"] >= 7 else "🟡" if entry["overall_score"] >= 5 else "🔴"
            with st.expander(
                f'{color} {entry["timestamp"][:16]} — {entry["overall_score"]}/10 '
                f'({entry["grade_letter"]}) [{entry["rubric"]}]'
            ):
                st.json(entry["data"])

# ========================== Analytics ==========================

with tab_analytics:
    st.header("Analytics")

    dist = st.session_state.distribution
    if dist.count == 0:
        st.info("No data yet. Grade some essays to see analytics.")
    else:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Essays Graded", dist.count)
        with col2:
            st.metric("Mean Score", f"{dist.mean:.2f}")
        with col3:
            st.metric("Median Score", f"{dist.median:.2f}")
        with col4:
            st.metric("Std Dev", f"{dist.std:.2f}")

        st.markdown("### Grade Distribution")
        import pandas as pd
        df = pd.DataFrame({"Score": dist.scores})
        st.bar_chart(df["Score"].value_counts().sort_index())

        # Criterion averages across history
        if history:
            all_criteria: dict[str, list[float]] = {}
            for entry in history:
                for c in entry["data"].get("criteria", []):
                    name = c.get("name", "")
                    score = c.get("score", 0)
                    all_criteria.setdefault(name, []).append(score)
            if all_criteria:
                st.markdown("### Criterion Averages")
                avg_data = {
                    k.replace("_", " ").title(): round(sum(v) / len(v), 2)
                    for k, v in all_criteria.items()
                }
                st.bar_chart(avg_data)
