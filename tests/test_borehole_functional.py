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

class TestBoreholeFunctional(unittest.TestSuite):

    """ Functional tests to demonstrate Borehole usage
    """

    def test_borehole_functional():
        """ Functional test using borehole data
        """
        # If you don't know what endpoints are available, you can instantiate
        # an NVCL endpoint registry, and see what's available
        registry = nvcl.NVCLEndpointRegistry()
        gswa = nvcl.NVCLImporter(registry['GSWA'])

        # So we can query the importer to find out what boreholes are
        # available at this endpoint
        with HTTMock(mock_resource):
            for ident, url in gswa.get_borehole_idents_and_urls().items():
                print ident, url

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

        # Try some groupby operations on the data
        counts = data.groupby(['Grp1sTSAS']).agg(len).ix[:,0]

class TestBoreholeFunctionalSynthetic(unittest.TestSuite):

    """ Test some stuff with boreholes using some confected data
    """

    def setUp():
        self.bh = synthetic_borehole()
        self.intdom = bh.interval_datasets['geochemistry']

    def test_init():
        """ Borehole should have some basic bits available
        """
        self.assertTrue(len(bh.interval_datasets) > 0)
        self.assertTrue(len(intdom.from_depths) > 0)

    def test_intdom_split_at_gaps():
        """ Split_at_gaps should work ok
        """
        self.intdom.split_at_gaps()
        self.assertTrue(self.intdom.gaps is not None)

    def test_interval_to_sampling():
        """ We should be able to add a new sampling domain ok
        """
        # Convert geochemistry IntervalDataSet to SamplingDataSet
        midpoints = (self.intdom.from_depths
                     + self.intdom.to_depths) / 2.
        sampdom = bh.add_point_dataset('geochemistry', midpoints)
        self.assertTrue(len(self.bh.sampling_datasets) > 0)
        for prop in self.intdom.properties.values():
            sampdom.add_property(prop.property_type, prop.values)

        # Check that everthings been added
        for key in self.intdom.properties.keys():
            self.assertTrue(key in sampdom.properties.keys())

    def test_regularization():
        """ Regularization should work ok for dataset
        """
        # Convert geochemistry IntervalDataSet to SamplingDataSet
        midpoints = (self.intdom.from_depths
                     + self.intdom.to_depths) / 2.
        sampdom = bh.add_point_dataset('geochemistry', midpoints)
        self.assertTrue(len(self.bh.sampling_datasets) > 0)
        for prop in self.intdom.properties.values():
            sampdom.add_property(prop.property_type, prop.values)

        # Regularise geochemistry dataset
        sampdom.split_at_gaps()
        self.assertTrue(sampdom.gaps is not None)
        resampled = sampdom.regularize(degree=1)
        bh.add_dataset(resampled)
        self.assertTrue(len(bh.sampling_datasets) > 1)
        self.assertEqual(len(samdom.depths), len(resampled.depths))
