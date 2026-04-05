"""Streamlit Web UI for Stock Report Generator."""

import sys
import os
import json
import logging

import streamlit as st
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.stock_reporter.core import (
    load_config,
    load_stock_data,
    compute_metrics,
    compute_technical_indicators,
    assess_risk,
    compare_tickers,
    generate_report,
)

logger = logging.getLogger(__name__)

# Custom CSS for professional dark theme
st.set_page_config(page_title="Stock Report Generator", page_icon="🎯", layout="wide")

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


def render_header():
    """Render the application header."""
    st.title("📈 Stock Report Generator")
    st.markdown("*Professional stock analysis reports — powered by local LLM*")
    st.divider()


def render_ticker_input():
    """Render ticker input section."""
    st.sidebar.header("📊 Stock Data")
    ticker = st.sidebar.text_input("Ticker Symbol", value="AAPL").upper()
    uploaded_file = st.sidebar.file_uploader("Upload stock data CSV", type=["csv"])

    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            data = df.to_dict("records")
            if not data:
                st.sidebar.error("CSV file is empty.")
                return None, None, None
            st.sidebar.success(f"✅ Loaded: {len(data)} data points")
            return ticker, data, df
        except Exception as e:
            st.sidebar.error(f"Error: {e}")
    return ticker, None, None


def render_report_sections(metrics: dict, ticker: str):
    """Render report metric sections."""
    st.subheader(f"📊 {ticker} — Key Metrics")

    col1, col2, col3, col4 = st.columns(4)
    change = metrics["change_percent"]
    col1.metric("Current Price", f"${metrics['current_price']:.2f}",
                f"{change:+.2f}%")
    col2.metric("Period High", f"${metrics['period_high']:.2f}")
    col3.metric("Period Low", f"${metrics['period_low']:.2f}")
    col4.metric("Avg Daily Return", f"{metrics['avg_daily_return']:.3f}%")

    col5, col6, col7, col8 = st.columns(4)
    col5.metric("SMA (5)", f"${metrics['sma_5']:.2f}")
    col6.metric("SMA (20)", f"${metrics['sma_20']:.2f}")
    col7.metric("Volatility", f"${metrics['volatility']:.2f}")
    col8.metric("Up/Down Days", f"{metrics['positive_days']}/{metrics['negative_days']}")


def render_indicators(indicators: dict):
    """Render technical indicators."""
    with st.expander("📈 Technical Indicators", expanded=True):
        if indicators.get("rsi") is None:
            st.warning("Need at least 14 data points for technical indicators.")
            return

        col1, col2, col3 = st.columns(3)

        rsi = indicators["rsi"]
        rsi_color = "🔴" if rsi > 70 else ("🟢" if rsi < 30 else "🟡")
        col1.metric(f"{rsi_color} RSI (14)", f"{rsi}", indicators["rsi_signal"].title())

        col2.metric("MACD Line", f"{indicators['macd_line']:.2f}",
                     indicators["macd_signal"].title())

        bb = indicators.get("bollinger", {})
        col3.metric("Bollinger Middle", f"${bb.get('middle', 0):.2f}",
                     f"Band: ${bb.get('lower', 0):.2f} — ${bb.get('upper', 0):.2f}")


def render_risk_meter(risk: dict):
    """Render risk assessment gauge."""
    with st.expander("⚠️ Risk Assessment", expanded=True):
        score = risk["risk_score"]
        level = risk["risk_level"]
        color_map = {"low": "🟢", "medium": "🟡", "high": "🔴"}

        st.metric(f"{color_map.get(level, '⚪')} Risk Level",
                  level.upper(), f"Score: {score}/100")

        st.progress(score / 100)

        if risk["risk_factors"]:
            st.markdown("**Risk Factors:**")
            for f in risk["risk_factors"]:
                st.markdown(f"- ⚠️ {f}")
        else:
            st.success("No significant risk factors identified.")


def render_comparison(datasets: dict):
    """Render multi-ticker comparison."""
    with st.expander("📊 Multi-Ticker Comparison", expanded=True):
        comparison = compare_tickers(datasets)
        if comparison:
            comp_data = []
            for tkr, m in comparison.items():
                comp_data.append({
                    "Ticker": tkr,
                    "Price": f"${m['current_price']:.2f}",
                    "Change %": f"{m['change_percent']:.2f}%",
                    "Volatility": f"${m['volatility']:.2f}",
                    "Avg Return": f"{m['avg_daily_return']:.3f}%",
                })
            st.dataframe(pd.DataFrame(comp_data), use_container_width=True)


def render_price_chart(df: pd.DataFrame):
    """Render price chart."""
    with st.expander("📉 Price Chart", expanded=True):
        close_col = None
        for c in ["Close", "close", "Adj Close", "price", "Price"]:
            if c in df.columns:
                close_col = c
                break
        if close_col:
            date_col = None
            for c in ["Date", "date", "Timestamp", "timestamp"]:
                if c in df.columns:
                    date_col = c
                    break
            if date_col:
                chart_df = df[[date_col, close_col]].copy()
                chart_df[date_col] = pd.to_datetime(chart_df[date_col])
                st.line_chart(chart_df.set_index(date_col))
            else:
                st.line_chart(df[close_col])
        else:
            st.warning("Could not identify price column for chart.")


def render_llm_report(data: list, metrics: dict, ticker: str,
                       indicators: dict, risk: dict):
    """Render LLM-generated analysis report."""
    with st.expander("📋 AI Analysis Report", expanded=False):
        if st.button("🤖 Generate Report"):
            with st.spinner("Generating analysis report..."):
                try:
                    report = generate_report(data, metrics, ticker, indicators, risk)
                    st.markdown(report)
                except Exception as e:
                    st.error(f"Report generation failed: {e}")


def main():
    """Main Streamlit application."""
    load_config()
    render_header()

    ticker, data, df = render_ticker_input()

    if data is not None and df is not None:
        metrics = compute_metrics(data)
        if "error" in metrics:
            st.error(metrics["error"])
            return

        render_report_sections(metrics, ticker)
        st.divider()
        render_price_chart(df)

        indicators = compute_technical_indicators(data)
        render_indicators(indicators)

        risk = assess_risk(metrics, indicators)
        render_risk_meter(risk)

        render_llm_report(data, metrics, ticker, indicators, risk)
    else:
        st.info("👈 Upload stock data CSV and enter a ticker symbol to get started!")
        st.markdown("""
        ### Features
        - 📊 **Technical metrics** — SMA, volatility, daily returns
        - 📈 **Technical indicators** — RSI, Bollinger Bands, MACD
        - ⚠️ **Risk assessment** — automated risk scoring and factor analysis
        - 📉 **Price charts** — interactive price visualization
        - 🤖 **AI reports** — comprehensive narrative analysis
        - 📊 **Multi-ticker comparison** — compare stocks side by side
        """)


if __name__ == "__main__":
    main()
