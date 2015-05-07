""" file:   test_metadata.py
    author: Jess Robertson
            CSIRO Earth Science and Resource Engineering
    date:   Tuesday 2 May, 2015

    description: Tests for metadata class
"""

from __future__ import print_function, division

from pysiss.webservices import nvcl
from pysiss.metadata import xml_to_metadata

import unittest
import httmock
import requests

from mocks.resource import mock_resource


class TestMetadata(unittest.TestCase):

    def setUp(self):
        # Get a pointer to the NVCL endpoint registry
        registry = nvcl.NVCLEndpointRegistry()

        # Make a request to the wfs
        payload = {
            'version': '1.1.0',
            'service': 'wfs',
            'request': 'getfeature',
            'typename': 'nvcl:ScannedBoreholeCollection'
        }
        self.response = requests.get(registry['GSWA']['wfsurl'],
                                     params=payload)
        self.response.raise_for_status()

    def test_that_weve_got_something_to_play_with(self):
        """ Check that we've got a response to play with
        """
        self.assertIsNotNone(self.response.content)

    def test_metadata_length(self):
        """ Check that the metadata conversion results in the right number of
            items.
        """
        mdata = xml_to_metadata(self.response.content)
        bh_elems = mdata.xpath('.//nvcl:scannedBorehole')
        self.assertTrue(len(list(mdata.yaml())) > 10)
        self.assertTrue(len(bh_elems) > 0)

    def test_metadata_queries(self):
        """ Check that queries can run multiple times and get the same results
        """
        mdata = xml_to_metadata(self.response.content)
        elems = mdata['.//nvcl:scannedBorehole']
        self.assertTrue(len(elems) > 0)
        elems2 = mdata['.//nvcl:scannedBorehole']
        self.assertEqual(len(elems2), len(elems)) 
