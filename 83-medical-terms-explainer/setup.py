"""Setup script for Medical Terms Explainer."""

from setuptools import setup, find_packages

setup(
    name="medical-terms-explainer",
    version="1.0.0",
    description="AI-powered medical terminology education tool",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="90 Local LLM Projects",
    python_requires=">=3.10",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=[
        "click",
        "requests",
        "rich",
        "pyyaml",
        "streamlit",
    ],
    extras_require={
        "dev": [
            "pytest",
            "pytest-cov",
        ],
    },
    entry_points={
        "console_scripts": [
            "medical-terms=medical_terms.cli:cli",
        ],
    },
)
