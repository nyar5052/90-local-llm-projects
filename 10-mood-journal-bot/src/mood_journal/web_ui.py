"""Streamlit web interface for Mood Journal Bot."""

import streamlit as st
from datetime import datetime
from collections import Counter

from .core import (
    add_entry, get_recent_entries, analyze_entries, load_entries,
    generate_weekly_report, generate_monthly_report, get_gratitude_prompt,
    get_mood_stats, export_entries, check_ollama_running,
    MOODS,
)
from .utils import setup_logging

setup_logging()


def main():
    """Main Streamlit application."""
    st.set_page_config(page_title="📔 Mood Journal Bot", page_icon="📔", layout="wide")
    st.title("📔 Mood Journal Bot")
    st.caption("Track your moods and discover patterns with AI insights")

    # Sidebar
    with st.sidebar:
        st.header("📊 Overview")
        stats = get_mood_stats()
        if stats["total"] > 0:
            col1, col2 = st.columns(2)
            col1.metric("Total Entries", stats["total"])
            col2.metric("Avg Energy", f"{stats['avg_energy']}/10")
        else:
            st.info("No entries yet")

        st.divider()
        if not check_ollama_running():
            st.error("❌ Ollama is not running")
            return

    tab_journal, tab_chart, tab_insights, tab_export = st.tabs(
        ["📝 Journal", "📊 Mood Chart", "🧠 Insights", "📤 Export"]
    )

    # --- Journal Tab ---
    with tab_journal:
        st.subheader("📝 New Entry")

        mood_options = {f"{emoji} {name}": key for key, (emoji, name, _) in MOODS.items()}
        selected_mood = st.selectbox("How are you feeling?", list(mood_options.keys()))
        mood_key = mood_options[selected_mood]

        energy = st.slider("Energy Level", 1, 10, 5)
        text = st.text_area("What's on your mind?", placeholder="Share your thoughts...")
        gratitude = st.text_input("🙏 What are you grateful for? (optional)")

        if st.button("💾 Save Entry", type="primary") and text:
            entry = add_entry(mood_key, text, energy, gratitude)
            emoji, mood_name, _ = MOODS[mood_key]
            st.success(f"✅ Entry saved: {emoji} {mood_name}")
            st.rerun()

        # Gratitude prompt
        st.divider()
        if st.button("🙏 Get Gratitude Prompt"):
            with st.spinner("Generating prompt..."):
                prompt = get_gratitude_prompt()
            st.info(prompt)

        # Recent entries
        st.divider()
        st.subheader("📖 Recent Entries")
        days = st.selectbox("Show entries from last", [7, 14, 30, 90], index=0)
        entries = get_recent_entries(days)
        if entries:
            for e in reversed(entries[-10:]):
                with st.expander(f"{e['date']} {e['time']} — {e['mood_emoji']} {e['mood']} (Energy: {e['energy_level']}/10)"):
                    st.write(e["text"])
                    if e.get("gratitude"):
                        st.write(f"🙏 **Grateful for:** {e['gratitude']}")
        else:
            st.info("No entries yet. Add one above!")

    # --- Mood Chart Tab ---
    with tab_chart:
        st.subheader("📊 Mood & Energy Trends")
        chart_days = st.slider("Days to display", 7, 90, 30, key="chart_days")
        entries = get_recent_entries(chart_days)

        if entries:
            # Mood score over time
            import pandas as pd
            df = pd.DataFrame(entries)
            df["date"] = pd.to_datetime(df["date"])

            st.subheader("Mood Score Over Time")
            chart_data = df[["date", "mood_score"]].set_index("date")
            st.line_chart(chart_data)

            st.subheader("Energy Level Over Time")
            energy_data = df[["date", "energy_level"]].set_index("date")
            st.line_chart(energy_data)

            # Mood distribution
            st.subheader("Mood Distribution")
            mood_counts = Counter(e["mood"] for e in entries)
            st.bar_chart(mood_counts)
        else:
            st.info("Not enough data for charts. Keep journaling!")

    # --- Insights Tab ---
    with tab_insights:
        st.subheader("🧠 AI-Powered Insights")
        analysis_days = st.selectbox("Analyze entries from last", [7, 14, 30], index=0, key="analysis_days")

        if st.button("🔍 Analyze Moods", type="primary"):
            entries = get_recent_entries(analysis_days)
            if entries:
                with st.spinner("Analyzing your mood patterns..."):
                    analysis = analyze_entries(entries)
                st.markdown(analysis)
            else:
                st.warning("No entries to analyze.")

        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("📊 Weekly Report")
            if st.button("Generate Weekly Report"):
                entries = get_recent_entries(7)
                report = generate_weekly_report(entries)
                st.markdown(report)
        with col2:
            st.subheader("📊 Monthly Report")
            if st.button("Generate Monthly Report"):
                report = generate_monthly_report()
                st.markdown(report)

        # Stats
        st.divider()
        st.subheader("📊 All-Time Statistics")
        stats = get_mood_stats()
        if stats["total"] > 0:
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Entries", stats["total"])
            col2.metric("Average Energy", f"{stats['avg_energy']}/10")
            col3.metric("Date Range", f"{stats['first_date']} to {stats['last_date']}")

            st.dataframe(
                [{"Mood": mood, "Count": count,
                  "Percentage": f"{(count / stats['total']) * 100:.1f}%"}
                 for mood, count in sorted(stats["mood_counts"].items(),
                                           key=lambda x: x[1], reverse=True)],
                use_container_width=True,
            )

    # --- Export Tab ---
    with tab_export:
        st.subheader("📤 Export Journal")
        export_days = st.number_input("Export last N days (0 for all)", min_value=0, value=0)

        if st.button("📥 Export to CSV"):
            output_path = "journal_export.csv"
            count = export_entries(output_path, export_days if export_days > 0 else None)
            st.success(f"Exported {count} entries to {output_path}")

            entries = load_entries()
            if entries:
                import json
                st.download_button(
                    "📥 Download JSON",
                    data=json.dumps(entries, indent=2, ensure_ascii=False),
                    file_name="journal_entries.json",
                    mime="application/json",
                )


if __name__ == "__main__":
    main()
