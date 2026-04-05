"""Setup configuration for Stock Report Generator."""

from setuptools import setup, find_packages

setup(
    name="stock-report-generator",
    version="1.0.0",
    description="Generate professional stock analysis reports using local LLM",
    author="Stock Reporter Team",
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
            "stock-reporter=stock_reporter.cli:main",
        ],
    },
)
