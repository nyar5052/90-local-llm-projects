"""Setup script for the News Digest Generator package."""

from setuptools import setup, find_packages

setup(
    name="news-digest",
    version="1.0.0",
    description="AI-powered news article aggregation, categorization, and digest generation",
    author="Local LLM Projects",
    python_requires=">=3.10",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
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
            "news-digest=news_digest.cli:main",
        ],
    },
)
