"""
Sleep Improvement Advisor - Streamlit Web UI.

⚠️  DISCLAIMER: This tool is for educational and informational purposes only and
is NOT medical advice. It does NOT diagnose or treat sleep disorders.
"""

import streamlit as st

# Custom CSS for professional dark theme
st.set_page_config(page_title="Sleep Improvement Advisor", page_icon="🎯", layout="wide")

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

import os
import tempfile

from .core import (
    parse_sleep_log,
    compute_sleep_stats,
    calculate_sleep_score,
    get_environment_checklist,
    build_bedtime_routine,
    analyze_weekly_patterns,
)

def show_disclaimer():
    """Display medical disclaimer prominently."""
    st.error(
        "⚠️ **MEDICAL DISCLAIMER**: This tool provides AI-generated sleep improvement "
        "suggestions for **informational purposes only**. It is **NOT medical advice** "
        "and does **NOT** diagnose or treat sleep disorders."
    )
    st.warning(
        "If you have persistent sleep problems, please **consult a qualified healthcare "
        "provider**. This tool is not a substitute for professional medical evaluation."
    )


def _save_uploaded_csv(uploaded_file) -> str:
    """Save an uploaded CSV to a temporary path and return it."""
    temp_dir = os.path.join(os.path.dirname(__file__), "..", "..", "_temp_uploads")
    os.makedirs(temp_dir, exist_ok=True)
    path = os.path.join(temp_dir, "uploaded_sleep_log.csv")
    with open(path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return path


def page_sleep_log():
    """Sleep Log upload and analysis page."""
    st.header("😴 Sleep Log Analysis")
    show_disclaimer()

    uploaded = st.file_uploader("Upload your sleep log CSV", type=["csv"], key="log_upload")
    if uploaded is not None:
        try:
            path = _save_uploaded_csv(uploaded)
            entries = parse_sleep_log(path)
            stats = compute_sleep_stats(entries)

            st.subheader("📋 Sleep Log Data")
            import pandas as pd
            df = pd.DataFrame(entries)
            st.dataframe(df, use_container_width=True)

            st.subheader("📊 Sleep Statistics")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Avg Duration", f"{stats['avg_duration']}h" if stats['avg_duration'] else "N/A")
                st.metric("Duration Range", f"{stats['min_duration']}–{stats['max_duration']}h" if stats['min_duration'] else "N/A")
            with col2:
                st.metric("Avg Quality", f"{stats['avg_quality']}/5" if stats['avg_quality'] else "N/A")
                st.metric("Quality Range", f"{stats['min_quality']}–{stats['max_quality']}" if stats['min_quality'] else "N/A")
            with col3:
                st.metric("Total Entries", stats['total_entries'])

        except (FileNotFoundError, ValueError) as e:
            st.error(f"Error: {e}")


def page_sleep_score():
    """Sleep Score page."""
    st.header("🏆 Sleep Score")
    show_disclaimer()

    uploaded = st.file_uploader("Upload your sleep log CSV", type=["csv"], key="score_upload")
    if uploaded is not None:
        try:
            path = _save_uploaded_csv(uploaded)
            entries = parse_sleep_log(path)
            stats = compute_sleep_stats(entries)
            result = calculate_sleep_score(stats)

            col1, col2 = st.columns(2)
            with col1:
                st.metric("Overall Score", f"{result['score']}/100")
                st.progress(result['score'] / 100)
            with col2:
                grade_colors = {"A": "🟢", "B": "🔵", "C": "🟡", "D": "🟠", "F": "🔴"}
                icon = grade_colors.get(result['grade'], "⚪")
                st.metric("Grade", f"{icon} {result['grade']}")

            st.subheader("Score Breakdown")
            breakdown = result['breakdown']
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("💤 Duration", f"{breakdown['duration']}/30")
                st.progress(breakdown['duration'] / 30)
            with col2:
                st.metric("⭐ Quality", f"{breakdown['quality']}/25")
                st.progress(breakdown['quality'] / 25)
            with col3:
                st.metric("📏 Consistency", f"{breakdown['consistency']}/20")
                st.progress(breakdown['consistency'] / 20)
            with col4:
                st.metric("🌙 Low Wake", f"{breakdown['low_wake_count']}/25")
                st.progress(breakdown['low_wake_count'] / 25)

        except (FileNotFoundError, ValueError) as e:
            st.error(f"Error: {e}")


def page_environment_checklist():
    """Environment Checklist page."""
    st.header("🏠 Sleep Environment Checklist")
    show_disclaimer()

    items = get_environment_checklist()

    priority_colors = {"high": "🔴", "medium": "🟡", "low": "🟢"}
    current_category = None

    for item in items:
        if item["category"] != current_category:
            current_category = item["category"]
            st.subheader(f"{current_category}")

        icon = priority_colors.get(item["priority"], "⚪")
        checked = st.checkbox(
            f"{icon} **{item['item']}** ({item['priority'].upper()}) — {item['recommendation']}",
            key=f"check_{item['category']}_{item['item']}",
        )


def page_routine_builder():
    """Routine Builder page."""
    st.header("🌙 Bedtime Routine Builder")
    show_disclaimer()

    col1, col2 = st.columns(2)
    with col1:
        wake_time = st.time_input("⏰ Desired Wake Time", value=None)
    with col2:
        duration = st.slider("💤 Sleep Duration (hours)", min_value=5.0, max_value=12.0, value=8.0, step=0.5)

    if wake_time is not None:
        wake_str = wake_time.strftime("%H:%M")
        result = build_bedtime_routine(wake_str, duration)

        st.subheader("Your Routine")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("⏰ Wake Time", result["wake_time"])
        with col2:
            st.metric("🛏️ Bedtime", result["bedtime"])
        with col3:
            st.metric("💤 Duration", f"{result['sleep_duration']}h")

        st.subheader("Evening Timeline")
        for step in result["routine"]:
            st.markdown(f"**{step['time']}** — {step['activity']} _{step['duration']}_")


def page_pattern_analysis():
    """Pattern Analysis page."""
    st.header("📊 Weekly Pattern Analysis")
    show_disclaimer()

    uploaded = st.file_uploader("Upload your sleep log CSV", type=["csv"], key="pattern_upload")
    if uploaded is not None:
        try:
            path = _save_uploaded_csv(uploaded)
            entries = parse_sleep_log(path)
            result = analyze_weekly_patterns(entries)

            # Day-of-week quality bar chart
            st.subheader("Sleep Quality by Day of Week")
            import pandas as pd
            day_data = []
            for day, data in result["day_averages"].items():
                if data["avg_quality"] is not None:
                    day_data.append({"Day": day, "Avg Quality": data["avg_quality"]})
            if day_data:
                df = pd.DataFrame(day_data)
                st.bar_chart(df.set_index("Day"))

            # Best and worst days
            col1, col2 = st.columns(2)
            with col1:
                st.metric("🏆 Best Day", result["best_day"] or "N/A")
            with col2:
                st.metric("⚠️ Worst Day", result["worst_day"] or "N/A")

            # Weekday vs weekend
            st.subheader("Weekday vs Weekend")
            wvw = result["weekday_vs_weekend"]
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Weekday Avg Quality", f"{wvw['weekday_avg_quality']}/5" if wvw['weekday_avg_quality'] else "N/A")
                st.metric("Weekday Avg Duration", f"{wvw['weekday_avg_duration']}h" if wvw['weekday_avg_duration'] else "N/A")
            with col2:
                st.metric("Weekend Avg Quality", f"{wvw['weekend_avg_quality']}/5" if wvw['weekend_avg_quality'] else "N/A")
                st.metric("Weekend Avg Duration", f"{wvw['weekend_avg_duration']}h" if wvw['weekend_avg_duration'] else "N/A")

            # Trend line chart
            st.subheader("Quality Trend")
            qualities = []
            for entry in entries:
                try:
                    qualities.append(float(entry.get("quality_rating", 0)))
                except (ValueError, TypeError):
                    pass
            if qualities:
                trend_df = pd.DataFrame({"Night": range(1, len(qualities) + 1), "Quality": qualities})
                st.line_chart(trend_df.set_index("Night"))

            trend_icons = {"improving": "📈 Improving", "declining": "📉 Declining", "stable": "➡️ Stable", "insufficient_data": "❓ Insufficient data"}
            st.info(f"**Trend:** {trend_icons.get(result['trend'], result['trend'])}")

        except (FileNotFoundError, ValueError) as e:
            st.error(f"Error: {e}")


def main():
    """Main Streamlit application."""
    st.title("😴 Sleep Improvement Advisor")
    show_disclaimer()

    page = st.sidebar.radio(
        "Navigation",
        [
            "😴 Sleep Log",
            "🏆 Sleep Score",
            "🏠 Environment Checklist",
            "🌙 Routine Builder",
            "📊 Pattern Analysis",
        ],
    )

    if page == "😴 Sleep Log":
        page_sleep_log()
    elif page == "🏆 Sleep Score":
        page_sleep_score()
    elif page == "🏠 Environment Checklist":
        page_environment_checklist()
    elif page == "🌙 Routine Builder":
        page_routine_builder()
    elif page == "📊 Pattern Analysis":
        page_pattern_analysis()

    st.sidebar.markdown("---")
    st.sidebar.warning(
        "⚠️ **Not medical advice.** Consult a healthcare provider for sleep disorders."
    )


if __name__ == "__main__":
    main()
