from setuptools import setup, find_packages

setup(
    name="symptom-checker-bot",
    version="1.0.0",
    description="AI-powered symptom analysis tool for educational purposes",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
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
            "symptom-checker=symptom_checker.cli:cli",
        ],
    },
)
