"""
Feedback Loop - AI-Assisted Development with Continuous Improvement

A system for collecting metrics, learning patterns, and generating better code
using real LLM integration and automated feedback loops.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text() if readme_file.exists() else __doc__

setup(
    name="feedback-loop",
    version="1.0.0",
    description="AI-assisted development with automated metrics and pattern learning",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Feedback Loop Contributors",
    url="https://github.com/doronpers/feedback-loop",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "anthropic>=0.7.0",
        "pytest>=7.0.0",
        "pytest-cov>=4.0.0",
    ],
    extras_require={
        "dev": [
            "pytest-asyncio>=0.21.0",
            "httpx>=0.24.0",
        ],
        "full": [
            "numpy>=1.20.0",
            "fastapi>=0.100.0",
            "python-multipart>=0.0.6",
            "uvicorn>=0.23.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "feedback-loop=metrics.integrate:main",
            "fl=metrics.integrate:main",  # Short alias
        ],
        "pytest11": [
            "feedback_loop_metrics = conftest",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Software Development :: Testing",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
)
