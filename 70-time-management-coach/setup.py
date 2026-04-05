"""Setup configuration for Time Management Coach."""

from setuptools import setup, find_packages

setup(
    name="time-management-coach",
    version="2.0.0",
    description="AI-powered time management coaching with Pomodoro, time blocking, and productivity scoring.",
    author="Time Coach Team",
    python_requires=">=3.10",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=[
        "requests>=2.31.0",
        "rich>=13.0.0",
        "click>=8.1.0",
        "pyyaml>=6.0",
        "streamlit>=1.28.0",
        "plotly>=5.18.0",
    ],
    extras_require={
        "dev": ["pytest>=7.0.0"],
    },
    entry_points={
        "console_scripts": [
            "time-coach=time_coach.cli:main",
        ],
    },
)
