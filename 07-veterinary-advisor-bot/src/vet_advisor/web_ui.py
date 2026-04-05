"""Streamlit web interface for Veterinary Advisor Bot."""

import streamlit as st
from .core import (
    format_pet_context, get_response, check_symptoms, get_breed_advice,
    get_nutrition_advice, add_pet_profile, load_pet_profiles, get_pet_profile,
    record_symptom, get_symptom_history_for_pet, check_ollama_running,
    PET_TYPES, MEDICAL_DISCLAIMER,
)
from .utils import setup_logging

setup_logging()


def main():
    """Main Streamlit application."""
    st.set_page_config(page_title="🐾 Veterinary Advisor Bot", page_icon="🐾", layout="wide")
    st.title("🐾 Veterinary Advisor Bot")
    st.caption("AI-powered pet health guidance")

    st.warning(MEDICAL_DISCLAIMER)

    # Sidebar - Pet Profile
    with st.sidebar:
        st.header("🐾 Pet Profile")

        profiles = load_pet_profiles()
        profile_names = ["New Pet"] + [p["name"] for p in profiles]
        selected = st.selectbox("Select Pet", profile_names)

        if selected == "New Pet":
            pet_type = st.selectbox("Pet Type", PET_TYPES)
            pet_name = st.text_input("Pet Name", value="Buddy")
            breed = st.text_input("Breed", value="unknown")
            age = st.text_input("Age", value="unknown")
            weight = st.text_input("Weight", value="unknown")

            if st.button("💾 Save Profile"):
                add_pet_profile(pet_name, pet_type, breed, age, weight)
                st.success(f"Saved {pet_name}'s profile!")
                st.rerun()

            pet_profile = {"type": pet_type, "name": pet_name, "breed": breed,
                           "age": age, "weight": weight}
        else:
            pet_profile = get_pet_profile(selected)
            if pet_profile:
                st.info(format_pet_context(pet_profile))
            else:
                pet_profile = {"type": "dog", "name": selected, "breed": "unknown",
                               "age": "unknown", "weight": "unknown"}

        st.divider()
        if not check_ollama_running():
            st.error("❌ Ollama is not running")
            return

    tab_chat, tab_symptoms, tab_history = st.tabs(["💬 Chat", "🩺 Symptom Check", "📋 History"])

    # --- Chat Tab ---
    with tab_chat:
        if "vet_history" not in st.session_state:
            st.session_state.vet_history = []
        if "vet_messages" not in st.session_state:
            st.session_state.vet_messages = []

        for msg in st.session_state.vet_messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        if prompt := st.chat_input(f"Ask about {pet_profile['name']}..."):
            st.session_state.vet_messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                with st.spinner("Consulting..."):
                    response = get_response(prompt, st.session_state.vet_history, pet_profile)
                st.markdown(response)

            st.session_state.vet_history.append({"role": "user", "content": prompt})
            st.session_state.vet_history.append({"role": "assistant", "content": response})
            st.session_state.vet_messages.append({"role": "assistant", "content": response})

    # --- Symptom Check Tab ---
    with tab_symptoms:
        st.subheader("🩺 Symptom Analysis")
        symptoms = st.text_area("Describe the symptoms", placeholder="e.g., vomiting, lethargy, loss of appetite")
        col1, col2 = st.columns(2)
        with col1:
            severity = st.selectbox("Perceived Severity", ["mild", "moderate", "severe", "unknown"])
        with col2:
            notes = st.text_input("Additional notes")

        if st.button("🔍 Analyze Symptoms") and symptoms:
            with st.spinner("Analyzing symptoms..."):
                result = check_symptoms(symptoms, pet_profile)
            record_symptom(pet_profile["name"], symptoms, severity, notes)
            st.markdown(result)

        st.divider()
        st.subheader("🐕 Breed-Specific Advice")
        if st.button("Get Breed Advice"):
            with st.spinner("Getting advice..."):
                advice = get_breed_advice(pet_profile["type"], pet_profile.get("breed", "unknown"))
            st.markdown(advice)

        st.subheader("🥗 Nutrition Advice")
        if st.button("Get Nutrition Advice"):
            with st.spinner("Getting advice..."):
                nutrition = get_nutrition_advice(pet_profile)
            st.markdown(nutrition)

    # --- History Tab ---
    with tab_history:
        st.subheader(f"📋 Symptom History — {pet_profile['name']}")
        hist = get_symptom_history_for_pet(pet_profile["name"])
        if hist:
            st.dataframe(
                [{"Date": h["date"][:10], "Symptoms": h["symptoms"],
                  "Severity": h.get("severity", "N/A"), "Notes": h.get("notes", "")}
                 for h in hist],
                use_container_width=True,
            )
        else:
            st.info("No symptom history recorded yet.")


if __name__ == "__main__":
    main()
