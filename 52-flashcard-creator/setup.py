from setuptools import setup, find_packages

setup(
    name="flashcard-creator",
    version="1.0.0",
    description="Production-grade flashcard creation with spaced repetition, powered by local LLM",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.10",
    install_requires=[
        "requests>=2.31.0",
        "rich>=13.7.0",
        "click>=8.1.0",
        "pyyaml>=6.0",
        "streamlit>=1.28.0",
    ],
    extras_require={
        "dev": ["pytest>=7.4.0", "pytest-cov>=4.1.0"],
    },
    entry_points={
        "console_scripts": [
            "flashcard-creator=flashcard_creator.cli:cli",
        ],
    },
)
