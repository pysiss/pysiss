#!/usr/bin/env python
""" file: setup.pyb (pysiss.borehole)
    author: Jess Robertson, CSIRO Earth Science and Resource Engineering
    date: Wednesday 1 May, 2013

    description: Distutils installer script for pysiss.borehole.
"""

import distribute_setup
distribute_setup.use_setuptools()
from setuptools import setup, find_packages

## VERSION NUMBERS
# Patch disutils if it can't cope with the 'classifiers' or 'download_url'
# keywords (for Python < 2.2.3)
from sys import version
if version < '2.2.3':
    from distutils.dist import DistributionMetadata
    DistributionMetadata.classifiers = None
    DistributionMetadata.download_url = None

# Load requirements from requirements.txt
with open('requirements.txt', 'rb') as fhandle:
    INSTALL_REQUIREMENTS = fhandle.readlines()

## PACKAGE INFORMATION
setup(
    name='pysiss',
    version='0.0.1',
    description='A pythonic interface to Spatial Information Services Stack '
                '(SISS) services',
    long_description=open('README.md').read(),
    author='Jess Robertson',
    author_email='jesse.robertson@csiro.au',
    url='https://stash.csiro.au/projects/DARDA/repos/pysiss/',
    packages=find_packages(),
    package_data={
        'pysiss.borehole.gml.resources': ['*'],
        'pysiss.vocabulary.gsml.resources': ['*'],
        'pysiss.vocabulary.lithology.resources': ['*'],
        'pysiss.vocabulary.resources': ['*']
    },
    install_requires=INSTALL_REQUIREMENTS,
    test_suite='tests',
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
