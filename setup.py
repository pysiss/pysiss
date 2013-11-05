#!/usr/bin/env python
""" file: setup.py
    author: Jess Robertson, CSIRO Earth Science and Resource Engineering
    date: Wednesday 1 May, 2013

    description: Distutils installer script for borehole_analysis.
"""

from distutils.core import setup, find_packages

## VERSION NUMBERS
# Patch disutils if it can't cope with the 'classifiers' or 'download_url' 
# keywords (for Python < 2.2.3)
from sys import version
if version < '2.2.3':
    from distutils.dist import DistributionMetadata
    DistributionMetadata.classifiers = None
    DistributionMetadata.download_url = None

## PACKAGE INFORMATION
setup(
    name='python_boreholes',
    version='0.1.1b',
    description='Python functions for analysing borehole data',
    long_description=open('README.md').read(),
    author='Jess Robertson',
    author_email='jesse.robertson@csiro.au',
    url='https://stash.csiro.au/projects/DARDA/repos/python_boreholes',
    packages=find_packages(),
    requires=['numpy', 'matplotlib', 'sklearn'],
    ext_modules=[],
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'License :: Other/Proprietary License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Geology',
        'Topic :: Scientific/Engineering :: Mathematics',
        'Topic :: Scientific/Engineering :: Physics',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
