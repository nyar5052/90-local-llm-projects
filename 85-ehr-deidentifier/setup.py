"""Setup for EHR De-Identifier package."""

from setuptools import setup, find_packages

setup(
    name="ehr-deidentifier",
    version="1.0.0",
    description="AI-powered EHR de-identification tool (EDUCATIONAL USE ONLY - NOT HIPAA CERTIFIED)",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="EHR De-Identifier Contributors",
    python_requires=">=3.10",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=[
        "requests",
        "rich",
        "click",
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
            "ehr-deidentify=ehr_deidentifier.cli:cli",
        ],
    },
)
