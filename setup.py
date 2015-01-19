#!/usr/bin/env python
""" file: setup.py (pysiss)
    author: Jess Robertson, CSIRO Earth Science and Resource Engineering
    date: Wednesday 1 May, 2013

    description: Setuptools installer script for pysiss.
"""

from setuptools import setup, find_packages
import os

# Get requirements from requirements.txt file
with open('requirements.txt') as fhandle:
    REQUIREMENTS = map(lambda l: l.strip('\n'), fhandle.readlines())


def read(*paths):
    """Build a file path from *paths* and return the contents."""
    with open(os.path.join(*paths), 'r') as f:
        return f.read()

## PACKAGE INFORMATION
setup(
    # Metadata
    name='pysiss',
    version='0.0.4',
    description='A pythonic interface to Spatial Information Services Stack '
                '(SISS) services',
    long_description=read('README.rst'),
    author='Jess Robertson',
    author_email='jesse.robertson@csiro.au',
    url='http://github.com/pysiss/pysiss',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2 :: Only',
        'Topic :: Internet',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: GIS',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Text Processing :: Markup :: XML'
    ],

    # Dependencies
    install_requires=[
        'matplotlib>=1.0',
        'numpy>=1.6',
        'scipy>=0.9',
        'OWSLib>=0.8',
        'lxml',
        'simplejson>=3.0',
        'pandas>=0.10',
        'shapely',
        'requests',
        'pint'
    ],

    # Contents
    packages=find_packages(exclude=['test*']),
    package_data={
        'pysiss.vocabulary.resources': ['*']
    },
    test_suite='tests'
)
