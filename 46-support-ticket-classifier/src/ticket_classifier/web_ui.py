"""
Support Ticket Classifier - Streamlit Web UI.

Provides an interactive dashboard for classifying tickets, viewing results,
managing priority queues, and exploring analytics.
"""

import json
import os
import sys
import tempfile

import pandas as pd
import streamlit as st


# Custom CSS for professional dark theme
st.set_page_config(page_title="Support Ticket Classifier", page_icon="🎯", layout="wide")

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

# Ensure the project root is on the path so common.llm_client is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))

from ticket_classifier.core import (
    build_priority_queue,
    check_ollama_running,
    classify_ticket,
    classify_tickets_batch,
    compute_analytics,
    compute_sla_deadlines,
    find_text_column,
    load_config,
    load_tickets,
    route_to_team,
    generate_auto_response,
)

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------

PRIORITY_COLORS_HEX = {
    "critical": "#FF0000",
    "high": "#FF8C00",
    "medium": "#FFD700",
    "low": "#32CD32",
}

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------


def render_sidebar() -> dict:
    """Render the sidebar and return runtime settings."""
    st.sidebar.title("⚙️ Configuration")

    config_path = st.sidebar.text_input("Config file", value="config.yaml")
    config = load_config(config_path)

    st.sidebar.subheader("Categories")
    default_cats = ", ".join(config.get("categories", []))
    categories_input = st.sidebar.text_area("Categories (comma-separated)", value=default_cats)
    categories = [c.strip() for c in categories_input.split(",") if c.strip()]

    st.sidebar.subheader("Model Settings")
    temperature = st.sidebar.slider(
        "Temperature", 0.0, 1.0,
        value=float(config.get("model", {}).get("temperature", 0.2)),
        step=0.05,
    )

    st.sidebar.subheader("SLA Hours")
    sla = config.get("sla_hours", {})
    sla_critical = st.sidebar.number_input("Critical", value=sla.get("critical", 1), min_value=1)
    sla_high = st.sidebar.number_input("High", value=sla.get("high", 4), min_value=1)
    sla_medium = st.sidebar.number_input("Medium", value=sla.get("medium", 8), min_value=1)
    sla_low = st.sidebar.number_input("Low", value=sla.get("low", 24), min_value=1)

    # Ollama status
    st.sidebar.divider()
    if check_ollama_running():
        st.sidebar.success("✅ Ollama is running")
    else:
        st.sidebar.error("❌ Ollama is not running")

    return {
        "config": config,
        "categories": categories,
        "temperature": temperature,
        "sla_hours": {
            "critical": sla_critical,
            "high": sla_high,
            "medium": sla_medium,
            "low": sla_low,
        },
    }


# ---------------------------------------------------------------------------
# Tab 1 – Ticket Input / Upload
# ---------------------------------------------------------------------------


def render_input_tab(settings: dict) -> None:
    """Upload CSV or paste ticket text for classification."""
    st.header("📥 Ticket Input")

    input_mode = st.radio("Input mode", ["Upload CSV", "Paste single ticket"], horizontal=True)

    if input_mode == "Upload CSV":
        uploaded = st.file_uploader("Upload tickets CSV", type=["csv"])
        if uploaded is not None:
            # Save to a temporary file so core.load_tickets can read it
            tmp_dir = os.path.join(os.path.dirname(__file__), "..", "..", "uploaded_data")
            os.makedirs(tmp_dir, exist_ok=True)
            tmp_path = os.path.join(tmp_dir, uploaded.name)
            with open(tmp_path, "wb") as f:
                f.write(uploaded.getbuffer())

            tickets = load_tickets(tmp_path)
            text_col = find_text_column(tickets)
            st.success(f"Loaded **{len(tickets)}** tickets. Detected text column: **{text_col}**")
            st.dataframe(pd.DataFrame(tickets).head(10))

            if st.button("🚀 Classify All Tickets", type="primary"):
                with st.spinner("Classifying tickets..."):
                    progress = st.progress(0)

                    def on_progress(current: int, total: int) -> None:
                        progress.progress(current / total)

                    classifications = classify_tickets_batch(
                        tickets,
                        settings["categories"],
                        text_col,
                        temperature=settings["temperature"],
                        on_progress=on_progress,
                    )

                st.session_state["tickets"] = tickets
                st.session_state["classifications"] = classifications
                st.session_state["text_col"] = text_col
                st.session_state["categories"] = settings["categories"]
                st.session_state["sla_hours"] = settings["sla_hours"]
                st.success("✅ Classification complete!")

    else:
        ticket_text = st.text_area("Paste ticket text", height=150)
        if st.button("🔍 Classify Ticket", type="primary") and ticket_text.strip():
            with st.spinner("Classifying..."):
                result = classify_ticket(
                    ticket_text,
                    settings["categories"],
                    temperature=settings["temperature"],
                )

            col1, col2, col3 = st.columns(3)
            col1.metric("Category", result["category"])
            col2.metric("Priority", result["priority"].title())
            col3.metric("Confidence", f"{result['confidence']:.0%}")

            st.subheader("💬 Auto-Response")
            auto_resp = generate_auto_response(ticket_text, result)
            st.markdown(auto_resp)

            team = route_to_team(result, settings["config"].get("team_routing", {}))
            st.info(f"**Routed to:** {team}")


# ---------------------------------------------------------------------------
# Tab 2 – Classification Results
# ---------------------------------------------------------------------------


def render_results_tab(settings: dict) -> None:
    """Show classification results table with color-coded priorities."""
    st.header("📋 Classification Results")

    if "classifications" not in st.session_state:
        st.info("No results yet. Upload and classify tickets in the **Ticket Input** tab.")
        return

    tickets = st.session_state["tickets"]
    classifications = st.session_state["classifications"]
    text_col = st.session_state["text_col"]
    routing = settings["config"].get("team_routing", {})

    rows = []
    for i, (ticket, clf) in enumerate(zip(tickets, classifications), 1):
        team = route_to_team(clf, routing)
        rows.append({
            "#": i,
            "Ticket": str(ticket.get(text_col, ""))[:100],
            "Category": clf.get("category", ""),
            "Priority": clf.get("priority", "medium").title(),
            "Confidence": f"{clf.get('confidence', 0.5):.0%}",
            "Team": team,
            "Response": str(clf.get("suggested_response", ""))[:80],
        })

    df = pd.DataFrame(rows)

    def color_priority(val: str) -> str:
        colors = {
            "Critical": "background-color: #FF000040",
            "High": "background-color: #FF8C0040",
            "Medium": "background-color: #FFD70040",
            "Low": "background-color: #32CD3240",
        }
        return colors.get(val, "")

    styled = df.style.map(color_priority, subset=["Priority"])
    st.dataframe(styled, use_container_width=True, hide_index=True)


# ---------------------------------------------------------------------------
# Tab 3 – Priority Queue
# ---------------------------------------------------------------------------


def render_queue_tab(settings: dict) -> None:
    """Display priority-sorted queue with SLA countdown."""
    st.header("🚨 Priority Queue")

    if "classifications" not in st.session_state:
        st.info("No results yet. Upload and classify tickets first.")
        return

    tickets = st.session_state["tickets"]
    classifications = st.session_state["classifications"]
    text_col = st.session_state["text_col"]

    queue = build_priority_queue(
        tickets, classifications, text_col,
        priority_weights=settings["config"].get("priority_weights"),
    )

    sla_deadlines = compute_sla_deadlines(
        classifications, settings["sla_hours"],
    )

    rows = []
    for item, sla in zip(queue, sla_deadlines):
        rows.append({
            "Position": item["position"],
            "Ticket": item["ticket_text"],
            "Category": item["category"],
            "Priority": item["priority"].title(),
            "Weight": item["weight"],
            "SLA (hrs)": sla["sla_hours"],
            "Remaining (hrs)": sla["remaining_hours"],
            "Deadline": sla["deadline"],
        })

    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)

    # SLA metrics
    st.subheader("⏱️ SLA Overview")
    col1, col2, col3, col4 = st.columns(4)
    priorities = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    for clf in classifications:
        p = clf.get("priority", "medium").lower()
        priorities[p] = priorities.get(p, 0) + 1
    col1.metric("🔴 Critical", priorities["critical"])
    col2.metric("🟠 High", priorities["high"])
    col3.metric("🟡 Medium", priorities["medium"])
    col4.metric("🟢 Low", priorities["low"])


# ---------------------------------------------------------------------------
# Tab 4 – Analytics Dashboard
# ---------------------------------------------------------------------------


def render_analytics_tab(settings: dict) -> None:
    """Display analytics dashboard with charts and metrics."""
    st.header("📊 Analytics Dashboard")

    if "classifications" not in st.session_state:
        st.info("No results yet. Upload and classify tickets first.")
        return

    classifications = st.session_state["classifications"]
    categories = st.session_state.get("categories", settings["categories"])
    analytics = compute_analytics(classifications, categories)

    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Tickets", analytics["total_tickets"])
    col2.metric("Avg Confidence", f"{analytics['avg_confidence']:.1%}")
    col3.metric("SLA Compliance", f"{analytics['sla_compliance']:.1f}%")
    col4.metric("High Priority", analytics["high_priority_count"])

    st.divider()

    # Charts side by side
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.subheader("Category Distribution")
        cat_df = pd.DataFrame(
            list(analytics["category_distribution"].items()),
            columns=["Category", "Count"],
        )
        st.bar_chart(cat_df.set_index("Category"))

    with chart_col2:
        st.subheader("Priority Distribution")
        pri_df = pd.DataFrame(
            list(analytics["priority_distribution"].items()),
            columns=["Priority", "Count"],
        )
        st.bar_chart(pri_df.set_index("Priority"))

    # Detailed breakdown
    st.divider()
    st.subheader("📈 Detailed Breakdown")

    detail_col1, detail_col2 = st.columns(2)

    with detail_col1:
        st.write("**Category Counts**")
        st.dataframe(cat_df, hide_index=True, use_container_width=True)

    with detail_col2:
        st.write("**Priority Counts**")
        st.dataframe(pri_df, hide_index=True, use_container_width=True)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    """Entry point for the Streamlit web UI."""
    st.title("🎫 Support Ticket Classifier")
    st.caption("AI-powered ticket classification with priority queue & SLA tracking")

    settings = render_sidebar()

    tab1, tab2, tab3, tab4 = st.tabs([
        "📥 Ticket Input",
        "📋 Results",
        "🚨 Priority Queue",
        "📊 Analytics",
    ])

    with tab1:
        render_input_tab(settings)
    with tab2:
        render_results_tab(settings)
    with tab3:
        render_queue_tab(settings)
    with tab4:
        render_analytics_tab(settings)


if __name__ == "__main__":
    main()
