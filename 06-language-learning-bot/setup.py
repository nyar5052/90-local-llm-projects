"""Setup script for Language Learning Bot."""

from setuptools import setup, find_packages

setup(
    name="language-learner",
    version="1.0.0",
    description="Practice conversations in 15+ languages with an AI tutor",
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
            "language-learner=language_learner.cli:main",
        ],
    },
)
