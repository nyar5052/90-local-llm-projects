"""
Health Plan Generator - Streamlit Web UI.

⚠️  DISCLAIMER: This tool is for INFORMATIONAL and EDUCATIONAL PURPOSES ONLY.
It does NOT provide medical advice, diagnosis, or treatment. Always consult a
qualified healthcare professional before starting any new health, diet, or
exercise program.
"""

import streamlit as st

from health_planner.core import (
    DISCLAIMER,
    WEEKLY_CHECKIN_QUESTIONS,
    ProgressTracker,
    check_ollama_running,
    generate_adaptive_recommendation,
    generate_plan,
    get_milestones_for_goal,
)

# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="🏋️ Health Plan Generator",
    page_icon="🏋️",
    layout="wide",
)

# ---------------------------------------------------------------------------
# Disclaimer banner
# ---------------------------------------------------------------------------
st.error(DISCLAIMER)

st.title("🏋️ Health Plan Generator")
st.caption(
    "AI-powered personalized wellness plans • **For informational purposes only**"
)

# ---------------------------------------------------------------------------
# Session state initialisation
# ---------------------------------------------------------------------------
if "tracker" not in st.session_state:
    st.session_state.tracker = ProgressTracker()
if "plan" not in st.session_state:
    st.session_state.plan = None
if "plan_goal" not in st.session_state:
    st.session_state.plan_goal = None

# ---------------------------------------------------------------------------
# Sidebar — Health Profile
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("👤 Health Profile")

    goal = st.text_input(
        "Wellness Goal",
        placeholder="e.g. lose weight, better sleep, reduce stress",
    )
    age = st.number_input("Age (optional)", min_value=0, max_value=120, value=0, step=1)
    age_val = age if age > 0 else None

    lifestyle = st.selectbox(
        "Activity Level",
        options=["sedentary", "moderate", "active"],
        index=1,
    )
    duration = st.selectbox(
        "Plan Duration",
        options=["1week", "1month", "3months"],
        index=1,
        format_func=lambda d: {"1week": "1 Week", "1month": "1 Month", "3months": "3 Months"}[d],
    )

    st.divider()
    ollama_ok = check_ollama_running()
    if ollama_ok:
        st.success("✅ Ollama is running")
    else:
        st.error("❌ Ollama is not running — start it first")

# ---------------------------------------------------------------------------
# Main area — tabs
# ---------------------------------------------------------------------------
tab_plan, tab_milestones, tab_checkin, tab_progress = st.tabs(
    ["📋 Plan Generator", "🎯 Milestone Tracker", "📝 Weekly Check-in", "📈 Progress Dashboard"]
)

# ---- Plan Generator Tab --------------------------------------------------
with tab_plan:
    st.subheader("Generate Your Wellness Plan")

    if st.button("🚀 Generate Plan", disabled=not (goal and ollama_ok), type="primary"):
        with st.spinner("Creating your personalised wellness plan..."):
            plan_text = generate_plan(goal, age_val, lifestyle, duration)
            st.session_state.plan = plan_text
            st.session_state.plan_goal = goal
            # Also initialize the tracker
            st.session_state.tracker.start_plan(goal)

    if st.session_state.plan:
        st.markdown("---")
        st.markdown(f"### Wellness Plan: {st.session_state.plan_goal}")
        st.markdown(st.session_state.plan)
        st.warning(DISCLAIMER)

# ---- Milestone Tracker Tab -----------------------------------------------
with tab_milestones:
    st.subheader("🎯 Goal Milestones")

    milestone_goal = goal or st.session_state.plan_goal or "general wellness"
    milestones = get_milestones_for_goal(milestone_goal)

    tracker = st.session_state.tracker
    current_week = tracker.current_week if tracker.goal else 1

    for m in milestones:
        week = m["week"]
        if week < current_week:
            icon = "✅"
        elif week == current_week:
            icon = "🔵"
        else:
            icon = "⬜"

        with st.expander(f"{icon} Week {week}: {m['milestone']}", expanded=(week == current_week)):
            st.write(f"💡 **Tip:** {m['tip']}")
            if week < current_week:
                st.success("Completed!")
            elif week == current_week:
                st.info("This is your current milestone.")

# ---- Weekly Check-in Tab -------------------------------------------------
with tab_checkin:
    st.subheader("📝 Weekly Check-in")

    if not st.session_state.tracker.goal:
        st.info("Generate a plan first to start tracking progress.")
    else:
        t = st.session_state.tracker
        st.write(f"**Goal:** {t.goal} | **Week:** {t.current_week} | **Started:** {t.start_date}")

        with st.form("checkin_form"):
            energy = st.slider(WEEKLY_CHECKIN_QUESTIONS[0], 1, 10, 5)
            meal = st.radio(
                WEEKLY_CHECKIN_QUESTIONS[1],
                options=["mostly", "partially", "not really"],
                horizontal=True,
            )
            exercise_days = st.number_input(
                WEEKLY_CHECKIN_QUESTIONS[2], min_value=0, max_value=7, value=3
            )
            sleep_q = st.slider(WEEKLY_CHECKIN_QUESTIONS[3], 1, 10, 5)
            challenge = st.text_input(WEEKLY_CHECKIN_QUESTIONS[4])
            win = st.text_input(WEEKLY_CHECKIN_QUESTIONS[5])
            stress = st.slider(WEEKLY_CHECKIN_QUESTIONS[6], 1, 10, 5)
            symptoms = st.text_input(WEEKLY_CHECKIN_QUESTIONS[7], value="None")
            adjustments = st.text_input(WEEKLY_CHECKIN_QUESTIONS[8])

            submitted = st.form_submit_button("✅ Submit Check-in", type="primary")

        if submitted:
            responses = {
                "energy": energy,
                "meal_plan": meal,
                "exercise_days": exercise_days,
                "sleep": sleep_q,
                "challenge": challenge,
                "win": win,
                "stress": stress,
                "symptoms": symptoms,
                "adjustments": adjustments,
            }
            entry = t.add_checkin(responses)
            st.success(f"Check-in for Week {entry['week']} saved!")

            recs = generate_adaptive_recommendation(t)
            st.info(recs)

# ---- Progress Dashboard Tab ----------------------------------------------
with tab_progress:
    st.subheader("📈 Progress Dashboard")

    if not st.session_state.tracker.goal:
        st.info("Generate a plan and complete check-ins to see your progress.")
    else:
        t = st.session_state.tracker
        summary = t.get_progress_summary()

        col1, col2, col3 = st.columns(3)
        col1.metric("Weeks Completed", summary.get("weeks_completed", 0))
        col2.metric(
            "Avg Energy",
            f"{summary['avg_energy']:.1f}/10" if summary.get("avg_energy") is not None else "N/A",
        )
        col3.metric(
            "Avg Sleep",
            f"{summary['avg_sleep']:.1f}/10" if summary.get("avg_sleep") is not None else "N/A",
        )

        st.markdown("---")

        # Energy & sleep trend chart
        if t.checkins:
            import pandas as pd

            chart_data = pd.DataFrame(
                {
                    "Week": [c["week"] for c in t.checkins],
                    "Energy": [c["responses"].get("energy", 0) for c in t.checkins],
                    "Sleep": [c["responses"].get("sleep", 0) for c in t.checkins],
                    "Stress": [c["responses"].get("stress", 0) for c in t.checkins],
                }
            )
            chart_data = chart_data.set_index("Week")
            st.line_chart(chart_data)

            # Check-in history
            st.subheader("Check-in History")
            for c in reversed(t.checkins):
                with st.expander(f"Week {c['week']} — {c['date']}"):
                    for k, v in c["responses"].items():
                        st.write(f"**{k.replace('_', ' ').title()}:** {v}")
        else:
            st.info("Complete your first weekly check-in to see progress charts.")

        # Adaptive recommendations
        st.markdown("---")
        recs = generate_adaptive_recommendation(t)
        st.subheader("🔄 Adaptive Recommendations")
        st.info(recs)

# ---------------------------------------------------------------------------
# Footer disclaimer
# ---------------------------------------------------------------------------
st.markdown("---")
st.warning(DISCLAIMER)
st.caption("*Part of the 90 Local LLM Projects collection.*")
