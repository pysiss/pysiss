#!/usr/bin/env python
""" file:   test_detrend.py
    author: Jess Robertson,
            CSIRO Earth Science and Resource Engineering
    date:   Tuesday November 19, 2013

    description: Tests for detrending functions
"""

import unittest
import numpy
from pysiss.borehole.analysis import detrend


class TestDetrend(unittest.TestCase):

    """ Unit tests for pysiss.borehole.analysis.detrend
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
        tiny = 1e-10  # should really use numpy.MachAr().tiny
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
            data = numpy.linspace(0, 1)  # Need to recreate data after detrend
            self.assertEqual(detrend(data, trend), None)
            self.assertTrue(self.narray_eq(data, exp_values))

    def test_default_detrend(self):
        """ Detrend should default to linear detrending
        """
        data = numpy.linspace(0, 1)
        detrend(data)
        self.assertTrue(self.narray_eq(data, self.expected['linear']))
