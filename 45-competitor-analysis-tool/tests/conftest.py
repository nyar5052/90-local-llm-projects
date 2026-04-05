"""Shared test fixtures for Competitor Analysis Tool."""

import pytest


@pytest.fixture
def sample_swot():
    """Return a sample SWOT analysis result."""
    return {
        "strengths": ["Strong brand", "Large user base"],
        "weaknesses": ["High pricing", "Limited features"],
        "opportunities": ["New markets", "AI integration"],
        "threats": ["New competitors", "Regulation"],
    }


@pytest.fixture
def sample_company_info():
    """Return sample company information."""
    return {
        "company": "TestCo",
        "competitors": ["Comp1", "Comp2"],
        "industry": "tech",
    }
