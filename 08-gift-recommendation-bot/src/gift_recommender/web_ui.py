"""Streamlit web interface for Gift Recommendation Bot."""

import streamlit as st
from .core import (
    generate_recommendations, get_gift_details, compare_prices,
    add_to_wishlist, get_wishlist, mark_purchased, load_wishlists,
    add_occasion, get_upcoming_occasions, check_ollama_running,
    OCCASIONS, RELATIONSHIPS,
)
from .utils import setup_logging

setup_logging()


def main():
    """Main Streamlit application."""
    st.set_page_config(page_title="🎁 Gift Recommendation Bot", page_icon="🎁", layout="wide")
    st.title("🎁 Gift Recommendation Bot")
    st.caption("Find the perfect gift with AI-powered suggestions")

    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")
        occasion = st.selectbox("Occasion", [o.replace("-", " ").title() for o in OCCASIONS])
        occasion_key = occasion.lower().replace(" ", "-")
        relationship = st.selectbox("Recipient Relationship", [r.capitalize() for r in RELATIONSHIPS])
        budget = st.slider("Budget ($)", 5, 1000, 50)
        interests = st.text_input("Recipient's Interests", placeholder="gaming, cooking, reading")
        age = st.text_input("Recipient's Age (optional)")
        gender = st.selectbox("Gender (optional)", ["", "male", "female", "non-binary"])

        st.divider()
        st.subheader("📅 Upcoming Occasions")
        upcoming = get_upcoming_occasions(30)
        if upcoming:
            for o in upcoming[:5]:
                st.write(f"🎉 {o['person']}: {o['occasion']} in {o.get('days_until', '?')} days")
        else:
            st.info("No upcoming occasions")

        if not check_ollama_running():
            st.error("❌ Ollama is not running")
            return

    tab_recs, tab_wishlist, tab_calendar = st.tabs(
        ["🎁 Recommendations", "📋 Wishlists", "📅 Calendar"]
    )

    # --- Recommendations Tab ---
    with tab_recs:
        if st.button("🔍 Find Gift Ideas", type="primary"):
            with st.spinner("Finding perfect gifts..."):
                recs = generate_recommendations(
                    occasion_key, relationship.lower(), budget,
                    interests if interests else None,
                    age if age else None,
                    gender if gender else None,
                )
            st.markdown(recs)

            st.divider()
            col1, col2 = st.columns(2)
            with col1:
                detail_gift = st.text_input("Get details about a specific gift")
                if st.button("📋 Get Details") and detail_gift:
                    with st.spinner("Getting details..."):
                        details = get_gift_details(detail_gift, budget)
                    st.markdown(details)
            with col2:
                compare_gift = st.text_input("Compare prices for a gift")
                if st.button("💰 Compare Prices") and compare_gift:
                    with st.spinner("Comparing prices..."):
                        comparison = compare_prices(compare_gift)
                    st.markdown(comparison)

    # --- Wishlist Tab ---
    with tab_wishlist:
        st.subheader("📋 Wishlist Management")
        col1, col2, col3 = st.columns(3)
        with col1:
            wl_person = st.text_input("Person's Name", key="wl_person")
        with col2:
            wl_gift = st.text_input("Gift Item", key="wl_gift")
        with col3:
            wl_price = st.text_input("Price (optional)", key="wl_price")

        if st.button("➕ Add to Wishlist") and wl_person and wl_gift:
            add_to_wishlist(wl_person, wl_gift, wl_price, occasion_key)
            st.success(f"Added {wl_gift} to {wl_person}'s wishlist!")
            st.rerun()

        wishlists = load_wishlists()
        if wishlists:
            for person_key, data in wishlists.items():
                st.subheader(f"🎁 {data['name']}'s Wishlist")
                items = data.get("items", [])
                if items:
                    st.dataframe(
                        [{"Gift": i["gift"], "Price": i.get("price", ""),
                          "Status": "✅ Purchased" if i.get("purchased") else "⬜ Pending",
                          "Added": i["added_date"][:10]}
                         for i in items],
                        use_container_width=True,
                    )
        else:
            st.info("No wishlists yet. Add items above!")

    # --- Calendar Tab ---
    with tab_calendar:
        st.subheader("📅 Occasion Calendar")
        col1, col2, col3 = st.columns(3)
        with col1:
            cal_person = st.text_input("Person", key="cal_person")
        with col2:
            cal_occasion = st.text_input("Occasion", key="cal_occasion")
        with col3:
            cal_date = st.date_input("Date", key="cal_date")

        if st.button("📅 Add Occasion") and cal_person and cal_occasion:
            add_occasion(cal_person, cal_occasion, cal_date.strftime("%Y-%m-%d"))
            st.success(f"Added {cal_person}'s {cal_occasion}!")
            st.rerun()

        upcoming = get_upcoming_occasions(90)
        if upcoming:
            st.dataframe(
                [{"Person": o["person"], "Occasion": o["occasion"],
                  "Date": o["date"], "Days Until": o.get("days_until", "?")}
                 for o in upcoming],
                use_container_width=True,
            )
        else:
            st.info("No upcoming occasions. Add some above!")


if __name__ == "__main__":
    main()
