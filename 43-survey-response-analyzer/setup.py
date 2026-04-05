"""Setup configuration for Survey Response Analyzer."""

from setuptools import setup, find_packages

setup(
    name="survey-response-analyzer",
    version="1.0.0",
    description="Extract themes and insights from survey data using local LLM",
    author="Survey Analyzer Team",
    python_requires=">=3.10",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "requests",
        "rich",
        "click",
        "pyyaml",
        "streamlit",
        "pandas",
    ],
    extras_require={
        "dev": ["pytest", "pytest-cov", "flake8", "black", "mypy"],
    },
    entry_points={
        "console_scripts": [
            "survey-analyzer=survey_analyzer.cli:main",
        ],
    },
)
