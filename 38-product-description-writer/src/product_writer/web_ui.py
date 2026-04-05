"""Streamlit Web UI for Product Description Writer."""

import sys
import os
import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))

from product_writer.core import (
    generate_descriptions,
    generate_ab_variants,
    load_config,
    get_platform_configs,
    map_features_to_benefits,
    calculate_seo_score,
    PLATFORM_CONFIGS,
    LENGTH_GUIDE,
)

# Custom CSS for professional dark theme
st.set_page_config(page_title="Product Description Writer", page_icon="🎯", layout="wide")

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


def main():
    st.title("🛒 Product Description Writer")
    st.markdown("*Generate SEO-optimized e-commerce product descriptions with AI*")

    config = load_config("config.yaml")
    platforms = get_platform_configs()

    tab1, tab2, tab3, tab4 = st.tabs(["📝 Product Form", "🏪 Platform Tabs", "📄 Generated Descriptions", "📊 SEO Score"])

    with tab1:
        col1, col2 = st.columns([1, 1])
        with col1:
            st.subheader("Product Details")
            product = st.text_input("Product Name", placeholder="e.g., Wireless Noise-Canceling Headphones")
            features_text = st.text_area("Key Features (one per line)", height=150, placeholder="Noise canceling\nBluetooth 5.3\n40-hour battery\nFoldable design")
            keywords_text = st.text_input("SEO Keywords (comma-separated)", placeholder="wireless headphones, noise canceling, bluetooth")
        with col2:
            st.subheader("Settings")
            platform_keys = list(platforms.keys())
            platform = st.selectbox("Platform", platform_keys, format_func=lambda x: f"{platforms[x]['icon']} {platforms[x]['name']}")
            length = st.selectbox("Description Length", list(LENGTH_GUIDE.keys()), format_func=lambda x: f"{x.title()} ({LENGTH_GUIDE[x]['words']} words)")
            variants = st.slider("Number of Variants", 1, 5, 2)

            features = [f.strip() for f in features_text.strip().split("\n") if f.strip()] if features_text else []
            if features:
                st.markdown("**Feature → Benefit Mapping:**")
                mapped = map_features_to_benefits(features)
                for m in mapped:
                    st.markdown(f"- **{m['feature']}** → {m['benefit']}")

        keywords = [k.strip() for k in keywords_text.split(",") if k.strip()] if keywords_text else None

        if st.button("🚀 Generate Descriptions", type="primary", use_container_width=True):
            if not product:
                st.error("Please enter a product name.")
            else:
                with st.spinner("Writing product descriptions..."):
                    try:
                        result = generate_descriptions(product, features, platform, length, variants, keywords, config)
                        st.session_state["product_result"] = result
                        st.session_state["product_keywords"] = keywords
                        st.success("Descriptions generated!")
                    except Exception as e:
                        st.error(f"Error: {e}")

    with tab2:
        st.subheader("🏪 Platform Guidelines")
        for key, plat in platforms.items():
            with st.expander(f"{plat['icon']} **{plat['name']}**"):
                st.markdown(f"**Tips:** {plat['tips']}")
                st.markdown(f"**Title Max:** {plat.get('title_max', 'N/A')} chars")
                st.code(f"--platform {key}", language="bash")

    with tab3:
        if "product_result" in st.session_state:
            st.markdown(st.session_state["product_result"])
            st.download_button("📄 Download", st.session_state["product_result"], file_name="product_descriptions.md", mime="text/markdown")
        else:
            st.info("Generate descriptions first.")

    with tab4:
        if "product_result" in st.session_state and st.session_state.get("product_keywords"):
            result = st.session_state["product_result"]
            kws = st.session_state["product_keywords"]
            seo = calculate_seo_score(result, kws)

            col1, col2, col3 = st.columns(3)
            col1.metric("SEO Score", f"{seo['overall_score']}/100")
            col2.metric("Keyword Coverage", f"{seo['keyword_coverage']}%")
            col3.metric("Word Count", seo["word_count"])

            st.markdown("### Keyword Details")
            for kw, details in seo["keyword_details"].items():
                st.markdown(f"- **{kw}**: {details['count']} occurrences ({details['density']}% density)")
        else:
            st.info("Generate descriptions with SEO keywords to see the score.")


if __name__ == "__main__":
    main()
