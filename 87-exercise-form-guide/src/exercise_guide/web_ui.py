"""
Exercise Form Guide - Streamlit Web UI.

Provides a browser-based interface for exercise guidance, muscle group info,
progression paths, and warm-up/cool-down routines.

⚠️  DISCLAIMER: This tool is for educational purposes only and is NOT medical advice.
"""

import streamlit as st

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from exercise_guide.core import (
    DISCLAIMER,
    VALID_LEVELS,
    VALID_MUSCLE_GROUPS,
    VALID_GOALS,
    MUSCLE_GROUP_DATABASE,
    PROGRESSION_PATHS,
    check_ollama_running,
    generate_guide,
    list_exercises,
    generate_routine,
    get_warmup_routine,
    get_cooldown_routine,
    get_exercise_variations,
    get_muscle_info,
)

# ---------------------------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Exercise Form Guide",
    page_icon="🏋️",
    layout="wide",
)

# ---------------------------------------------------------------------------
# Disclaimer
# ---------------------------------------------------------------------------

st.warning(
    "⚠️ **DISCLAIMER**: This tool provides AI-generated exercise guidance for "
    "**educational purposes only**. It is **NOT medical advice**. Always consult "
    "a qualified fitness professional or physician before starting any exercise "
    "program. Improper form can lead to serious injury."
)

# ---------------------------------------------------------------------------
# Sidebar Navigation
# ---------------------------------------------------------------------------

st.sidebar.title("🏋️ Exercise Form Guide")
page = st.sidebar.radio(
    "Navigate",
    [
        "🏋️ Exercise Guide",
        "💪 Muscle Groups",
        "📈 Progression Paths",
        "🔥 Warm-up/Cool-down",
    ],
)

# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------

if page == "🏋️ Exercise Guide":
    st.title("🏋️ Exercise Form Guide")
    st.markdown("Get detailed, AI-powered form instructions for any exercise.")

    col1, col2 = st.columns(2)
    with col1:
        exercise = st.text_input("Exercise Name", placeholder="e.g., deadlift, bench press, squat")
    with col2:
        level = st.selectbox("Experience Level", VALID_LEVELS)

    if st.button("🔍 Get Form Guide", type="primary"):
        if not exercise.strip():
            st.error("Please enter an exercise name.")
        elif not check_ollama_running():
            st.error("Ollama is not running. Please start Ollama first.")
        else:
            with st.spinner("Consulting AI coach..."):
                result = generate_guide(exercise.strip(), level)
            st.markdown("---")
            st.markdown(result)

    st.markdown("---")
    st.caption(
        "Remember: Always prioritize proper form over heavier weights. "
        "When in doubt, seek professional guidance."
    )

elif page == "💪 Muscle Groups":
    st.title("💪 Muscle Group Database")
    st.markdown("Explore muscles, descriptions, and common exercises for each muscle group.")

    group = st.selectbox("Select Muscle Group", VALID_MUSCLE_GROUPS)
    info = get_muscle_info(group)

    if info:
        st.subheader(f"{group.title()}")
        st.markdown(f"**Description:** {info['description']}")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Muscles:**")
            for m in info["muscles"]:
                st.markdown(f"- {m}")
        with col2:
            st.markdown("**Common Exercises:**")
            for ex in info["common_exercises"]:
                st.markdown(f"- {ex}")
    else:
        st.info("No information available for this muscle group.")

elif page == "📈 Progression Paths":
    st.title("📈 Exercise Progression Paths")
    st.markdown("See how to progress from beginner to advanced variations.")

    exercise = st.selectbox("Select Exercise", list(PROGRESSION_PATHS.keys()))
    variations = get_exercise_variations(exercise)

    if variations:
        st.subheader(f"Progression: {exercise.title()}")
        for i, step in enumerate(variations, 1):
            if i <= 2:
                level_label = "🟢 Beginner"
            elif i <= 4:
                level_label = "🟡 Intermediate"
            else:
                level_label = "🔴 Advanced"
            st.markdown(f"**Step {i}:** {step} &nbsp; *({level_label})*")
    else:
        st.info("No progression path available for this exercise.")

elif page == "🔥 Warm-up/Cool-down":
    st.title("🔥 Warm-up & 🧘 Cool-down Routines")
    st.markdown("Prepare your body before training and recover properly afterward.")

    group = st.selectbox("Select Muscle Group", VALID_MUSCLE_GROUPS, key="wc_group")

    tab_warmup, tab_cooldown = st.tabs(["🔥 Warm-up", "🧘 Cool-down"])

    with tab_warmup:
        warmup = get_warmup_routine(group)
        if warmup:
            st.subheader(f"Warm-up: {group.title()}")
            import pandas as pd

            df = pd.DataFrame(warmup)
            df.columns = ["Exercise", "Duration", "Description"]
            st.table(df)
        else:
            st.info("No warm-up routine available for this muscle group.")

    with tab_cooldown:
        cooldown = get_cooldown_routine(group)
        if cooldown:
            st.subheader(f"Cool-down: {group.title()}")
            import pandas as pd

            df = pd.DataFrame(cooldown)
            df.columns = ["Stretch", "Duration", "Description"]
            st.table(df)
        else:
            st.info("No cool-down routine available for this muscle group.")

# ---------------------------------------------------------------------------
# Footer Disclaimer
# ---------------------------------------------------------------------------

st.markdown("---")
st.markdown(
    "*⚠️ This tool is for educational purposes only and is NOT medical advice. "
    "Always consult a qualified fitness professional or physician before starting "
    "any exercise program.*"
)
