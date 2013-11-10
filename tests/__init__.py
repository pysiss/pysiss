#!/usr/bin/env python
""" file:   __init__.py (python_boreholes tests)
    author: Jess Robertson
            CSIRO Earth Science and Resource Engineering
    email:  jesse.robertson@csiro.au
    date:   Wednesday May 1, 2013

    description: Initialisation of tests.
"""

import unittest

#pylint: disable=W0401
from tests.test_borehole import *
from tests.test_utilities import *

if __name__ == '__main__':
    unittest.main()