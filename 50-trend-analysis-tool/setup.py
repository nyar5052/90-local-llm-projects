"""Setup script for trend-analyzer."""

from setuptools import setup, find_packages

setup(
    name="trend-analyzer",
    version="1.0.0",
    description="Production-grade trend analysis tool using local LLMs",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Trend Analyzer Team",
    python_requires=">=3.10",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=[
        "requests>=2.28",
        "rich>=13.0",
        "click>=8.0",
        "streamlit>=1.28",
        "pyyaml>=6.0",
        "pandas>=2.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "trend-analyzer=trend_analyzer.cli:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
