""" file: test_utilities.py
    author: Jess Robertson
            CSIRO Earth Science and Resource Engineering
    date: Tuesday May 14, 2013

    description: unittests for utilities.py
"""

import unittest
import numpy
from python_boreholes import *
from python_boreholes.utilities import *

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

class TestDetrend(unittest.TestCase):

    """ Unit tests for cwavelets.detrend
    """

    def setUp(self):
        # Data and expected results
        self.data = numpy.linspace(0, 1)
        zeros = numpy.zeros_like(self.data, dtype=numpy.float_)
        self.expected = {
            'none': numpy.linspace(0, 1),
            'mean': numpy.linspace(-0.5, 0.5),
            'linear': zeros,
            'quadratic': zeros,
            'cubic': zeros,
        }

        # Checking for equality between float arrays
        tiny = 1e-10 # should really use numpy.MachAr().tiny
        self.narray_eq = lambda a, b: numpy.all((a - b) ** 2 < tiny)

    def test_detrend_modification(self):
        """ Data should be modified in place
        """
        data = numpy.linspace(0, 1)
        self.assertEqual(detrend(data), None)

    def test_detrend_values(self):
        """ Test values returned by detrend
        """
        for trend, exp_values in self.expected.items():
            data = numpy.linspace(0, 1) # Need to recreate data after detrend
            self.assertEqual(detrend(data, trend), None)
            self.assertTrue(self.narray_eq(data, exp_values))

    def test_default_detrend(self):
        """ Detrend should default to linear detrending
        """
        data = numpy.linspace(0, 1)
        detrend(data)
        self.assertTrue(self.narray_eq(data, self.expected['linear']))
