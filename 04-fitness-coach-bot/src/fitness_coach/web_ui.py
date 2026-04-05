"""Streamlit web interface for Fitness Coach Bot."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

import streamlit as st

from .config import load_config, setup_logging
from .core import check_ollama_running, generate_workout_plan, get_exercise_details, LEVELS, GOALS
from .utils import (
    log_workout,
    load_workout_log,
    record_progress,
    load_progress,
    get_progress_summary,
    search_exercises,
    EXERCISE_LIBRARY,
)

st.set_page_config(page_title="💪 Fitness Coach Bot", page_icon="💪", layout="wide")


def init_state():
    defaults = {"config": load_config(), "workout_plan": ""}
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def sidebar():
    cfg = st.session_state.config
    st.sidebar.title("⚙️ Settings")
    cfg["model"]["name"] = st.sidebar.text_input("Model", value=cfg["model"]["name"])
    cfg["model"]["temperature"] = st.sidebar.slider("Temperature", 0.0, 1.0, cfg["model"]["temperature"], 0.1)

    st.sidebar.markdown("---")
    st.sidebar.subheader("👤 Profile Setup")
    level = st.sidebar.selectbox("Fitness Level", LEVELS)
    goal = st.sidebar.selectbox("Goal", GOALS)
    equipment = st.sidebar.text_input("Equipment", value="bodyweight")
    days = st.sidebar.slider("Days/Week", 1, 7, 4)
    duration = st.sidebar.slider("Minutes/Session", 15, 120, 45)
    return level, goal, equipment, days, duration


def main():
    init_state()
    cfg = st.session_state.config
    setup_logging(cfg)
    storage_cfg = cfg.get("storage", {})

    st.title("💪 Fitness Coach Bot")
    st.caption("Personalized workout plans, exercise library, and progress tracking.")
    st.warning("⚕️ Always consult a healthcare provider before starting a new exercise program.")

    level, goal, equipment, days, duration = sidebar()

    tab_plan, tab_log, tab_progress, tab_library = st.tabs(["🏋️ Workout Plan", "📝 Log Workout", "📈 Progress", "📚 Exercise Library"])

    with tab_plan:
        if st.button("🏋️ Generate Workout Plan", type="primary"):
            if not check_ollama_running():
                st.error("❌ Ollama is not running.")
                return
            with st.spinner("Creating your workout plan..."):
                plan = generate_workout_plan(
                    level, goal, equipment, days, duration,
                    model=cfg["model"]["name"],
                    temperature=cfg["model"]["temperature"],
                )
                st.session_state.workout_plan = plan
        if st.session_state.workout_plan:
            st.markdown(st.session_state.workout_plan)

        st.markdown("---")
        st.subheader("📖 Exercise Details")
        ex_name = st.text_input("Exercise name")
        if st.button("Get Details") and ex_name:
            with st.spinner("Looking up..."):
                details = get_exercise_details(ex_name, level, model=cfg["model"]["name"])
            st.markdown(details)

    with tab_log:
        st.subheader("📝 Log a Workout")
        col1, col2, col3, col4 = st.columns(4)
        ex = col1.text_input("Exercise", key="log_ex")
        sets = col2.number_input("Sets", 1, 20, 3, key="log_sets")
        reps = col3.number_input("Reps", 1, 100, 10, key="log_reps")
        weight = col4.number_input("Weight (kg, 0=N/A)", 0.0, 500.0, 0.0, key="log_weight")
        if st.button("✅ Log Workout") and ex:
            log_workout(ex, sets, reps, weight=weight if weight > 0 else None,
                        filepath=storage_cfg.get("workout_log_file", "workout_log.json"))
            st.success(f"Logged: {ex} {sets}x{reps}")

        st.markdown("---")
        st.subheader("📋 Recent Workouts")
        wlog = load_workout_log(storage_cfg.get("workout_log_file", "workout_log.json"))
        if wlog:
            for entry in reversed(wlog[-10:]):
                w = f" @ {entry['weight']}kg" if entry.get("weight") else ""
                st.markdown(f"- **{entry['exercise']}** {entry['sets']}x{entry['reps']}{w} — {entry['date'][:10]}")
        else:
            st.info("No workouts logged yet.")

    with tab_progress:
        st.subheader("📈 Record Progress")
        col1, col2 = st.columns(2)
        w_kg = col1.number_input("Weight (kg)", 0.0, 300.0, 0.0, key="prog_w")
        bf = col2.number_input("Body Fat %", 0.0, 60.0, 0.0, key="prog_bf")
        notes = st.text_input("Notes", key="prog_notes")
        if st.button("📊 Record"):
            record_progress(
                weight_kg=w_kg if w_kg > 0 else None,
                body_fat_pct=bf if bf > 0 else None,
                notes=notes,
                filepath=storage_cfg.get("progress_file", "progress.json"),
            )
            st.success("Progress recorded!")

        st.markdown("---")
        summary = get_progress_summary(storage_cfg.get("progress_file", "progress.json"))
        if summary["entries"] > 0:
            cols = st.columns(3)
            cols[0].metric("Entries", summary["entries"])
            if summary.get("latest_weight"):
                cols[1].metric("Latest Weight", f"{summary['latest_weight']} kg")
            if summary.get("weight_change") is not None:
                cols[2].metric("Weight Change", f"{summary['weight_change']:+.1f} kg")

            progress_data = load_progress(storage_cfg.get("progress_file", "progress.json"))
            weights = [p["weight_kg"] for p in progress_data if p.get("weight_kg")]
            if len(weights) > 1:
                st.line_chart(weights)
        else:
            st.info("No progress data yet.")

    with tab_library:
        st.subheader("📚 Exercise Library")
        search = st.text_input("Search exercises", key="lib_search")
        diff_filter = st.selectbox("Difficulty", [None, "beginner", "intermediate", "advanced"], format_func=lambda x: x or "All")
        results = search_exercises(search or "", diff_filter)
        if results:
            for e in results:
                st.markdown(f"**{e['name'].title()}** — {e['muscles']} | {e['type']} | {e['difficulty']}")
        else:
            st.info("No exercises match your search.")


if __name__ == "__main__":
    main()
