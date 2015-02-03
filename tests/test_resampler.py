#!/usr/bin/env python
""" file:   test_resampler.py
    author: Jess Robertson,
            CSIRO Earth Science and Resource Engineering
    date:   Tuesday November 19, 2013

    description: Tests for detrending functions
"""

import unittest
import numpy
from pysiss.borehole.analysis import ReSampler, unique

class TestReSampler(unittest.TestCase):

    """ Tests for ReSampler class
    """

    def setUp(self):
        self.depths = numpy.random.uniform(size=10)
        self.data = numpy.random.uniform(size=10)

    def test_resampler_init(self):
        """ ReSampler should init without problems
        """
        sampler = ReSampler(self.depths, self.data)
        self.assertTrue(sampler.order, 3)
        self.assertTrue(numpy.allclose(sampler.sample_locations,
                                       self.depths))
        self.assertTrue(numpy.allclose(sampler.signal, self.data))

    def test_resampler_wrong_length(self):
        """ Wrong length inputs should kill the ReSampler
        """
        self.assertRaises(ValueError, ReSampler, self.depths[:-1], self.data)

    def test_resample_lengths(self):
        """ Resampled lengths should match what's specified
        """
        sampler = ReSampler(self.depths, self.data)
        for length in (1, 3, 10, 100, 5291):
            xs, ys = sampler.resample(length)
            self.assertEqual(len(xs), length)
            self.assertEqual(len(ys), length)

    def test_resample_order(self):
        """ Different orders should work ok
        """
        for order in range(1, 4):
            sampler = ReSampler(self.depths, self.data, order=order)
            xs, ys = sampler.resample(10)

    def test_resample_derivative(self):
        """ Different orders should work ok
        """
        for derivative in range(0, 4):
            sampler = ReSampler(self.depths, self.data)
            xs, ys = sampler.resample(10, derivative=derivative)


class TestUnique(unittest.TestCase):

    """ Tests for unique function
    """

    def setUp(self):
        self.data = [1, 3, 3, 6, 3, 7, 8]
        self.expected = [1, 3, 6, 7, 8]

    def test_unique(self):
        """ Unique function should sort data nicely
        """
        result = unique(self.data,
                        return_index=False)
        self.assertTrue(
            all(a == b for a, b in zip(result, self.expected)))

    def test_empty_unique(self):
        """ Empty unique returns empty list
        """
        result = unique([], return_index=False)
        self.assertEqual(result.shape, (0,))

    def test_uniqe_methods(self):
        """ Different methods should work ok
        """
        sort_methods = ('heapsort', 'quicksort', 'mergesort')
        for sort_method in sort_methods:
            result = unique(self.data,
                return_index=False,
                sort_method=sort_method)
            self.assertTrue(
                all(a == b for a, b in zip(result, self.expected)))

    def test_equality_methods(self):
        """ Different equality tests should work
        """
        eqtests = [lambda a, b: a == b,
                    lambda a, b: (a - b) ** 2 < 0.001]
        for eqtest in eqtests:
            result = unique(self.data,
                return_index=False,
                eqtest=eqtest)
            self.assertTrue(
                all(a == b for a, b in zip(result, self.expected)))
