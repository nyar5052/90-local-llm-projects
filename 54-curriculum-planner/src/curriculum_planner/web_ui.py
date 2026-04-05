#!/usr/bin/env python3
"""
Curriculum Planner Web UI — Streamlit-based interface for curriculum design.
"""

import json
import os
import sys

import streamlit as st
import pandas as pd

# Ensure project root is on path for LLM imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))

from src.curriculum_planner.core import (
    ConfigManager,
    generate_curriculum,
    validate_curriculum_data,
    build_course_design,
    export_curriculum,
    setup_logging,
    OutcomeMapper,
    AssessmentPlanner,
    ResourceSuggester,
    LearningOutcome,
    check_ollama_running,
)

# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Curriculum Planner",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Session state initialization
# ---------------------------------------------------------------------------

if "curriculum_data" not in st.session_state:
    st.session_state.curriculum_data = None
if "course_design" not in st.session_state:
    st.session_state.course_design = None
if "config" not in st.session_state:
    st.session_state.config = ConfigManager()
    setup_logging(st.session_state.config)

cfg = st.session_state.config

# ---------------------------------------------------------------------------
# Sidebar — Course Setup
# ---------------------------------------------------------------------------

with st.sidebar:
    st.header("📚 Course Setup")

    course_name = st.text_input("Course Name", placeholder="e.g., Intro to Machine Learning")
    weeks = st.slider(
        "Duration (weeks)",
        min_value=1,
        max_value=cfg.get("curriculum", "max_weeks", 52),
        value=cfg.get("curriculum", "default_weeks", 12),
    )
    level = st.selectbox(
        "Level",
        options=["beginner", "intermediate", "advanced"],
        index=0,
    )
    focus_areas = st.text_area(
        "Focus Areas (comma-separated)",
        placeholder="e.g., neural networks, NLP, computer vision",
    )

    st.divider()

    # Ollama status
    ollama_running = check_ollama_running()
    if ollama_running:
        st.success("✅ Ollama is running")
    else:
        st.error("❌ Ollama is not running. Start with: `ollama serve`")

    generate_btn = st.button(
        "🚀 Generate Curriculum",
        type="primary",
        disabled=not (course_name and ollama_running),
        use_container_width=True,
    )

    if generate_btn and course_name:
        with st.spinner("Designing curriculum..."):
            try:
                data = generate_curriculum(course_name, weeks, level, focus_areas, cfg=cfg)
                st.session_state.curriculum_data = data
                st.session_state.course_design = build_course_design(data)
                st.success("✅ Curriculum generated!")
            except ValueError as exc:
                st.error(f"Error: {exc}")

    st.divider()

    # Upload existing curriculum
    st.subheader("📂 Load Existing")
    uploaded = st.file_uploader("Upload curriculum JSON", type=["json"])
    if uploaded:
        try:
            data = json.load(uploaded)
            st.session_state.curriculum_data = data
            st.session_state.course_design = build_course_design(data)
            st.success("Loaded curriculum from file!")
        except json.JSONDecodeError:
            st.error("Invalid JSON file")

# ---------------------------------------------------------------------------
# Main content area
# ---------------------------------------------------------------------------

st.title("📚 Curriculum Planner")
st.caption("Design production-grade course curricula with AI-powered planning")

if st.session_state.curriculum_data is None:
    st.info("👈 Configure your course in the sidebar and click **Generate Curriculum** to get started.")
    st.stop()

data = st.session_state.curriculum_data
design = st.session_state.course_design

# Tabs
tab_design, tab_weekly, tab_outcomes, tab_resources, tab_assessment = st.tabs([
    "📋 Course Design",
    "📅 Weekly Breakdown",
    "🎯 Outcome Matrix",
    "📖 Resources",
    "📊 Assessment Plan",
])

# ---------------------------------------------------------------------------
# Tab: Course Design
# ---------------------------------------------------------------------------

with tab_design:
    st.header(data.get("course_title", "Course Curriculum"))

    col1, col2, col3 = st.columns(3)
    col1.metric("Level", data.get("level", "N/A").title())
    col2.metric("Duration", f"{data.get('duration_weeks', '?')} weeks")
    col3.metric("Topics", sum(len(w.get("topics", [])) for w in data.get("weekly_plan", [])))

    st.subheader("Description")
    st.write(data.get("description", "No description available."))

    # Validation
    issues = validate_curriculum_data(data)
    if issues:
        with st.expander("⚠️ Validation Issues"):
            for issue in issues:
                st.warning(issue)

    # Learning Objectives
    if data.get("learning_objectives"):
        st.subheader("🎯 Learning Objectives")
        for i, obj in enumerate(data["learning_objectives"], 1):
            st.markdown(f"{i}. {obj}")

    # Prerequisites
    if data.get("prerequisites"):
        st.subheader("📋 Prerequisites")
        for p in data["prerequisites"]:
            label = p if isinstance(p, str) else p.get("name", str(p))
            st.markdown(f"- {label}")

    # Assessment Strategy
    if data.get("assessment_strategy"):
        st.subheader("📊 Assessment Strategy")
        st.info(data["assessment_strategy"])

    # Export
    st.divider()
    col_json, col_md = st.columns(2)
    with col_json:
        st.download_button(
            "⬇️ Download JSON",
            data=json.dumps(data, indent=2, ensure_ascii=False),
            file_name="curriculum.json",
            mime="application/json",
        )
    with col_md:
        from src.curriculum_planner.core import _curriculum_to_markdown
        st.download_button(
            "⬇️ Download Markdown",
            data=_curriculum_to_markdown(data),
            file_name="curriculum.md",
            mime="text/markdown",
        )

# ---------------------------------------------------------------------------
# Tab: Weekly Breakdown
# ---------------------------------------------------------------------------

with tab_weekly:
    st.header("📅 Weekly Breakdown")

    for week in data.get("weekly_plan", []):
        with st.expander(f"**Week {week.get('week', '?')}: {week.get('title', 'Untitled')}**"):
            col_topics, col_activities = st.columns(2)
            with col_topics:
                st.markdown("**Topics:**")
                for t in week.get("topics", []):
                    st.markdown(f"- {t}")

                if week.get("learning_goals"):
                    st.markdown("**Learning Goals:**")
                    for g in week["learning_goals"]:
                        st.markdown(f"- {g}")

            with col_activities:
                st.markdown("**Activities:**")
                for a in week.get("activities", []):
                    st.markdown(f"- {a}")

                if week.get("assessment"):
                    st.markdown(f"**Assessment:** {week['assessment']}")

# ---------------------------------------------------------------------------
# Tab: Outcome Matrix
# ---------------------------------------------------------------------------

with tab_outcomes:
    st.header("🎯 Outcome-Week Matrix")

    if not design.outcomes:
        for i, obj in enumerate(design.objectives, 1):
            design.outcomes.append(LearningOutcome(id=f"LO-{i}", description=obj))

    if design.outcomes:
        mapper = OutcomeMapper(design.outcomes, design.weekly_plan)
        matrix = mapper.generate_outcome_matrix()
        week_nums = sorted(w.week for w in design.weekly_plan)

        if matrix:
            columns = ["Outcome"] + [f"W{wn}" for wn in week_nums]
            df = pd.DataFrame(matrix, columns=columns)
            st.dataframe(df, use_container_width=True, hide_index=True)

        uncovered = mapper.check_coverage()
        if uncovered:
            st.warning(f"⚠️ {len(uncovered)} outcome(s) not mapped to any week:")
            for o in uncovered:
                st.markdown(f"- **{o.id}**: {o.description}")
        else:
            st.success("✅ All outcomes are covered by at least one week.")
    else:
        st.info("No learning outcomes defined. Add objectives to see the matrix.")

# ---------------------------------------------------------------------------
# Tab: Resources
# ---------------------------------------------------------------------------

with tab_resources:
    st.header("📖 Resources")

    res_list = data.get("resources", [])
    if res_list:
        # Filter by type
        types_available = sorted({r.get("type", "other") for r in res_list})
        selected_types = st.multiselect(
            "Filter by type",
            options=types_available,
            default=types_available,
        )

        for r in res_list:
            rtype = r.get("type", "other")
            if rtype in selected_types:
                with st.container():
                    st.markdown(
                        f"**[{rtype.upper()}]** {r.get('title', 'Untitled')}  \n"
                        f"{r.get('description', '')}"
                    )
                    if r.get("url"):
                        st.markdown(f"🔗 [{r['url']}]({r['url']})")
                    st.divider()
    else:
        st.info("No resources included in this curriculum.")

# ---------------------------------------------------------------------------
# Tab: Assessment Plan
# ---------------------------------------------------------------------------

with tab_assessment:
    st.header("📊 Assessment Plan")

    planner = AssessmentPlanner()
    planned = planner.plan_assessments(design.outcomes, design.weeks)
    planner.calculate_weights()

    # Calendar view
    st.subheader("Assessment Calendar")
    calendar = planner.get_assessment_calendar()
    if calendar:
        cal_df = pd.DataFrame(calendar)
        st.dataframe(cal_df, use_container_width=True, hide_index=True)

    # Weight distribution chart
    st.subheader("Weight Distribution")
    if planned:
        weight_data = pd.DataFrame(
            [{"Assessment": a.name, "Weight (%)": a.weight} for a in planned]
        )
        st.bar_chart(weight_data.set_index("Assessment"))

    if data.get("assessment_strategy"):
        st.subheader("Overall Strategy")
        st.info(data["assessment_strategy"])
