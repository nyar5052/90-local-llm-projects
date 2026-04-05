"""Package setup for IT Helpdesk Bot."""

from setuptools import setup, find_packages

setup(
    name="it-helpdesk-bot",
    version="1.0.0",
    description="AI-powered IT support chatbot for common tech issues",
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
            "helpdesk-bot=helpdesk_bot.cli:main",
        ],
    },
)
