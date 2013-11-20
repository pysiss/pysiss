#!/usr/bin/env python
""" file:   __init__.py (pyboreholes tests)
    author: Jess Robertson
            CSIRO Earth Science and Resource Engineering
    email:  jesse.robertson@csiro.au
    date:   Wednesday May 1, 2013

    description: Initialisation of tests.
"""

import unittest

#pylint: disable=W0401
from .test_borehole import *
from .test_utilities import *
from .test_detrend import *
from .test_regularizer import *
from .test_real_data import *

if __name__ == '__main__':
    unittest.main()