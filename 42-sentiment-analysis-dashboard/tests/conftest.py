"""Shared test fixtures for Sentiment Analysis Dashboard."""

import pytest


@pytest.fixture
def sample_reviews(tmp_path):
    """Create a sample reviews file."""
    file_path = tmp_path / "reviews.txt"
    file_path.write_text(
        "This product is amazing! Best purchase ever.\n"
        "Terrible quality, broke after one day.\n"
        "It's okay, nothing special but works fine.\n"
    )
    return str(file_path)


@pytest.fixture
def sample_results():
    """Return sample sentiment analysis results."""
    return [
        {"sentiment": "positive", "confidence": 0.95, "key_phrases": ["amazing", "best"], "summary": "Very positive"},
        {"sentiment": "negative", "confidence": 0.88, "key_phrases": ["terrible", "broke"], "summary": "Very negative"},
        {"sentiment": "neutral", "confidence": 0.72, "key_phrases": ["okay", "fine"], "summary": "Neutral review"},
    ]
