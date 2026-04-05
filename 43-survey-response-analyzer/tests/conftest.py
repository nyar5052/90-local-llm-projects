"""Shared test fixtures for Survey Response Analyzer."""

import pytest


@pytest.fixture
def sample_survey(tmp_path):
    """Create a sample survey CSV file."""
    csv_path = tmp_path / "survey.csv"
    csv_path.write_text(
        "id,feedback,rating\n"
        "1,The onboarding process was very smooth and helpful,5\n"
        "2,Customer support was slow and unresponsive,2\n"
        "3,Great product but the documentation could be better,4\n"
        "4,Pricing is too high compared to competitors,3\n"
    )
    return str(csv_path)


@pytest.fixture
def sample_data():
    """Return sample survey data as list of dicts."""
    return [
        {"id": "1", "feedback": "The onboarding process was very smooth and helpful", "rating": "5"},
        {"id": "2", "feedback": "Customer support was slow and unresponsive", "rating": "2"},
        {"id": "3", "feedback": "Great product but documentation could be better", "rating": "4"},
        {"id": "4", "feedback": "Pricing is too high compared to competitors", "rating": "3"},
    ]
