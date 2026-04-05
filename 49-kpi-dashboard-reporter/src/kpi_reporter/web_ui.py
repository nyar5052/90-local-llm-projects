"""
KPI Dashboard Reporter - Streamlit Web UI.

Provides an interactive web interface for KPI analysis with
metric cards, goal progress, trend charts, and anomaly detection.
"""

import os
import tempfile

import pandas as pd
import streamlit as st


# Custom CSS for professional dark theme
st.set_page_config(page_title="KPI Dashboard Reporter", page_icon="🎯", layout="wide")

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

from src.kpi_reporter.core import (
    compute_kpi_trends,
    compute_moving_average,
    detect_anomalies,
    load_config,
    load_kpi_data,
    safe_float,
    track_goals,
)

def main() -> None:
    """Main Streamlit application entry point."""
    st.title("📊 KPI Dashboard Reporter")

    # --- Sidebar ---
    with st.sidebar:
        st.header("⚙️ Settings")

        uploaded_file = st.file_uploader("Upload KPI CSV", type=["csv"])

        period = st.selectbox(
            "Reporting Period",
            options=["monthly", "quarterly", "yearly"],
            index=0,
        )

        st.subheader("🎯 Targets")
        st.caption("Set target values for your KPIs.")

        config = load_config()
        default_targets = config.get("targets", {})

        targets: dict[str, float] = {}
        for kpi_name, default_val in default_targets.items():
            targets[kpi_name] = st.number_input(
                f"Target: {kpi_name}",
                value=float(default_val),
                step=1.0,
                key=f"target_{kpi_name}",
            )

        custom_kpi = st.text_input("Add custom KPI target name")
        if custom_kpi:
            custom_val = st.number_input(
                f"Target: {custom_kpi}", value=0.0, step=1.0, key="target_custom"
            )
            if custom_val > 0:
                targets[custom_kpi] = custom_val

        anom_threshold = st.slider(
            "Anomaly threshold (σ)", min_value=1.0, max_value=4.0, value=2.0, step=0.5
        )

    if uploaded_file is None:
        st.info("👈 Upload a CSV file to get started.")
        return

    # Save uploaded file and load data
    tmp_dir = tempfile.mkdtemp()
    tmp_path = os.path.join(tmp_dir, "upload.csv")
    with open(tmp_path, "wb") as f:
        f.write(uploaded_file.getvalue())

    try:
        data = load_kpi_data(tmp_path)
    except (FileNotFoundError, ValueError) as e:
        st.error(f"Failed to load CSV: {e}")
        return

    trends = compute_kpi_trends(data)
    if not trends:
        st.warning("No numeric KPI columns found in the uploaded data.")
        return

    goal_results = track_goals(trends, targets) if targets else {}
    anomalies_list = detect_anomalies(trends, threshold=anom_threshold)

    # --- Tabs ---
    tab1, tab2, tab3, tab4 = st.tabs(
        ["📄 KPI Upload", "📊 Metric Cards", "🎯 Goal Progress", "📈 Trend Charts"]
    )

    # Tab 1: KPI Upload - Data Preview
    with tab1:
        st.subheader("📄 Data Preview")
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True)
        st.caption(f"Loaded **{len(data)}** rows with **{len(data[0])}** columns.")

    # Tab 2: Metric Cards
    with tab2:
        st.subheader("📊 KPI Metrics")
        cols = st.columns(min(len(trends), 4))
        for i, (kpi, info) in enumerate(trends.items()):
            with cols[i % len(cols)]:
                delta_str = f"{info['change_pct']:+.1f}%"
                st.metric(
                    label=kpi.replace("_", " ").title(),
                    value=f"{info['latest']:,.2f}",
                    delta=delta_str,
                )

        st.divider()
        st.subheader("📋 Detailed Trends")
        trend_rows = []
        for kpi, info in trends.items():
            trend_rows.append({
                "KPI": kpi,
                "Latest": info["latest"],
                "Previous": info["previous"],
                "Change": info["change"],
                "Change %": f"{info['change_pct']:.1f}%",
                "Trend": info["trend"],
                "Average": info["average"],
                "Min": info["min"],
                "Max": info["max"],
            })
        st.dataframe(pd.DataFrame(trend_rows), use_container_width=True)

    # Tab 3: Goal Progress Bars
    with tab3:
        st.subheader("🎯 Goal Tracking")
        if not goal_results:
            st.info("No targets configured. Set targets in the sidebar.")
        else:
            for kpi, info in goal_results.items():
                pct = min(info["pct_of_goal"] / 100, 1.0)
                status_emoji = {
                    "achieved": "✅",
                    "on_track": "📈",
                    "at_risk": "⚠️",
                    "behind": "🔴",
                }.get(info["status"], "❓")

                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(
                        f"**{kpi.replace('_', ' ').title()}** — "
                        f"{info['actual']:,.2f} / {info['target']:,.2f}"
                    )
                    st.progress(pct)
                with col2:
                    st.write(f"{status_emoji} {info['status'].replace('_', ' ').title()}")
                    st.write(f"**{info['pct_of_goal']:.1f}%**")

    # Tab 4: Trend Charts with Anomaly Markers
    with tab4:
        st.subheader("📈 Trend Charts")
        ma_window = config.get("moving_average", {}).get("window", 3)

        for kpi, info in trends.items():
            st.write(f"### {kpi.replace('_', ' ').title()}")
            periods = info["periods"]
            values = info["values"]
            ma_values = compute_moving_average(values, window=ma_window)

            chart_df = pd.DataFrame({
                "Period": periods,
                kpi: values,
                f"{kpi} (MA-{ma_window})": ma_values,
            }).set_index("Period")

            st.line_chart(chart_df)

            # Show anomalies for this KPI
            kpi_anomalies = [a for a in anomalies_list if a["kpi"] == kpi]
            if kpi_anomalies:
                st.warning(
                    f"⚠️ Anomalies detected: "
                    + ", ".join(
                        f"{a['period']} ({a['value']:,.2f}, {a['deviation']:.1f}σ)"
                        for a in kpi_anomalies
                    )
                )

        if not anomalies_list:
            st.success("✅ No anomalies detected across all KPIs.")


if __name__ == "__main__":
    main()
