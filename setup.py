#!/usr/bin/env python
import os

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

SCRIPT_DIR = os.path.dirname(__file__)
if not SCRIPT_DIR:
    SCRIPT_DIR = os.getcwd()


setup(
    name="tag-version",
    version="0.0.0",
    description="semantic versioned git tags",
    author="DoubleVerify",
    author_email="code@doubleverify.com",
    url="https://github.com/openslate/tag-version",
    package_dir={"": "src"},
    packages=["tagversion"],
    install_requires=["sh==1.14.3"],
    entry_points={"console_scripts": ["tag-version = tagversion.entrypoints:main"]},
)
