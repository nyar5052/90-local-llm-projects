"""Package setup for Meal Planner Bot."""

from setuptools import setup, find_packages

setup(
    name="meal-planner-bot",
    version="1.0.0",
    description="Generate personalized weekly meal plans with recipes",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.10",
    install_requires=[
        "requests",
        "rich",
        "click",
        "PyYAML",
        "streamlit",
    ],
    entry_points={
        "console_scripts": [
            "meal-planner=meal_planner.cli:main",
        ],
    },
)
