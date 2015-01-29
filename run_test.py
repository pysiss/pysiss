#!/usr/bin/env python
""" file: run_tests.py (pysiss)
    author: Jess Robertson
            CSIRO Minerals Resources Flagship
    date: January 2015

    description: Run tests
"""

import sys
import unittest

def main():
    # Glom tests together and run them
    suite = unittest.defaultTestLoader.discover('tests')
    result = unittest.TextTestRunner(verbosity=2).run(suite)

    # Check for errors and failures, conda expects script to return 1
    # on failure and 0 otherwise
    nerrors, nfailures = len(result.errors), len(result.failures)
    sys.exit(int(nerrors + nfailures > 0))

if __name__ == '__main__':
    main()
