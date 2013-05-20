#!/usr/bin/env python
""" file:   test_borehole_data.py (borehole_analysis)
    author: Jess Robertson
            CSIRO Earth Science and Resource Engineering
    email:  jesse.robertson@csiro.au
    date:   Wednesday May 1, 2013

    description: Data munging utilities for the borehole_analysis module.
"""

import unittest, numpy, itertools
from borehole_analysis.borehole import *

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

class TestBorehole(unittest.TestCase):
    
    """ Testing Borehole class
    """

    def setUp(self):
        "Test suite set up"
        self.test_file = 'tests/MKD_PGE_profile.csv'
        self.domain_key='Depth'
        self.data_keys=['Ru', 'Pt', 'Ni', 'MgO', 'S*', 'Pd', 'Rh', 'Al2O3', 
                'Co', 'Ir', 'Cr', 'Cu']

    def test_init(self):
        "BoreholeData class should initialise without errors."
        bore = Borehole()
        bore.import_from_csv(self.test_file, 
            domain_key=self.domain_key, 
            data_keys=self.data_keys)

    def test_resample(self):
        "Resampling should give vectors of known length"
        bore = Borehole()
        bore.import_from_csv(self.test_file, 
            domain_key=self.domain_key, 
            data_keys=self.data_keys)
        for nsamples in [10, 100, 34, 97]:
            bore.resample(nsamples=nsamples, normalize=False)
            self.assertTrue(bore.data.shape == (nsamples, len(self.data_keys)))

    def test_normalisation(self):
        "Normalisation should give zero mean and unit std-dev"
        bore = Borehole()
        bore.import_from_csv(self.test_file, 
            domain_key=self.domain_key, 
            data_keys=self.data_keys)
        bore.resample(normalize=True)
        for mu, sigma in zip(bore.data.mean(axis=0), bore.data.std(axis=0)):
            self.assertTrue(mu ** 2 < 1e-10)
            self.assertTrue((sigma - 1)** 2 < 1e-10)

    def test_normalisation_default(self):
        "Normalisation should default to False"
        bore = Borehole()
        bore.import_from_csv(self.test_file,
            domain_key=self.domain_key,
            data_keys=self.data_keys)
        bore.resample()
        for mu, sigma in zip(bore.data.mean(axis=0), bore.data.std(axis=0)):
            self.assertFalse(mu ** 2 < 1e-10)
            self.assertFalse((sigma - 1)** 2 < 1e-10)

if __name__ == '__main__':
    unittest.main()