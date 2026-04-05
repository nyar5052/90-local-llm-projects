from setuptools import setup, find_packages

setup(
    name="home-automation-scripter",
    version="2.0.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "click>=8.1.0",
        "rich>=13.0.0",
        "requests>=2.31.0",
        "pyyaml>=6.0",
        "streamlit>=1.28.0",
    ],
    entry_points={
        "console_scripts": [
            "home-automation=home_automation.cli:main",
        ],
    },
    python_requires=">=3.10",
)
