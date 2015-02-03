#!/usr/bin/env python
""" file: run_test.py (pysiss)
    author: Jess Robertson
            CSIRO Minerals Resources Flagship
    date: January 2015

    description: Run tests
"""

import sys
import unittest
import pysiss
import os

from tests.mocks.update import update_mocks

def main():
    # Print version for logging purposes
    print 'pySISS version: {0}'.format(pysiss.__version__)

    # Update networks if required
    if not os.path.exists('tests/mocks/cache'):
        update_mocks()

    # Glom tests together and run them
    suite = unittest.defaultTestLoader.discover('tests')
    result = unittest.TextTestRunner(verbosity=2).run(suite)

    # Check for errors and failures, conda expects script to return 1
    # on failure and 0 otherwise
    nerrors, nfailures = len(result.errors), len(result.failures)
    sys.exit(int(nerrors + nfailures > 0))

if __name__ == '__main__':
    main()
