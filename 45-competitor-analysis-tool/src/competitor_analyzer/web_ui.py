"""Streamlit Web UI for Competitor Analysis Tool."""

import sys
import os
import json
import logging

import streamlit as st
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.competitor_analyzer.core import (
    load_config,
    generate_swot,
    generate_feature_matrix,
    generate_pricing_comparison,
    generate_market_positioning,
    generate_action_items,
    generate_comparison,
    generate_recommendations,
)

logger = logging.getLogger(__name__)

st.set_page_config(page_title="Competitor Analysis Tool", page_icon="🏢", layout="wide")


def render_header():
    """Render the application header."""
    st.title("🏢 Competitor Analysis Tool")
    st.markdown("*SWOT analysis, feature comparison, and market positioning — powered by local LLM*")
    st.divider()


def render_company_inputs():
    """Render company input section."""
    st.sidebar.header("🏢 Company Setup")
    company = st.sidebar.text_input("Your Company/Product", placeholder="e.g., Acme Corp")
    competitors_str = st.sidebar.text_area("Competitors (one per line)",
                                            placeholder="Competitor A\nCompetitor B\nCompetitor C")
    industry = st.sidebar.text_input("Industry", placeholder="e.g., SaaS, E-commerce")

    competitors = [c.strip() for c in competitors_str.split("\n") if c.strip()]

    if company and competitors and industry:
        st.sidebar.success(f"✅ {company} vs {len(competitors)} competitors")
        return company, competitors, industry
    return None, None, None


def render_swot_cards(swot: dict, company: str):
    """Render SWOT analysis as cards."""
    st.subheader(f"📊 SWOT Analysis — {company}")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 💪 Strengths")
        for s in swot.get("strengths", []):
            st.success(f"✅ {s}")

        st.markdown("### 🎯 Opportunities")
        for o in swot.get("opportunities", []):
            st.info(f"🔵 {o}")

    with col2:
        st.markdown("### ⚠️ Weaknesses")
        for w in swot.get("weaknesses", []):
            st.error(f"🔴 {w}")

        st.markdown("### 🔥 Threats")
        for t in swot.get("threats", []):
            st.warning(f"🟡 {t}")


def render_feature_matrix_table(features: dict):
    """Render feature comparison matrix table."""
    with st.expander("📋 Feature Matrix", expanded=True):
        if not features.get("features") or not features.get("matrix"):
            st.warning("Feature matrix unavailable.")
            return

        emoji_map = {"yes": "✅", "no": "❌", "partial": "🔶"}

        data = []
        for feat in features["features"]:
            row = {"Feature": feat}
            for company, vals in features["matrix"].items():
                val = vals.get(feat, "N/A")
                row[company] = emoji_map.get(str(val).lower(), str(val))
            data.append(row)

        st.dataframe(pd.DataFrame(data).set_index("Feature"), use_container_width=True)

        if features.get("summary"):
            st.caption(features["summary"])


def render_pricing_comparison(pricing: dict):
    """Render pricing comparison."""
    with st.expander("💰 Pricing Comparison", expanded=False):
        if not pricing.get("companies"):
            st.warning("Pricing comparison unavailable.")
            return

        data = []
        for c in pricing["companies"]:
            data.append({
                "Company": c.get("name", "N/A"),
                "Model": c.get("pricing_model", "N/A"),
                "Price Range": c.get("price_range", "N/A"),
                "Tier": c.get("tier", "N/A"),
                "Value Proposition": c.get("value_proposition", "N/A"),
            })
        st.dataframe(pd.DataFrame(data), use_container_width=True)

        if pricing.get("recommendation"):
            st.info(f"💡 **Recommendation:** {pricing['recommendation']}")


def render_positioning_chart(positioning: dict):
    """Render market positioning chart."""
    with st.expander("🗺️ Market Positioning", expanded=False):
        if not positioning.get("positions"):
            st.warning("Positioning data unavailable.")
            return

        data = []
        for p in positioning["positions"]:
            data.append({
                "Company": p.get("company", "N/A"),
                "Price (x)": p.get("x_axis", 5),
                "Quality (y)": p.get("y_axis", 5),
                "Quadrant": p.get("quadrant", "N/A"),
            })

        df = pd.DataFrame(data)
        st.scatter_chart(df, x="Price (x)", y="Quality (y)")
        st.dataframe(df, use_container_width=True)

        if positioning.get("market_gaps"):
            st.markdown("**Market Gaps:**")
            for gap in positioning["market_gaps"]:
                st.markdown(f"- 🎯 {gap}")


def render_action_items(company: str, competitors: list, industry: str, swot: dict):
    """Render action items section."""
    with st.expander("🎯 Action Items", expanded=False):
        if st.button("Generate Action Items"):
            with st.spinner("Generating action items..."):
                items = generate_action_items(company, competitors, industry, swot)
                if items:
                    for i, item in enumerate(items, 1):
                        priority = item.get("priority", "medium")
                        colors = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}
                        icon = colors.get(priority, "⚪")
                        st.markdown(f"### {icon} {i}. {item.get('title', 'Action')}")
                        st.markdown(item.get("description", ""))
                        col1, col2, col3 = st.columns(3)
                        col1.info(f"**Priority:** {priority.title()}")
                        col2.info(f"**Timeline:** {item.get('timeline', 'N/A').title()}")
                        col3.info(f"**Category:** {item.get('category', 'N/A').title()}")
                        st.divider()
                else:
                    st.warning("Could not generate action items.")


def main():
    """Main Streamlit application."""
    load_config()
    render_header()

    company, competitors, industry = render_company_inputs()

    if company and competitors and industry:
        if "comp_swot" not in st.session_state or st.sidebar.button("🔄 Re-analyze"):
            with st.spinner("Generating SWOT analysis..."):
                swot = generate_swot(company, competitors, industry)
                st.session_state["comp_swot"] = swot

            with st.spinner("Generating feature matrix..."):
                features = generate_feature_matrix(company, competitors, industry)
                st.session_state["comp_features"] = features

            with st.spinner("Analyzing pricing..."):
                pricing = generate_pricing_comparison(company, competitors, industry)
                st.session_state["comp_pricing"] = pricing

            with st.spinner("Mapping market position..."):
                positioning = generate_market_positioning(company, competitors, industry)
                st.session_state["comp_positioning"] = positioning

        swot = st.session_state.get("comp_swot", {})
        features = st.session_state.get("comp_features", {})
        pricing = st.session_state.get("comp_pricing", {})
        positioning = st.session_state.get("comp_positioning", {})

        render_swot_cards(swot, company)
        st.divider()
        render_feature_matrix_table(features)
        render_pricing_comparison(pricing)
        render_positioning_chart(positioning)
        render_action_items(company, competitors, industry, swot)
    else:
        st.info("👈 Enter your company, competitors, and industry to get started!")
        st.markdown("""
        ### Features
        - 📊 **SWOT analysis** — comprehensive strengths, weaknesses, opportunities, threats
        - 📋 **Feature matrix** — detailed feature-by-feature comparison
        - 💰 **Pricing comparison** — pricing model and tier analysis
        - 🗺️ **Market positioning** — visual positioning map
        - 🎯 **Action items** — prioritized strategic action items
        """)


if __name__ == "__main__":
    main()
