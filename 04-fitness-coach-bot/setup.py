"""Package setup for Fitness Coach Bot."""

from setuptools import setup, find_packages

setup(
    name="fitness-coach-bot",
    version="1.0.0",
    description="AI-powered personal fitness trainer with workout plans",
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
            "fitness-coach=fitness_coach.cli:main",
        ],
    },
)
