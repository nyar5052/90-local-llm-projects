#!/usr/bin/env python3
"""Streamlit web interface for Smart Calendar Assistant."""

import sys
import os
import json
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

import streamlit as st

from calendar_assistant.core import (
    load_schedule,
    display_schedule,
    optimize_schedule,
    suggest_meeting_time,
    analyze_workload,
    detect_conflicts,
    score_priority,
    generate_daily_agenda,
    load_config,
    get_config,
)

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------

st.set_page_config(page_title="Smart Calendar Assistant", page_icon="📅", layout="wide")

# ---------------------------------------------------------------------------
# Session state defaults
# ---------------------------------------------------------------------------

if "events" not in st.session_state:
    st.session_state.events = []

config = get_config()

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

st.sidebar.title("📅 Smart Calendar Assistant")
page = st.sidebar.radio(
    "Navigation",
    ["Calendar View", "Add Event", "Daily Agenda", "Optimization", "Conflict Detection", "Workload Analysis"],
)

uploaded = st.sidebar.file_uploader("Load schedule JSON", type=["json"])
if uploaded is not None:
    try:
        st.session_state.events = json.loads(uploaded.read().decode("utf-8"))
        st.sidebar.success(f"Loaded {len(st.session_state.events)} events")
    except json.JSONDecodeError:
        st.sidebar.error("Invalid JSON file")

st.sidebar.markdown("---")
st.sidebar.caption(f"v{config['app']['version']}  •  TZ: {config['calendar']['default_timezone']}")

# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------

events = st.session_state.events


def _calendar_view() -> None:
    st.header("📅 Calendar View")
    if not events:
        st.info("No events loaded. Upload a schedule JSON from the sidebar.")
        return
    for ev in events:
        pri = ev.get("priority", "medium").lower()
        color_map = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢", "optional": "⚪"}
        icon = color_map.get(pri, "🟡")
        with st.expander(f"{icon} {ev.get('title', 'Untitled')}  —  {ev.get('start', '')} → {ev.get('end', '')}"):
            st.write(f"**Priority:** {pri.upper()}")
            st.write(f"**Attendees:** {', '.join(ev.get('attendees', [])) if isinstance(ev.get('attendees'), list) else ev.get('attendees', 'N/A')}")
            st.write(f"**Location:** {ev.get('location', 'N/A')}")
            st.write(f"**Description:** {ev.get('description', 'N/A')}")
            st.write(f"**Priority Score:** {score_priority(ev)}")


def _add_event() -> None:
    st.header("➕ Add Event")
    with st.form("add_event_form"):
        title = st.text_input("Title")
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start date")
            start_time = st.time_input("Start time")
        with col2:
            end_date = st.date_input("End date")
            end_time = st.time_input("End time")
        priority = st.selectbox("Priority", ["critical", "high", "medium", "low", "optional"])
        attendees = st.text_input("Attendees (comma-separated)")
        location = st.text_input("Location")
        description = st.text_area("Description")
        submitted = st.form_submit_button("Add Event")
        if submitted and title:
            new_event = {
                "title": title,
                "start": f"{start_date}T{start_time}",
                "end": f"{end_date}T{end_time}",
                "priority": priority,
                "attendees": [a.strip() for a in attendees.split(",") if a.strip()],
                "location": location,
                "description": description,
            }
            st.session_state.events.append(new_event)
            st.success(f"Added event: {title}")


def _daily_agenda() -> None:
    st.header("📋 Daily Agenda")
    if not events:
        st.info("No events loaded.")
        return
    date_str = st.date_input("Select date").isoformat()
    agenda_items = generate_daily_agenda(events, date_str)
    if not agenda_items:
        st.warning("No events for the selected date.")
        return
    for ev in agenda_items:
        st.markdown(
            f"**{ev.get('start', '')} – {ev.get('end', '')}** | "
            f"{ev.get('title', 'Untitled')} | "
            f"Priority: {ev.get('priority', 'medium').upper()} (score {ev.get('priority_score', '')})"
        )


def _optimization() -> None:
    st.header("✨ Schedule Optimization")
    if not events:
        st.info("No events loaded.")
        return
    if st.button("Optimize Schedule"):
        with st.spinner("Consulting AI…"):
            result = optimize_schedule(events)
        st.markdown(result)

    st.markdown("---")
    st.subheader("💡 Suggest Meeting Time")
    duration = st.number_input("Duration (minutes)", min_value=5, max_value=480, value=30, step=5)
    attendees = st.text_input("Attendees (comma-separated)", key="suggest_att")
    if st.button("Suggest Time"):
        with st.spinner("Finding optimal slot…"):
            result = suggest_meeting_time(events, int(duration), attendees or None)
        st.markdown(result)


def _conflict_detection() -> None:
    st.header("⚠️ Conflict Detection")
    if not events:
        st.info("No events loaded.")
        return
    pairs = detect_conflicts(events)
    if not pairs:
        st.success("No conflicts found! ✅")
        return
    st.error(f"Found {len(pairs)} conflict(s)")
    for a, b in pairs:
        st.markdown(
            f"- **{a.get('title', '?')}** ({a.get('start', '')} – {a.get('end', '')}) ↔ "
            f"**{b.get('title', '?')}** ({b.get('start', '')} – {b.get('end', '')})"
        )


def _workload_analysis() -> None:
    st.header("📊 Workload Analysis")
    if not events:
        st.info("No events loaded.")
        return
    if st.button("Analyze Workload"):
        with st.spinner("Analyzing…"):
            result = analyze_workload(events)
        st.markdown(result)


# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------

_PAGES = {
    "Calendar View": _calendar_view,
    "Add Event": _add_event,
    "Daily Agenda": _daily_agenda,
    "Optimization": _optimization,
    "Conflict Detection": _conflict_detection,
    "Workload Analysis": _workload_analysis,
}

_PAGES[page]()
