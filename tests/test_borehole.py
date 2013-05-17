#!/usr/bin/env python
""" file:   test_borehole_data.py (borehole_analysis)
    author: Jess Robertson
            CSIRO Earth Science and Resource Engineering
    email:  jesse.robertson@csiro.au
    date:   Wednesday May 1, 2013

    description: Data munging utilities for the borehole_analysis module.
"""

import unittest
from borehole_analysis import Borehole

class TestBoreholeData(unittest.TestCase):
    
    """ Testing BoreholeData class
    """

    def test_init(self):
        "BoreholeData class should initialise without errors."
        bore = Borehole()

    def test_normalisation(self):
        "Normalisation should give zero mean and unit std-dev"
        bore = Borehole()
        bore.import_from_csv('tests/MKD_PGE_profile.csv', domain_key='Depth', not_float=['Zone'])
        bore.align_data()
        for mu, sigma in zip(bore.data.mean(axis=0), bore.data.std(axis=0)):
            self.assertTrue(mu ** 2 < 1e-10)
            self.assertTrue((sigma - 1)** 2 < 1e-10)

if __name__ == '__main__':
    unittest.main()