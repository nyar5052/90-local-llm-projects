"""Shared test fixtures for Stock Report Generator."""

import pytest


@pytest.fixture
def sample_stock_csv(tmp_path):
    """Create a sample stock data CSV."""
    csv_path = tmp_path / "stock.csv"
    csv_path.write_text(
        "Date,Open,High,Low,Close,Volume\n"
        "2024-01-02,150.00,152.00,149.00,151.00,1000000\n"
        "2024-01-03,151.00,155.00,150.00,154.00,1200000\n"
        "2024-01-04,154.00,156.00,152.00,153.00,900000\n"
        "2024-01-05,153.00,158.00,153.00,157.00,1100000\n"
        "2024-01-08,157.00,160.00,155.00,159.00,1300000\n"
        "2024-01-09,159.00,161.00,157.00,160.00,1050000\n"
    )
    return str(csv_path)


@pytest.fixture
def sample_stock_data():
    """Return sample stock data as list of dicts."""
    return [
        {"Date": "2024-01-02", "Close": "150.00"},
        {"Date": "2024-01-03", "Close": "155.00"},
        {"Date": "2024-01-04", "Close": "153.00"},
        {"Date": "2024-01-05", "Close": "158.00"},
        {"Date": "2024-01-08", "Close": "160.00"},
    ]


@pytest.fixture
def large_stock_data():
    """Return larger stock data for indicator testing."""
    base = 150.0
    data = []
    for i in range(30):
        price = base + (i % 7 - 3) * 2
        data.append({"Date": f"2024-01-{i+1:02d}", "Close": f"{price:.2f}"})
    return data
