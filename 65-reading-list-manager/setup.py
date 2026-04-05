"""Setup script for Reading List Manager."""
from setuptools import setup, find_packages

setup(
    name="reading-list-manager",
    version="1.0.0",
    description="AI-powered book management and recommendations",
    author="Reading List Team",
    python_requires=">=3.10",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=[
        "requests>=2.31.0",
        "rich>=13.0.0",
        "click>=8.1.0",
        "pyyaml>=6.0",
        "streamlit>=1.28.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "reading-list=reading_list.cli:cli",
        ],
    },
)
