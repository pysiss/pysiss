#!/usr/bin/env python
""" file:   __main__.py (pyboreholes tests)
    author: Jess Robertson
            CSIRO Earth Science and Resource Engineering
    email:  jesse.robertson@csiro.au
    date:   Wednesday May 1, 2013

    description: Initialisation of tests.
"""

import unittest
from os import path
from glob import glob


def test_all():
    """ Discover and run all the test stuff in the directory
    """
    test_modules = [path.basename(f)[:-3]
                    for f in glob(path.join(path.dirname(__file__),
                                            'test_*.py'))]
    modules = map(__import__, test_modules)
    load = unittest.defaultTestLoader.loadTestsFromModule
    return unittest.TestSuite(map(load, modules))


if __name__ == '__main__':
    unittest.main(defaultTest='test_all')
