#!/usr/bin/env python
import os

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

SCRIPT_DIR = os.path.dirname(__file__)
if not SCRIPT_DIR:
    SCRIPT_DIR = os.getcwd()


setup(name='tag-version',
      version='0.0.0',
      description='semantic versioned git tags',
      author='OpenSlate',
      author_email='code@openslate.com',
      url='https://github.com/openslate/tag-version',
      package_dir={'': 'src'},
      packages=['tagversion'],
      install_requires=[
        'sh',
      ],
      entry_points={
          'console_scripts': [
              'tag-version = tagversion.entrypoints:main'
          ]
      },)
