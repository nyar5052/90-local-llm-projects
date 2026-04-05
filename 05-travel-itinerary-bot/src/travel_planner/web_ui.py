"""Streamlit web interface for Travel Itinerary Bot."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

import streamlit as st

from .config import load_config, setup_logging
from .core import (
    check_ollama_running,
    generate_itinerary,
    generate_multi_destination_itinerary,
    get_place_details,
    generate_budget_breakdown,
    generate_packing_list,
    BUDGETS,
)
from .utils import parse_destinations, parse_budget_items, save_itinerary, load_saved_itineraries

# Custom CSS for professional dark theme
st.set_page_config(page_title="Travel Itinerary Bot", page_icon="🎯", layout="wide")

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


def init_state():
    defaults = {
        "config": load_config(),
        "itinerary": "",
        "budget_breakdown": "",
        "packing_list": "",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def sidebar():
    cfg = st.session_state.config
    st.sidebar.title("⚙️ Settings")
    cfg["model"]["name"] = st.sidebar.text_input("Model", value=cfg["model"]["name"])
    cfg["model"]["temperature"] = st.sidebar.slider("Temperature", 0.0, 1.0, cfg["model"]["temperature"], 0.1)

    st.sidebar.markdown("---")
    st.sidebar.subheader("📜 Saved Itineraries")
    saved = load_saved_itineraries(cfg.get("storage", {}).get("itineraries_file", "saved_itineraries.json"))
    if saved:
        for s in saved[-5:]:
            st.sidebar.markdown(f"- **{s['destination']}** ({s['days']}d, {s['budget']})")
    else:
        st.sidebar.info("No saved itineraries.")


def main():
    init_state()
    cfg = st.session_state.config
    setup_logging(cfg)
    storage_cfg = cfg.get("storage", {})

    st.title("✈️ Travel Itinerary Bot")
    st.caption("Plan your perfect vacation with AI — supports multi-destination trips.")

    sidebar()

    tab_plan, tab_budget, tab_pack, tab_place = st.tabs(["🗺️ Itinerary", "💰 Budget", "🎒 Packing List", "📍 Place Details"])

    with tab_plan:
        col1, col2, col3 = st.columns(3)
        destination = col1.text_input("Destination(s)", placeholder="Tokyo, Kyoto, Osaka")
        days = col2.number_input("Days (per destination)", 1, 30, 5)
        budget = col3.selectbox("Budget Level", BUDGETS, index=1)

        col4, col5 = st.columns(2)
        interests = col4.text_input("Interests", placeholder="food, culture, nature...")
        travelers = col5.number_input("Travelers", 1, 20, 1)

        if st.button("✈️ Generate Itinerary", type="primary") and destination:
            if not check_ollama_running():
                st.error("❌ Ollama is not running.")
                return
            destinations = parse_destinations(destination)
            with st.spinner(f"Planning your {' → '.join(destinations)} trip..."):
                if len(destinations) > 1:
                    itin = generate_multi_destination_itinerary(
                        destinations, days, budget, interests or None, travelers,
                        model=cfg["model"]["name"], temperature=cfg["model"]["temperature"],
                    )
                else:
                    itin = generate_itinerary(
                        destinations[0], days, budget, interests or None, travelers,
                        model=cfg["model"]["name"], temperature=cfg["model"]["temperature"],
                    )
                st.session_state.itinerary = itin
                save_itinerary(
                    " → ".join(destinations), days, budget, itin,
                    storage_cfg.get("itineraries_file", "saved_itineraries.json"),
                )

        if st.session_state.itinerary:
            st.markdown(st.session_state.itinerary)

            # Map placeholder
            st.markdown("---")
            st.subheader("🗺️ Map")
            st.info("Map visualization would appear here. Integrate with folium or pydeck for interactive maps.")

    with tab_budget:
        if st.session_state.itinerary:
            if st.button("💰 Generate Budget Breakdown"):
                with st.spinner("Calculating budget..."):
                    bd = generate_budget_breakdown(
                        st.session_state.itinerary, budget, travelers,
                        model=cfg["model"]["name"],
                    )
                    st.session_state.budget_breakdown = bd
            if st.session_state.budget_breakdown:
                st.markdown(st.session_state.budget_breakdown)
                items = parse_budget_items(st.session_state.budget_breakdown)
                if items:
                    st.markdown("---")
                    st.subheader("📊 Budget Chart")
                    import pandas as pd
                    df = pd.DataFrame(items)
                    st.bar_chart(df.set_index("category"))
        else:
            st.info("Generate an itinerary first to get a budget breakdown.")

    with tab_pack:
        if st.button("🎒 Generate Packing List") and destination:
            with st.spinner("Creating packing list..."):
                pl = generate_packing_list(
                    destination, days, interests or None,
                    model=cfg["model"]["name"],
                )
                st.session_state.packing_list = pl
        if st.session_state.packing_list:
            st.markdown(st.session_state.packing_list)
        elif not destination:
            st.info("Enter a destination above first.")

    with tab_place:
        place = st.text_input("Place or attraction name")
        dest_ctx = st.text_input("In which city/country?", value=destination if destination else "")
        if st.button("📍 Get Details") and place and dest_ctx:
            with st.spinner(f"Looking up {place}..."):
                details = get_place_details(place, dest_ctx, model=cfg["model"]["name"])
            st.markdown(details)


if __name__ == "__main__":
    main()
