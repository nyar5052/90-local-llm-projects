#!/usr/bin/env python3
"""Reading List Manager - Streamlit Web UI."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import streamlit as st
from datetime import datetime

from reading_list.core import (
    load_books,
    add_book,
    update_progress,
    rate_book,
    get_genre_stats,
    get_summary,
    get_recommendations,
    display_books,
    set_reading_goal,
    check_goal_progress,
    get_tbr_list,
    calculate_reading_speed,
    recommend_similar,
    config,
    STATUS_EMOJI,
)

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------

st.set_page_config(page_title="Reading List Manager", page_icon="📚", layout="wide")

# ---------------------------------------------------------------------------
# Sidebar navigation
# ---------------------------------------------------------------------------

st.sidebar.title("📚 Reading List Manager")
page = st.sidebar.radio(
    "Navigate",
    ["Add Book", "My Library", "Recommendations", "Reading Stats"],
)

STATUSES = config.get("reading", {}).get("statuses", ["to-read", "reading", "completed", "dropped", "on-hold"])
GENRES = config.get("reading", {}).get("genres", [])

# ---------------------------------------------------------------------------
# Add Book page
# ---------------------------------------------------------------------------

if page == "Add Book":
    st.header("➕ Add a New Book")

    with st.form("add_book_form"):
        col1, col2 = st.columns(2)
        with col1:
            title = st.text_input("Title", placeholder="Enter book title")
            author = st.text_input("Author", placeholder="Enter author name")
            genre = st.selectbox("Genre", [""] + GENRES)
        with col2:
            pages = st.number_input("Total Pages", min_value=0, value=0, step=1)
            status = st.selectbox("Status", STATUSES)

        submitted = st.form_submit_button("📖 Add Book")
        if submitted and title and author:
            book = add_book(title, author, genre, status, pages=pages)
            st.success(f"✅ Added: \"{book['title']}\" by {book['author']}")
        elif submitted:
            st.warning("Please enter both title and author.")

# ---------------------------------------------------------------------------
# My Library page
# ---------------------------------------------------------------------------

elif page == "My Library":
    st.header("📖 My Library")
    data = load_books()
    books = data["books"]

    if not books:
        st.info("No books yet. Add some from the sidebar!")
    else:
        # Filters
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            filter_status = st.selectbox("Filter by Status", ["All"] + STATUSES)
        with col_f2:
            filter_genre = st.selectbox("Filter by Genre", ["All"] + GENRES)

        filtered = books
        if filter_status != "All":
            filtered = [b for b in filtered if b.get("status") == filter_status]
        if filter_genre != "All":
            filtered = [b for b in filtered if b.get("genre") == filter_genre]

        # Metrics
        total = len(books)
        completed = len([b for b in books if b.get("status") == "completed"])
        ratings = [b["rating"] for b in books if b.get("rating", 0) > 0]
        avg_rating = round(sum(ratings) / len(ratings), 1) if ratings else 0.0

        m1, m2, m3 = st.columns(3)
        m1.metric("📚 Total Books", total)
        m2.metric("✅ Completed", completed)
        m3.metric("⭐ Avg Rating", f"{avg_rating}/5")

        # Table
        for book in filtered:
            emoji = STATUS_EMOJI.get(book.get("status", "to-read"), "📋")
            stars = "⭐" * book.get("rating", 0) if book.get("rating") else "—"
            pct = book.get("progress_percent", 0)

            with st.expander(f"{emoji} **{book['title']}** by {book['author']}  |  {stars}"):
                c1, c2, c3 = st.columns(3)
                c1.write(f"**Genre:** {book.get('genre', '-')}")
                c2.write(f"**Pages:** {book.get('pages_read', 0)}/{book.get('pages', '?')}")
                c3.write(f"**Progress:** {pct:.0f}%")
                if book.get("review"):
                    st.write(f"**Review:** {book['review']}")
                if book.get("notes"):
                    st.write(f"**Notes:** {book['notes']}")

                # Inline progress update
                new_pages = st.number_input(
                    "Update pages read",
                    min_value=0,
                    value=book.get("pages_read", 0),
                    key=f"pg_{book['id']}",
                )
                if st.button("Update Progress", key=f"up_{book['id']}"):
                    update_progress(book["id"], new_pages)
                    st.rerun()

                # Inline rating
                new_rating = st.slider("Rate", 1, 5, value=book.get("rating", 3), key=f"rt_{book['id']}")
                new_review = st.text_input("Review", value=book.get("review", ""), key=f"rv_{book['id']}")
                if st.button("Save Rating", key=f"sr_{book['id']}"):
                    rate_book(book["id"], new_rating, new_review)
                    st.rerun()

# ---------------------------------------------------------------------------
# Recommendations page
# ---------------------------------------------------------------------------

elif page == "Recommendations":
    st.header("🔮 Book Recommendations")

    tab_ai, tab_similar = st.tabs(["AI Recommendations", "Similar from Library"])

    with tab_ai:
        genre_sel = st.selectbox("Select genre (optional)", [""] + GENRES)
        if st.button("🤖 Get AI Recommendations"):
            data = load_books()
            with st.spinner("Thinking..."):
                try:
                    result = get_recommendations(genre_sel, data["books"])
                    st.markdown(result)
                except Exception as e:
                    st.error(f"LLM error: {e}. Make sure Ollama is running.")

    with tab_similar:
        data = load_books()
        similar = recommend_similar(data["books"])
        if similar:
            for b in similar:
                emoji = STATUS_EMOJI.get(b.get("status", "to-read"), "📋")
                st.write(f"{emoji} **{b['title']}** by {b['author']} — {b.get('genre', '')}")
        else:
            st.info("Add more books with ratings to get similarity-based recommendations.")

# ---------------------------------------------------------------------------
# Reading Stats page
# ---------------------------------------------------------------------------

elif page == "Reading Stats":
    st.header("📊 Reading Statistics")
    data = load_books()
    books = data["books"]

    if not books:
        st.info("No books yet!")
    else:
        # Goal tracking
        st.subheader("🎯 Yearly Goal")
        year = datetime.now().year
        col_g1, col_g2 = st.columns([3, 1])
        with col_g2:
            new_target = st.number_input("Set goal", min_value=1, value=24, key="goal_target")
            if st.button("Set Goal"):
                set_reading_goal(year, new_target)
                st.rerun()

        progress_info = check_goal_progress(year, books)
        with col_g1:
            st.progress(min(progress_info["percent"] / 100, 1.0))
            st.write(f"**{progress_info['completed']}** / **{progress_info['target']}** books completed ({progress_info['percent']:.1f}%)")
            if progress_info["remaining"] > 0 and progress_info["days_left"] > 0:
                st.write(f"📅 {progress_info['days_left']} days left — need ~{progress_info['books_per_month_needed']:.1f} books/month")

        st.divider()

        # Genre chart
        st.subheader("📚 Books by Genre")
        genre_stats = get_genre_stats(books)
        if genre_stats:
            import pandas as pd

            df_genre = pd.DataFrame([
                {"Genre": g, "Count": s["count"], "Avg Rating": s["avg_rating"]}
                for g, s in genre_stats.items()
            ])
            st.bar_chart(df_genre.set_index("Genre")["Count"])

        st.divider()

        # Rating distribution
        st.subheader("⭐ Rating Distribution")
        ratings = [b.get("rating", 0) for b in books if b.get("rating", 0) > 0]
        if ratings:
            import pandas as pd

            rating_counts = {i: ratings.count(i) for i in range(1, 6)}
            df_ratings = pd.DataFrame(list(rating_counts.items()), columns=["Rating", "Count"])
            st.bar_chart(df_ratings.set_index("Rating"))
        else:
            st.info("Rate some books to see the distribution.")

        st.divider()

        # Reading speed
        st.subheader("🏃 Reading Speed")
        completed_books = [b for b in books if b.get("status") == "completed"]
        if completed_books:
            for b in completed_books:
                speed = calculate_reading_speed(b)
                if speed:
                    st.write(f"📖 **{b['title']}**: {speed} pages/day")
        else:
            st.info("Complete some books to see reading speed stats.")
