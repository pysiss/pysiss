#!/usr/bin/env python
""" file:   test_borehole_functional.py
    author: Jess Robertson
            CSIRO Earth Science and Resource ENgineering
    date:   January 20, 2015

    description: Functional tests to demonstrate the borehole model.
"""

from pysiss.webservices import nvcl

import unittest
from httmock import HTTMock
from .mocks.resource import mock_resource
from .mocks.geology import synthetic_borehole
import logging


class TestBoreholeFunctional(unittest.TestCase):

    """ Functional tests to demonstrate Borehole usage
    """

    def test_borehole_functional(self):
        """ Functional test using borehole data
        """
        # If you don't know what endpoints are available, you can instantiate
        # an NVCL endpoint registry, and see what's available
        registry = nvcl.NVCLEndpointRegistry()
        gswa = nvcl.NVCLImporter('GSWA')

        # So we can query the importer to find out what boreholes are
        # available at this endpoint
        with HTTMock(mock_resource):
            for ident, url in gswa.get_borehole_idents_and_urls().items():
                logging.info('Found data {0} at {1}'.format(
                            ident, url))

        # And we can get all the datasets as a Borehole instance
        with HTTMock(mock_resource):
            bhole = gswa.get_borehole('PDP2C')

        # We can checkout the pointdatasets that we've gotten back
        self.assertTrue(bhole.point_datasets['PDP2C'] is not None)
        data = bhole.point_datasets['PDP2C']
        self.assertTrue(data.properties is not None)

        # And we can munge this into a Pandas dataframe
        data = data.to_dataframe()
        data.head()


class TestBoreholeFunctionalSynthetic(unittest.TestCase):

    """ Test some stuff with boreholes using some confected data
    """

    def setUp(self):
        self.bh = synthetic_borehole()
        self.intdom = self.bh.interval_datasets['geochemistry']

        # Convert geochemistry IntervalDataSet to SamplingDataSet
        midpoints = (self.intdom.from_depths
                     + self.intdom.to_depths) / 2.
        self.sampdom = self.bh.add_point_dataset('geochemistry', midpoints)
        for prop in self.intdom.properties.values():
            self.sampdom.add_property(prop.property_type, prop.values)

    def test_init(self):
        """ Borehole should have some basic bits available
        """
        self.assertTrue(len(self.bh.interval_datasets) > 0)
        self.assertTrue(len(self.intdom.from_depths) > 0)

    def test_intdom_split_at_gaps(self):
        """ Split_at_gaps should work ok
        """
        self.intdom.split_at_gaps()
        self.assertTrue(self.intdom.gaps is not None)

    def test_sampdom_split_at_gaps(self):
        """ Split_at_gaps should work ok
        """
        self.sampdom.split_at_gaps()
        self.assertTrue(self.sampdom.gaps is not None)

    def test_sampdom_reglarize(self):
        """ Regularize should work ok
        """
        # Should also work if gaps not found
        self.sampdom.gaps = None
        _ = self.sampdom.regularize(degree=2)
        new_data = self.sampdom.regularize(npoints=200, degree=2)
        self.assertEqual(len(new_data.depths), 200)

    def test_interval_to_sampling(self):
        """ We should be able to add a new sampling domain ok
        """
        # Convert geochemistry IntervalDataSet to SamplingDataSet
        midpoints = (self.intdom.from_depths
                     + self.intdom.to_depths) / 2.
        sampdom = self.bh.add_point_dataset('geochemistry', midpoints)
        self.assertTrue(len(self.bh.point_datasets) > 0)
        for prop in self.intdom.properties.values():
            sampdom.add_property(prop.property_type, prop.values)

        # Check that everthings been added
        for key in self.intdom.properties.keys():
            self.assertTrue(key in sampdom.properties.keys())

    def test_regularization(self):
        """ Regularization should work ok for dataset
        """
        # Convert geochemistry IntervalDataSet to SamplingDataSet
        midpoints = (self.intdom.from_depths
                     + self.intdom.to_depths) / 2.
        sampdom = self.bh.add_point_dataset('geochemistry', midpoints)
        self.assertTrue(len(self.bh.point_datasets) > 0)
        for prop in self.intdom.properties.values():
            sampdom.add_property(prop.property_type, prop.values)

        # Regularise geochemistry dataset
        sampdom.split_at_gaps()
        self.assertTrue(sampdom.gaps is not None)
        resampled = sampdom.regularize(degree=1)
        self.bh.add_dataset(resampled)
        self.assertTrue(len(self.bh.point_datasets) > 1)
        self.assertTrue(len(sampdom.depths) < len(resampled.depths))


if __name__ == "__main__":
    unittest.main()
