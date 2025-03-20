"""
pyUSPTO Package Setup

This module handles the setup and installation configuration for the pyUSPTO package.
It defines package metadata, dependencies, and other installation requirements.
"""

from setuptools import setup, find_packages

setup(
    name="pyUSPTO",
    use_scm_version=True,
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.0",
    ],
    author="Andrew Piechocki",
    author_email="apiechocki@dunlapcodding.com",
    description="Python client for accessing USPTO APIs",
    long_description=open(file="README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/DunlapCoddingPC/pyUSPTO",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
        "Topic :: Scientific/Engineering :: Information Analysis",
    ],
    keywords="uspto, patent, api, client, bulk data, patent data",
    python_requires=">=3.10",
)
