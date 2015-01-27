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
