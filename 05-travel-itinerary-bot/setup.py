"""Package setup for Travel Itinerary Bot."""

from setuptools import setup, find_packages

setup(
    name="travel-itinerary-bot",
    version="1.0.0",
    description="AI-powered vacation planner with multi-destination support",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.10",
    install_requires=[
        "requests",
        "rich",
        "click",
        "PyYAML",
        "streamlit",
        "pandas",
    ],
    entry_points={
        "console_scripts": [
            "travel-planner=travel_planner.cli:main",
        ],
    },
)
