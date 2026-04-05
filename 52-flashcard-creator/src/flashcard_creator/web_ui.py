#!/usr/bin/env python3
"""
Flashcard Creator — Streamlit Web UI.

Provides four modes: Create Cards, Review Mode, Deck Browser, Statistics.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st

from flashcard_creator.core import (
    ConfigManager,
    DeckManager,
    SpacedRepetition,
    ReviewSession,
    Flashcard,
    Deck,
    create_flashcards,
    dict_to_flashcards,
    setup_logging,
)
from common.llm_client import check_ollama_running  # noqa: E402

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------

st.set_page_config(page_title="Flashcard Creator", page_icon="🗂️", layout="wide")

# ---------------------------------------------------------------------------
# Session-level singletons
# ---------------------------------------------------------------------------


@st.cache_resource
def _get_config():
    cfg = ConfigManager()
    setup_logging(cfg)
    return cfg


@st.cache_resource
def _get_deck_manager():
    cfg = _get_config()
    return DeckManager(cfg.get("storage", "decks_dir", "./decks"))


config = _get_config()
dm = _get_deck_manager()

# ---------------------------------------------------------------------------
# Sidebar — mode selector
# ---------------------------------------------------------------------------

st.sidebar.title("🗂️ Flashcard Creator")
mode = st.sidebar.radio(
    "Mode",
    ["Create Cards", "Review Mode", "Deck Browser", "Statistics"],
    index=0,
)

# ---------------------------------------------------------------------------
# Create Cards
# ---------------------------------------------------------------------------

if mode == "Create Cards":
    st.header("✨ Create Flashcards")

    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        topic = st.text_input("Topic", placeholder="e.g. Python Decorators")
    with col2:
        count = st.slider("Cards", min_value=1, max_value=50,
                           value=config.get("flashcards", "default_count", 10))
    with col3:
        difficulty = st.selectbox("Difficulty", ["easy", "medium", "hard"], index=1)

    deck_name = st.text_input("Save to deck (optional)", placeholder="My Deck")

    generate = st.button("🚀 Generate", type="primary", disabled=not topic)

    if generate and topic:
        if not check_ollama_running():
            st.error("Ollama is not running. Start with `ollama serve`.")
        else:
            with st.spinner("Generating flashcards…"):
                try:
                    data = create_flashcards(topic, count, difficulty, config=config)
                except Exception as exc:
                    st.error(f"Generation failed: {exc}")
                    data = None

            if data:
                cards = data.get("cards", [])
                st.success(f"Generated {len(cards)} cards about **{data.get('topic', topic)}**")

                # Editable card display
                edited_cards = []
                for idx, card in enumerate(cards):
                    with st.expander(f"Card {idx + 1}: {card.get('front', '')[:60]}", expanded=idx == 0):
                        front = st.text_area("Front", card.get("front", ""), key=f"f_{idx}")
                        back = st.text_area("Back", card.get("back", ""), key=f"b_{idx}")
                        hint = st.text_input("Hint", card.get("hint", ""), key=f"h_{idx}")
                        diff = st.selectbox("Difficulty", ["easy", "medium", "hard"],
                                            index=["easy", "medium", "hard"].index(
                                                card.get("difficulty", "medium")),
                                            key=f"d_{idx}")
                        edited_cards.append({**card, "front": front, "back": back,
                                             "hint": hint, "difficulty": diff})

                if deck_name and st.button("💾 Save to deck"):
                    deck = dm.get_deck(deck_name) or dm.create_deck(deck_name)
                    for c in edited_cards:
                        deck.cards.append(Flashcard(
                            id=str(c.get("id", "")),
                            front=c["front"], back=c["back"],
                            hint=c["hint"], difficulty=c["difficulty"],
                            tags=c.get("tags", []),
                        ))
                    dm._save(deck)
                    st.success(f"Saved {len(edited_cards)} cards to **{deck_name}**")

# ---------------------------------------------------------------------------
# Review Mode
# ---------------------------------------------------------------------------

elif mode == "Review Mode":
    st.header("🧠 Review Flashcards")

    all_decks = dm.list_decks()
    if not all_decks:
        st.info("No decks found. Create some flashcards first!")
    else:
        deck_names = [d.name for d in all_decks]
        selected = st.selectbox("Select Deck", deck_names)
        due_only = st.checkbox("Due cards only", value=False)

        deck = dm.get_deck(selected)
        if deck is None:
            st.error("Deck not found.")
        else:
            sr = SpacedRepetition(config)

            if "review_session" not in st.session_state or st.session_state.get("review_deck") != selected:
                st.session_state["review_session"] = ReviewSession(deck, due_only=due_only)
                st.session_state["review_idx"] = 0
                st.session_state["review_deck"] = selected
                st.session_state["review_show_back"] = False

            session: ReviewSession = st.session_state["review_session"]
            idx: int = st.session_state["review_idx"]
            total = len(session.cards)

            if total == 0:
                st.info("No cards to review right now.")
            elif idx < total:
                card = session.cards[idx]
                st.progress((idx) / total, text=f"Card {idx + 1} / {total}")

                # Front
                st.subheader("Front")
                st.info(card.front)

                if card.hint:
                    with st.expander("💡 Hint"):
                        st.write(card.hint)

                if not st.session_state["review_show_back"]:
                    if st.button("🔄 Flip Card"):
                        st.session_state["review_show_back"] = True
                        st.rerun()
                else:
                    st.subheader("Back")
                    st.success(card.back)

                    st.write("**Rate your recall (0-5):**")
                    cols = st.columns(6)
                    labels = ["0 – Blackout", "1 – Wrong", "2 – Hard wrong",
                              "3 – Hard right", "4 – Good", "5 – Perfect"]
                    for q_val, col in enumerate(cols):
                        with col:
                            if st.button(labels[q_val], key=f"q_{idx}_{q_val}"):
                                session.record(q_val)
                                sr.calculate_next_review(card, q_val)
                                st.session_state["review_idx"] = idx + 1
                                st.session_state["review_show_back"] = False
                                st.rerun()
            else:
                # Session complete
                dm._save(deck)
                stats = session.finish()
                st.balloons()
                st.subheader("🎉 Session Complete!")
                c1, c2, c3 = st.columns(3)
                c1.metric("Score", f"{stats.correct}/{stats.cards_reviewed}")
                c2.metric("Percentage", f"{stats.score_pct:.0f}%")
                c3.metric("Avg Quality", f"{stats.avg_quality:.1f}")

                if st.button("🔁 Restart"):
                    del st.session_state["review_session"]
                    st.rerun()

# ---------------------------------------------------------------------------
# Deck Browser
# ---------------------------------------------------------------------------

elif mode == "Deck Browser":
    st.header("📚 Deck Browser")

    all_decks = dm.list_decks()
    if not all_decks:
        st.info("No decks found.")
    else:
        search_query = st.text_input("🔍 Search cards", placeholder="keyword or tag")
        tag_filter = st.text_input("🏷️ Filter by tag", placeholder="e.g. python")

        for deck in all_decks:
            filtered = deck.cards
            if search_query:
                q = search_query.lower()
                filtered = [c for c in filtered if q in c.front.lower() or q in c.back.lower()]
            if tag_filter:
                t = tag_filter.lower()
                filtered = [c for c in filtered if any(t in tag.lower() for tag in c.tags)]

            with st.expander(f"**{deck.name}** — {len(filtered)} card(s)", expanded=False):
                st.caption(deck.description or "No description")
                if deck.tags:
                    st.write("Tags: " + ", ".join(f"`{t}`" for t in deck.tags))
                for card in filtered:
                    st.markdown(f"**Q:** {card.front}")
                    st.markdown(f"**A:** {card.back}")
                    if card.hint:
                        st.caption(f"Hint: {card.hint}")
                    st.divider()

# ---------------------------------------------------------------------------
# Statistics
# ---------------------------------------------------------------------------

elif mode == "Statistics":
    st.header("📊 Statistics")

    all_decks = dm.list_decks()
    if not all_decks:
        st.info("No decks yet.")
    else:
        # Cards per deck chart
        deck_sizes = {d.name: len(d.cards) for d in all_decks}
        st.subheader("Cards per Deck")
        st.bar_chart(deck_sizes)

        # Per-deck detail
        for deck in all_decks:
            stats = dm.get_stats(deck)
            with st.expander(f"**{deck.name}**"):
                c1, c2, c3 = st.columns(3)
                c1.metric("Total Cards", stats.total_cards)
                c2.metric("Reviewed", stats.cards_reviewed)
                c3.metric("Due", stats.due_cards)

                st.write("**Difficulty breakdown:**")
                if stats.cards_by_difficulty:
                    st.bar_chart(stats.cards_by_difficulty)

                # Mastery progress
                if stats.total_cards > 0:
                    mastered = sum(1 for c in deck.cards if c.repetitions >= 3)
                    pct = mastered / stats.total_cards
                    st.progress(pct, text=f"Mastery: {mastered}/{stats.total_cards} ({pct:.0%})")

                # Spaced repetition stats
                if deck.cards:
                    avg_ef = sum(c.ease_factor for c in deck.cards) / len(deck.cards)
                    avg_int = sum(c.interval for c in deck.cards) / len(deck.cards)
                    st.write(f"Avg Ease Factor: **{avg_ef:.2f}** | Avg Interval: **{avg_int:.1f}** days")
