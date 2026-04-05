"""Setup script for Gift Recommendation Bot."""

from setuptools import setup, find_packages

setup(
    name="gift-recommender",
    version="1.0.0",
    description="Personalized gift suggestion engine powered by AI",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.10",
    install_requires=[
        "requests",
        "rich",
        "click",
        "pyyaml",
        "streamlit",
    ],
    extras_require={
        "dev": ["pytest", "pytest-cov"],
    },
    entry_points={
        "console_scripts": [
            "gift-recommender=gift_recommender.cli:main",
        ],
    },
)
