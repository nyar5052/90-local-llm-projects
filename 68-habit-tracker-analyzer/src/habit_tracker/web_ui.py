#!/usr/bin/env python3
"""Habit Tracker Analyzer - Streamlit Web UI."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from common.llm_client import check_ollama_running

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta

from .core import (
    load_config,
    load_habits,
    save_habits,
    log_habit,
    add_habit,
    delete_habit,
    compute_streaks,
    get_completion_rate,
    compute_correlations,
    check_achievements,
    analyze_habits,
    get_calendar_data,
    generate_weekly_report,
    generate_monthly_report,
    ACHIEVEMENTS,
)

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------

st.set_page_config(page_title="Habit Tracker Analyzer", page_icon="🎯", layout="wide")

config = load_config()
HABITS_FILE = config.get("habits_file", "habits.json")


def _load():
    return load_habits(HABITS_FILE)


# ---------------------------------------------------------------------------
# Sidebar navigation
# ---------------------------------------------------------------------------

st.sidebar.title("🎯 Habit Tracker")
page = st.sidebar.radio("Navigate", ["Log Habits", "Dashboard", "Analytics", "Achievements"])

# ============================================================================
# LOG HABITS PAGE
# ============================================================================

if page == "Log Habits":
    st.header("📝 Log Habits")
    data = _load()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Log Existing Habit")
        habit_names = {k: v["name"] for k, v in data["habits"].items()}
        if habit_names:
            selected = st.selectbox("Select habit", list(habit_names.values()))
            done = st.toggle("Done", value=True)
            notes = st.text_input("Notes (optional)")
            if st.button("📌 Log Habit"):
                entry = log_habit(selected, done, notes, habits_file=HABITS_FILE)
                st.success(f"{'✅ Done' if done else '⏭️ Skipped'}: {selected} ({entry['date']})")
                st.rerun()
        else:
            st.info("No habits yet. Add one on the right →")

    with col2:
        st.subheader("Add New Habit")
        new_name = st.text_input("Habit name")
        new_category = st.selectbox("Category", ["general", "health", "learning",
                                                   "productivity", "mindfulness", "fitness"])
        new_target = st.selectbox("Target", ["daily", "weekly"])
        if st.button("➕ Add Habit"):
            if new_name.strip():
                add_habit(new_name.strip(), new_category, new_target, habits_file=HABITS_FILE)
                st.success(f"Added: {new_name}")
                st.rerun()
            else:
                st.warning("Enter a habit name.")

    # Today's summary
    st.divider()
    st.subheader("📅 Today's Log")
    data = _load()
    today = datetime.now().strftime("%Y-%m-%d")
    today_logs = [l for l in data["logs"] if l["date"] == today]

    if today_logs:
        for l in today_logs:
            icon = "✅" if l["done"] else "⏭️"
            name = data["habits"].get(l["habit"], {}).get("name", l["habit"])
            note_str = f' — {l["notes"]}' if l.get("notes") else ""
            st.write(f"{icon} **{name}** at {l['time']}{note_str}")
    else:
        st.info("No logs today yet.")


# ============================================================================
# DASHBOARD PAGE
# ============================================================================

elif page == "Dashboard":
    st.header("📊 Dashboard")
    data = _load()

    if not data["habits"]:
        st.warning("No habits tracked yet. Go to **Log Habits** to get started.")
    else:
        streaks = compute_streaks(data)
        rates = get_completion_rate(data, 30)

        # Quick stats
        total_days = len({l["date"] for l in data["logs"] if l["done"]})
        best_overall = max((s["best"] for s in streaks.values()), default=0)
        avg_rate = (
            sum(r["rate"] for r in rates.values()) / len(rates)
            if rates else 0
        )

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Active Days", total_days)
        c2.metric("Best Streak", f"🔥 {best_overall}")
        c3.metric("Avg 30-Day Rate", f"{avg_rate:.0f}%")
        c4.metric("Habits Tracked", len(data["habits"]))

        st.divider()

        # Current streaks
        st.subheader("🔥 Current Streaks")
        streak_cols = st.columns(min(len(streaks), 4))
        for idx, (key, info) in enumerate(streaks.items()):
            name = data["habits"].get(key, {}).get("name", key)
            with streak_cols[idx % len(streak_cols)]:
                st.metric(name, f"🔥 {info['current']} days", f"Best: {info['best']}")

        st.divider()

        # Completion rate bars
        st.subheader("📈 Completion Rates (30 days)")
        rate_df = pd.DataFrame([
            {
                "Habit": data["habits"].get(k, {}).get("name", k),
                "Rate": v["rate"],
            }
            for k, v in rates.items()
        ])
        if not rate_df.empty:
            fig = px.bar(rate_df, x="Habit", y="Rate", color="Rate",
                         color_continuous_scale="Greens", range_y=[0, 100])
            fig.update_layout(yaxis_title="Completion %")
            st.plotly_chart(fig, use_container_width=True)

        # Calendar heatmap
        st.subheader("📅 Streak Calendar")
        habit_select = st.selectbox(
            "Select habit for calendar",
            list(data["habits"].keys()),
            format_func=lambda k: data["habits"][k]["name"],
        )
        cal_data = get_calendar_data(data, habit_select, months=3)
        if cal_data:
            cal_df = pd.DataFrame([
                {"Date": d, "Done": 1 if v else 0}
                for d, v in cal_data.items()
            ])
            cal_df["Date"] = pd.to_datetime(cal_df["Date"])
            cal_df["Week"] = cal_df["Date"].dt.isocalendar().week.astype(int)
            cal_df["Day"] = cal_df["Date"].dt.day_name()

            fig2 = px.density_heatmap(
                cal_df, x="Week", y="Day", z="Done",
                color_continuous_scale=["#ebedf0", "#40c463"],
                category_orders={"Day": ["Monday", "Tuesday", "Wednesday",
                                          "Thursday", "Friday", "Saturday", "Sunday"]},
            )
            fig2.update_layout(height=250)
            st.plotly_chart(fig2, use_container_width=True)


# ============================================================================
# ANALYTICS PAGE
# ============================================================================

elif page == "Analytics":
    st.header("🔬 Analytics")
    data = _load()

    if not data["habits"]:
        st.warning("No habits tracked yet.")
    else:
        period = st.selectbox("Period", ["week", "month", "year"])
        days_map = {"week": 7, "month": 30, "year": 365}
        days = days_map[period]

        # Completion rate chart
        st.subheader("📈 Completion Rate Over Time")
        rates = get_completion_rate(data, days)
        rate_df = pd.DataFrame([
            {
                "Habit": data["habits"].get(k, {}).get("name", k),
                "Rate": v["rate"],
                "Done": v["done"],
                "Total Days": v["total_days"],
            }
            for k, v in rates.items()
        ])
        if not rate_df.empty:
            fig = px.bar(rate_df, x="Habit", y="Rate",
                         color="Rate", color_continuous_scale="RdYlGn",
                         range_y=[0, 100], text="Rate")
            fig.update_traces(texttemplate="%{text:.0f}%", textposition="outside")
            st.plotly_chart(fig, use_container_width=True)

        # Correlation matrix
        st.subheader("🔗 Habit Correlations")
        correlations = compute_correlations(data)
        if correlations:
            corr_rows = []
            for info in correlations.values():
                h1_name = data["habits"].get(info["habits"][0], {}).get("name", info["habits"][0])
                h2_name = data["habits"].get(info["habits"][1], {}).get("name", info["habits"][1])
                corr_rows.append({
                    "Habit 1": h1_name,
                    "Habit 2": h2_name,
                    "Co-occurrence %": info["rate"],
                })
            corr_df = pd.DataFrame(corr_rows)
            st.dataframe(corr_df, use_container_width=True)
        else:
            st.info("Need at least 2 habits with logs to compute correlations.")

        # AI analysis
        st.subheader("🤖 AI Analysis")
        if st.button("🔍 Run AI Analysis"):
            if not check_ollama_running():
                st.error("Ollama is not running. Start it with: `ollama serve`")
            else:
                with st.spinner("Analyzing your habits..."):
                    result = analyze_habits(data, period, config)
                st.markdown(result)


# ============================================================================
# ACHIEVEMENTS PAGE
# ============================================================================

elif page == "Achievements":
    st.header("🏅 Achievements")
    data = _load()

    if not data["habits"]:
        st.warning("No habits tracked yet.")
    else:
        earned = check_achievements(data)
        earned_ids = {a["id"] for a in earned}

        st.subheader("🏆 Achievement Gallery")
        cols = st.columns(3)
        for idx, (ach_id, ach) in enumerate(ACHIEVEMENTS.items()):
            with cols[idx % 3]:
                if ach_id in earned_ids:
                    st.success(f"{ach['icon']}  **{ach['name']}**\n\n{ach['description']}")
                else:
                    st.info(f"🔒  **{ach['name']}**\n\n{ach['description']}")

        st.divider()

        # Progress towards next achievement
        st.subheader("📈 Progress")
        streaks = compute_streaks(data)
        for key, info in streaks.items():
            name = data["habits"].get(key, {}).get("name", key)
            max_streak = max(info["current"], info["best"])

            next_target = None
            for threshold in [7, 30, 100]:
                if max_streak < threshold:
                    next_target = threshold
                    break

            if next_target:
                progress = min(max_streak / next_target, 1.0)
                st.write(f"**{name}**: {max_streak}/{next_target} days")
                st.progress(progress)
            else:
                st.write(f"**{name}**: 💯 All streak milestones achieved!")

        st.divider()
        st.metric("Achievements Unlocked", f"{len(earned_ids)} / {len(ACHIEVEMENTS)}")
