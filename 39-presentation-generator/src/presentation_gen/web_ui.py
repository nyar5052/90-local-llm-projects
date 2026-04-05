"""Streamlit Web UI for Presentation Generator."""

import sys
import os
import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))

from presentation_gen.core import (
    generate_presentation,
    load_config,
    get_formats,
    get_slide_templates,
    get_visual_suggestions,
    estimate_timing,
    export_to_markdown,
    generate_speaker_notes_only,
    FORMATS,
)

st.set_page_config(page_title="📊 Presentation Generator", page_icon="📊", layout="wide")


def main():
    st.title("📊 Presentation Generator")
    st.markdown("*Generate compelling slide decks with speaker notes using AI*")

    config = load_config("config.yaml")
    formats = get_formats()

    tab1, tab2, tab3, tab4 = st.tabs(["🎯 Topic Input", "📑 Slide Cards", "⏱️ Timing", "📥 Download"])

    with tab1:
        col1, col2 = st.columns([2, 1])
        with col1:
            topic = st.text_input("Presentation Topic", placeholder="e.g., Machine Learning for Beginners")
            audience = st.text_input("Target Audience", value="general", placeholder="e.g., executives, students, developers")
        with col2:
            format_type = st.selectbox("Format", list(formats.keys()), format_func=lambda x: formats[x]["name"])
            slides = st.slider("Number of Slides", 3, 30, 12)

        timing = estimate_timing(slides, format_type)
        st.info(f"⏱️ Estimated presentation time: **{timing['formatted']}** ({timing['total_minutes']} minutes)")

        if st.button("🚀 Generate Presentation", type="primary", use_container_width=True):
            if not topic:
                st.error("Please enter a topic.")
            else:
                with st.spinner("Generating your presentation..."):
                    try:
                        result = generate_presentation(topic, slides, audience, format_type, config)
                        st.session_state["pres_result"] = result
                        st.session_state["pres_topic"] = topic
                        st.success("Presentation generated!")
                    except Exception as e:
                        st.error(f"Error: {e}")

    with tab2:
        if "pres_result" in st.session_state:
            st.subheader(f"📑 {st.session_state.get('pres_topic', 'Presentation')}")
            result = st.session_state["pres_result"]
            slide_sections = result.split("### Slide")
            for section in slide_sections[1:]:
                with st.expander(f"### Slide{section[:50].split(chr(10))[0]}"):
                    st.markdown(f"### Slide{section}")

            st.markdown("---")
            st.subheader("🎤 Speaker Notes Only")
            notes = generate_speaker_notes_only(result)
            st.markdown(notes)
        else:
            st.info("Generate a presentation first.")

    with tab3:
        st.subheader("⏱️ Timing Estimator")
        col1, col2 = st.columns(2)
        with col1:
            t_format = st.selectbox("Format", list(formats.keys()), format_func=lambda x: formats[x]["name"], key="timing_fmt")
        with col2:
            t_slides = st.slider("Slides", 3, 30, 12, key="timing_slides")

        t = estimate_timing(t_slides, t_format)

        import pandas as pd
        timing_data = []
        for i in range(1, t_slides + 1):
            timing_data.append({"Slide": i, "Cumulative Time (min)": round(i * t["per_slide_seconds"] / 60, 1)})
        df = pd.DataFrame(timing_data)
        st.bar_chart(df.set_index("Slide"))

        st.metric("Total Time", t["formatted"])

    with tab4:
        if "pres_result" in st.session_state:
            result = st.session_state["pres_result"]
            topic = st.session_state.get("pres_topic", "presentation")

            col1, col2 = st.columns(2)
            with col1:
                md = export_to_markdown(result, topic)
                st.download_button("📄 Download Markdown", md, file_name=f"{topic.replace(' ', '_')}.md", mime="text/markdown")
            with col2:
                notes = generate_speaker_notes_only(result)
                st.download_button("🎤 Download Speaker Notes", notes, file_name="speaker_notes.md", mime="text/markdown")
        else:
            st.info("Generate a presentation first.")


if __name__ == "__main__":
    main()
