""" file: test_feature.py
    author: Jess Robertson
            CSIRO Minerals Resources Flagship
    date:   January 2015

    description: Tests of classes for feature data
"""

from pysiss import geospatial, webservices
from mocks.resource import mock_resource

import unittest

WFSURL = ("http://www.ga.gov.au/geows/{0}/oneg_wa_1m/wfs")
GEOLOGIC_OBJECTS = ('contacts', 'faults', 'geologicunits')

class TestFeatureService(unittest.TestCase):

    def setUp(self):
        with httmock.HTTMock(mock_resource):
            for obj in GEOLOGIC_OBJECTS:
                self.wcs[obj] = webservices.FeatureService(WFSURL)

    def test_capabilities(self):
        """ FeatureService should configure itself from the endpoint
            capabilities
        """
        with httmock.HTTMock(mock_resource):
            for obj in GEOLOGIC_OBJECTS:
                self.assertTrue(
                    self.wcs[obj].capabilities is not None)
                self.assertTrue(
                    self.wcs[obj].version is not None)
