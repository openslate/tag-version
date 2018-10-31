#!/usr/bin/env python
import os

from distutils.core import setup
import setuptools # noqa

SCRIPT_DIR = os.path.dirname(__file__)
if not SCRIPT_DIR:
    SCRIPT_DIR = os.getcwd()


setup(name='tag-version',
      version='{{ version }}',
      description='semantic versioned git tags',
      author='Roberto Aguilar',
      author_email='roberto.c.aguilar@gmail.com',
      url='https://github.com/rca/tag-version',
      package_dir = {'': 'src'},
      packages=['tagversion'],
      install_requires=[
        'sh',
      ],
      entry_points={
          'console_scripts': [
              'tag-version = tagversion.entrypoints:main'
          ]
      },
)
