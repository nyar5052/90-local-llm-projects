"""Setup script for Study Buddy Bot."""

from setuptools import setup, find_packages

setup(
    name="study-buddy",
    version="1.0.0",
    description="AI-powered exam preparation assistant with quizzes and study plans",
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
            "study-buddy=study_buddy.cli:main",
        ],
    },
)
