"""Setup script for the Research Paper QA package."""

from setuptools import setup, find_packages

setup(
    name="research-qa",
    version="1.0.0",
    description="Interactive question answering over research papers using local LLM",
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
            "research-qa=research_qa.cli:main",
        ],
    },
)
