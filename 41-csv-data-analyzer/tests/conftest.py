"""Shared test fixtures for CSV Data Analyzer."""

import pytest
import pandas as pd


@pytest.fixture
def sample_csv(tmp_path):
    """Create a sample CSV file for testing."""
    csv_path = tmp_path / "test_data.csv"
    df = pd.DataFrame({
        "month": ["Jan", "Feb", "Mar", "Apr"],
        "revenue": [10000, 15000, 12000, 18000],
        "expenses": [8000, 9000, 7500, 10000],
    })
    df.to_csv(csv_path, index=False)
    return str(csv_path)


@pytest.fixture
def sample_df():
    """Return a sample DataFrame."""
    return pd.DataFrame({
        "month": ["Jan", "Feb", "Mar"],
        "revenue": [10000, 15000, 12000],
        "expenses": [8000, 9000, 7500],
    })


@pytest.fixture
def large_numeric_df():
    """Return a DataFrame with many numeric columns for correlation testing."""
    import numpy as np
    np.random.seed(42)
    return pd.DataFrame({
        "a": np.random.randn(100),
        "b": np.random.randn(100),
        "c": np.random.randn(100) * 2 + 1,
    })
