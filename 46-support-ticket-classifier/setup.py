from setuptools import setup, find_packages

setup(
    name="ticket-classifier",
    version="1.0.0",
    description="AI-powered support ticket classification with priority queue and SLA tracking",
    author="AI Engineering Team",
    python_requires=">=3.10",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=[
        "click>=8.0",
        "rich>=13.0",
        "streamlit>=1.28",
        "requests>=2.28",
        "pyyaml>=6.0",
        "pandas>=2.0",
    ],
    extras_require={
        "dev": ["pytest>=7.0", "pytest-cov>=4.0"],
    },
    entry_points={
        "console_scripts": [
            "ticket-classifier=ticket_classifier.cli:main",
        ],
    },
)
