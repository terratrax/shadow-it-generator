"""
Shadow IT Log Generator
A tool for generating realistic shadow IT network traffic logs for security testing and training
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="shadow-it-generator",
    version="0.1.0",
    author="Shadow IT Generator Team",
    description="Generate realistic shadow IT network traffic logs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/shadow-it-generator",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Information Technology",
        "Topic :: Security",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pyyaml>=6.0",
        "faker>=18.0",
        "numpy>=1.24",
        "python-dateutil>=2.8",
        "click>=8.0",
        "pydantic>=2.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "black>=23.0",
            "flake8>=6.0",
            "mypy>=1.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "shadow-it-gen=shadow_it_generator.main:main",
        ],
    },
)