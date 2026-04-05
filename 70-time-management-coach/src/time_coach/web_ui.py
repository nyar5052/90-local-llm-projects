"""Streamlit Web UI for Time Management Coach."""

import os
import sys
import csv
import time
import io
from datetime import date, datetime, timedelta

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# Ensure project root is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from src.time_coach.core import (
    load_config,
    load_timelog,
    save_time_entry,
    compute_time_breakdown,
    compute_daily_totals,
    compute_productivity_score,
    generate_time_blocks,
    analyze_time_usage,
    generate_pomodoro_plan,
    generate_weekly_review,
    get_focus_time_stats,
    get_category_breakdown,
    compute_trends,
    check_ollama_running,
    POMODORO_DEFAULTS,
)

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(page_title="Time Management Coach", page_icon="⏱️", layout="wide")

CONFIG_PATH = os.environ.get("TIME_COACH_CONFIG", "config.yaml")
config = load_config(CONFIG_PATH)

# ---------------------------------------------------------------------------
# Session-state defaults
# ---------------------------------------------------------------------------
if "pomodoro_running" not in st.session_state:
    st.session_state.pomodoro_running = False
if "pomodoro_sessions" not in st.session_state:
    st.session_state.pomodoro_sessions = 0
if "pomodoro_start" not in st.session_state:
    st.session_state.pomodoro_start = None

# ---------------------------------------------------------------------------
# Sidebar navigation
# ---------------------------------------------------------------------------
st.sidebar.title("⏱️ Time Coach")
page = st.sidebar.radio("Navigate", ["Time Log", "Analysis", "Pomodoro Timer", "Weekly Review"])

LOG_FILE = config.get("time_log", "timelog.csv")


# ===========================================================================
# PAGE: Time Log
# ===========================================================================
def page_time_log():
    st.header("📝 Time Log")

    # --- Quick entry form ---
    with st.expander("➕ Quick Entry", expanded=True):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            entry_date = st.date_input("Date", value=date.today())
        with col2:
            category = st.selectbox("Category", [
                "coding", "writing", "design", "research",
                "email", "meetings", "admin", "lunch", "break", "exercise", "other",
            ])
        with col3:
            activity = st.text_input("Activity")
        with col4:
            duration = st.number_input("Duration (h)", min_value=0.0, max_value=24.0, value=1.0, step=0.25)

        if st.button("Log Entry"):
            if activity:
                save_time_entry({
                    "date": entry_date.isoformat(),
                    "category": category,
                    "activity": activity,
                    "duration": str(duration),
                }, LOG_FILE)
                st.success(f"✅ Logged: {category} — {activity} ({duration}h)")
                st.rerun()
            else:
                st.warning("Please enter an activity description.")

    # --- Upload CSV ---
    with st.expander("📁 Upload CSV"):
        uploaded = st.file_uploader("Upload a time-log CSV", type=["csv"])
        if uploaded is not None:
            content = uploaded.read().decode("utf-8")
            reader = csv.DictReader(io.StringIO(content))
            count = 0
            for row in reader:
                save_time_entry(row, LOG_FILE)
                count += 1
            st.success(f"Imported {count} entries.")

    # --- Today's entries ---
    st.subheader("Today's Entries")
    if os.path.exists(LOG_FILE):
        entries = load_timelog(LOG_FILE)
        today_str = date.today().isoformat()
        today_entries = [e for e in entries if e.get("date") == today_str]
        if today_entries:
            st.table(today_entries)
        else:
            st.info("No entries logged today yet.")

        # --- Category breakdown pie chart ---
        breakdown = compute_time_breakdown(entries)
        if breakdown:
            st.subheader("Category Breakdown")
            fig = px.pie(
                names=list(breakdown.keys()),
                values=list(breakdown.values()),
                title="Hours by Category",
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No time log file found. Start logging entries above!")


# ===========================================================================
# PAGE: Analysis
# ===========================================================================
def page_analysis():
    st.header("📊 Analysis")

    log_path = st.text_input("Time log path", value=LOG_FILE)
    if not os.path.exists(log_path):
        st.warning("Log file not found. Log some entries first or upload a CSV on the Time Log page.")
        return

    entries = load_timelog(log_path)
    breakdown = compute_time_breakdown(entries)
    daily = compute_daily_totals(entries)
    total_hours = sum(breakdown.values())

    # --- Time breakdown table ---
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Time Breakdown")
        rows = []
        for cat, hrs in breakdown.items():
            pct = (hrs / total_hours * 100) if total_hours else 0
            rows.append({"Category": cat, "Hours": f"{hrs:.1f}", "%": f"{pct:.1f}%"})
        st.table(rows)

    with col2:
        st.subheader("Daily Totals")
        if daily:
            fig = px.line(
                x=list(daily.keys()),
                y=list(daily.values()),
                labels={"x": "Date", "y": "Hours"},
                title="Daily Hours",
            )
            st.plotly_chart(fig, use_container_width=True)

    # --- Productivity score ---
    st.subheader("Productivity Score")
    score_info = compute_productivity_score(breakdown, config)
    score_val = score_info["score"]
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score_val,
        domain={"x": [0, 1], "y": [0, 1]},
        title={"text": "Productivity Score"},
        gauge={
            "axis": {"range": [0, 10]},
            "bar": {"color": "darkblue"},
            "steps": [
                {"range": [0, 4], "color": "red"},
                {"range": [4, 7], "color": "yellow"},
                {"range": [7, 10], "color": "green"},
            ],
        },
    ))
    st.plotly_chart(fig_gauge, use_container_width=True)

    if score_info["suggestions"]:
        st.info("\n".join(f"• {s}" for s in score_info["suggestions"]))

    # --- Category trends ---
    st.subheader("Category Trends")
    trends = compute_trends(entries)
    if trends:
        all_cats = set()
        for wb in trends.values():
            all_cats.update(wb.keys())
        trend_rows = []
        for week, bd in trends.items():
            for cat in all_cats:
                trend_rows.append({"Week": week, "Category": cat, "Hours": bd.get(cat, 0)})
        if trend_rows:
            fig_trend = px.bar(trend_rows, x="Week", y="Hours", color="Category",
                               barmode="group", title="Weekly Category Trends")
            st.plotly_chart(fig_trend, use_container_width=True)

    # --- AI analysis ---
    st.subheader("AI Analysis")
    if st.button("🤖 Run AI Analysis"):
        if not check_ollama_running():
            st.error("Ollama is not running. Start it with `ollama serve`.")
        else:
            with st.spinner("Analyzing…"):
                result = analyze_time_usage(entries, breakdown, daily, config)
            st.markdown(result)


# ===========================================================================
# PAGE: Pomodoro Timer
# ===========================================================================
def page_pomodoro():
    st.header("🍅 Pomodoro Timer")

    pom_cfg = config.get("pomodoro", POMODORO_DEFAULTS)
    work_min = pom_cfg.get("work_minutes", 25)
    short_brk = pom_cfg.get("short_break", 5)
    long_brk = pom_cfg.get("long_break", 15)
    sessions_long = pom_cfg.get("sessions_before_long", 4)

    task = st.text_input("Current task")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Work", f"{work_min} min")
    with col2:
        st.metric("Short Break", f"{short_brk} min")
    with col3:
        st.metric("Long Break", f"{long_brk} min")

    # Timer display
    if st.button("▶️ Start Pomodoro" if not st.session_state.pomodoro_running else "⏹️ Stop"):
        st.session_state.pomodoro_running = not st.session_state.pomodoro_running
        if st.session_state.pomodoro_running:
            st.session_state.pomodoro_start = time.time()
        else:
            st.session_state.pomodoro_sessions += 1

    if st.session_state.pomodoro_running and st.session_state.pomodoro_start:
        elapsed = time.time() - st.session_state.pomodoro_start
        remaining = max(0, work_min * 60 - elapsed)
        mins, secs = divmod(int(remaining), 60)
        st.markdown(f"### ⏳ {mins:02d}:{secs:02d}")
        if remaining <= 0:
            st.balloons()
            st.session_state.pomodoro_running = False
            st.session_state.pomodoro_sessions += 1
            # Auto-log the session
            if task:
                save_time_entry({
                    "date": date.today().isoformat(),
                    "category": "pomodoro",
                    "activity": task,
                    "duration": str(round(work_min / 60, 2)),
                }, LOG_FILE)
                st.success(f"Session logged: {task}")

    st.markdown(f"**Sessions today:** {st.session_state.pomodoro_sessions}")
    next_break = "Long break" if (st.session_state.pomodoro_sessions + 1) % sessions_long == 0 else "Short break"
    st.caption(f"Next: {next_break}")

    # --- Generate full-day plan ---
    st.divider()
    st.subheader("Generate Full-Day Pomodoro Plan")
    plan_tasks = st.text_area("Tasks (comma-separated)")
    plan_hours = st.slider("Available hours", 1.0, 12.0, 8.0, 0.5)
    if st.button("🍅 Generate Plan"):
        if not check_ollama_running():
            st.error("Ollama is not running.")
        elif plan_tasks:
            with st.spinner("Generating plan…"):
                result = generate_pomodoro_plan(plan_tasks, plan_hours, config)
            st.markdown(result)


# ===========================================================================
# PAGE: Weekly Review
# ===========================================================================
def page_weekly_review():
    st.header("📅 Weekly Review")

    log_path = st.text_input("Time log path", value=LOG_FILE, key="weekly_log")
    if not os.path.exists(log_path):
        st.warning("Log file not found.")
        return

    entries = load_timelog(log_path)
    breakdown = compute_time_breakdown(entries)
    daily = compute_daily_totals(entries)
    total_hours = sum(breakdown.values())
    days = len(daily)

    # --- Week selector ---
    trends = compute_trends(entries, weeks=8)
    available_weeks = list(trends.keys())
    if available_weeks:
        selected_week = st.selectbox("Select week", available_weeks, index=len(available_weeks) - 1)
    else:
        selected_week = None

    # --- Summary stats ---
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Hours", f"{total_hours:.1f}h")
    with col2:
        st.metric("Days Tracked", str(days))
    with col3:
        avg = total_hours / max(days, 1)
        st.metric("Avg Daily", f"{avg:.1f}h")
    with col4:
        score_info = compute_productivity_score(breakdown, config)
        st.metric("Score", f"{score_info['score']}/10")

    # --- Category comparison ---
    if len(available_weeks) >= 2:
        st.subheader("This Week vs Last Week")
        this_wk = trends.get(available_weeks[-1], {})
        last_wk = trends.get(available_weeks[-2], {})
        all_cats = sorted(set(list(this_wk.keys()) + list(last_wk.keys())))
        comp_rows = []
        for cat in all_cats:
            comp_rows.append({
                "Category": cat,
                "This Week": f"{this_wk.get(cat, 0):.1f}h",
                "Last Week": f"{last_wk.get(cat, 0):.1f}h",
            })
        st.table(comp_rows)

    # --- Productivity trend ---
    if trends:
        st.subheader("Productivity Trend")
        week_labels = list(trends.keys())
        week_totals = [sum(b.values()) for b in trends.values()]
        fig = px.line(x=week_labels, y=week_totals, labels={"x": "Week", "y": "Total Hours"},
                      title="Weekly Total Hours")
        st.plotly_chart(fig, use_container_width=True)

    # --- Goals vs actual ---
    st.subheader("Goals vs Actual")
    target_deep = config.get("productivity", {}).get("target_deep_work_hours", 4.0)
    target_total = config.get("productivity", {}).get("target_total_hours", 8.0)
    focus = get_focus_time_stats(entries, config)
    goals_data = [
        {"Metric": "Deep Work (daily avg)", "Target": f"{target_deep:.1f}h",
         "Actual": f"{focus['deep_work_hours'] / max(days, 1):.1f}h"},
        {"Metric": "Total (daily avg)", "Target": f"{target_total:.1f}h",
         "Actual": f"{total_hours / max(days, 1):.1f}h"},
    ]
    st.table(goals_data)

    # --- AI weekly review ---
    st.subheader("AI Weekly Review")
    if st.button("🤖 Generate Weekly Review"):
        if not check_ollama_running():
            st.error("Ollama is not running. Start it with `ollama serve`.")
        else:
            with st.spinner("Generating weekly review…"):
                result = generate_weekly_review(entries, config)
            st.markdown(result)


# ===========================================================================
# Router
# ===========================================================================
if page == "Time Log":
    page_time_log()
elif page == "Analysis":
    page_analysis()
elif page == "Pomodoro Timer":
    page_pomodoro()
elif page == "Weekly Review":
    page_weekly_review()
