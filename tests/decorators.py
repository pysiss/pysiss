""" file: slow_decorator.py
    author: Jess Robertson
            CSIRO Minerals Resources Flagship
    date:   Thursday 29 May, 2014

    description: Adds a facility to skip slow tests
"""

import unittest

# Set the flag below to False to run the slow tests
SKIP_SLOW = True


# Define a custom unittest decorator to tag slow tests which should be skipped
def slow(obj):
    """ Decorator to skip slow tests
    """
    if SKIP_SLOW:
        return unittest.skip('Skipping slow tests')(obj)
    else:
        return obj
