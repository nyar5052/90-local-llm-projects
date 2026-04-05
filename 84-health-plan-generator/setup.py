"""Setup script for Health Plan Generator."""

from setuptools import setup, find_packages

setup(
    name="health-plan-generator",
    version="1.0.0",
    description="AI-powered personalized wellness plan generator",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Health Plan Generator",
    python_requires=">=3.10",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=[
        "requests",
        "rich",
        "click",
        "pyyaml",
        "streamlit",
        "pandas",
    ],
    extras_require={
        "dev": [
            "pytest",
            "pytest-cov",
        ],
    },
    entry_points={
        "console_scripts": [
            "health-planner=health_planner.cli:cli",
        ],
    },
)
