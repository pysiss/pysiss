""" file: test_borehole_utilities.py
    author: Jess Robertson & Ben Caradoc-Davies
            CSIRO Earth Science and Resource Engineering
    date: Tuesday May 14, 2013

    description: unittests for pysiss/borehole/utilities.py
"""

import unittest
import numpy
from pysiss.utilities import mask_all_nans


class TestMaskNans(unittest.TestCase):

    """ Testing masking nans function
    """

    def test_fail(self):
        "Function should fail with different sized input"
        self.assertRaises(ValueError, mask_all_nans,
                          numpy.arange(10),
                          numpy.arange(11),
                          numpy.arange(10))

    def test_convert(self):
        "Function should convert floats to numpy arrays"
        mask_all_nans(range(10), range(10), range(10))

    def test_fail_non_numeric(self):
        "Function should fail with non-numeric input"
        self.assertRaises(ValueError, mask_all_nans,
                          "i'm a string",
                          range(10))
