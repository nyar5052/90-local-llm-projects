from setuptools import setup, find_packages

setup(
    name="sleep-improvement-advisor",
    version="1.0.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=["requests", "rich", "click", "pyyaml", "streamlit"],
    extras_require={"dev": ["pytest", "pytest-cov"]},
    entry_points={"console_scripts": ["sleep-advisor=sleep_advisor.cli:main"]},
    python_requires=">=3.10",
)
