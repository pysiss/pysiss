""" file: test_raster.py
    author: Jess Robertson
            CSIRO Minerals Resources Flagship
    date:   January 2015

    description: Tests of classes for raster coverage data
"""

from pysiss import geospatial, webservices
from mocks.resource import mock_resource

import unittest
import numpy
import os
import httmock

# ASTER products for tests
BOUNDS = (119.52, -21.6, 120.90, -20.5)
WCSURL = ('http://aster.nci.org.au/thredds/wcs/aster/vnir/'
          'Aus_Mainland/Aus_Mainland_AlOH_group_composition_reprojected.nc4')
TEST_FILE = '{0}/resources/AlOH_group_composition.geotiff'


class TestRasterCoverage(unittest.TestCase):

    # testversions = ('1.0.0', '1.1.0', '2.0.0')
    testversions = ('1.0.0', '1.1.0')

    def setUp(self):
        with httmock.HTTMock(mock_resource):
            self.wcs = webservices.CoverageService(WCSURL)

    def test_wcs_init(self):
        """ WebCoverageService should initialize without errors
        """
        self.assertTrue(self.wcs.version is not None)
        self.assertTrue(self.wcs.endpoint == WCSURL.split('?')[0])

    def test_wcs_capabilities(self):
        """ Check that values are initialized by calls to wcs capabilities
        """
        self.assertTrue(self.wcs.capabilities is not None)

    def test_wcs_descriptions(self):
        """ Check that descriptions are pulled in ok
        """
        self.assertTrue('AlOH_group_composition' in
                        self.wcs.descriptions.keys())
        desc = self.wcs.descriptions['AlOH_group_composition']
        self.assertTrue(desc.mdatatype == 'wcs:describecoverage')

    def test_layers(self):
        """ Check that layers are decoded
        """
        self.assertTrue('AlOH_group_composition' in self.wcs.layers)

    def test_getcapabilties_payload_creation(self):
        """ Check that payloads get created ok
        """
        # Modify for other versions
        for version in self.testversions:
            self.wcs._version = version
            self.wcs._make_payload('getcapabilities')

    def test_borked_describecoverage_payload_creation(self):
        """ Check that describecoverage payloads get created ok
        """
        layer = self.wcs.layers[0]

        # Modify for other versions
        for version in self.testversions:
            self.wcs._version = version
            self.wcs._make_payload('describecoverage',
                                   ident=layer)

    def test_borked_describecoverage_payload_creation(self):
        """ Borked arguments should raise a KeyError
        """
        # Modify for other versions
        for version in self.testversions:
            self.wcs._version = version
            self.assertRaises(KeyError,
                              self.wcs._make_payload,
                              request='describecoverage')
            self.assertRaises(KeyError,
                              self.wcs._make_payload,
                              'describecoverage')


class CoverageTest(unittest.TestCase):

    def setUp(self):
        test_dir = os.path.dirname(os.path.realpath(__file__))
        self.raster = geospatial.Coverage(
            filename=TEST_FILE.format(test_dir))

    def tearDown(self):
        del self.raster

    @unittest.skip('Skipping file init for now')
    def test_file_init(self):
        """ Raster object should load from file with no errors
        """
        self.assertTrue(self.raster.ident is not None)
        self.assertTrue(self.raster.metadata is not None)
        self.assertTrue(self.raster.projection is not None)
        self.assertTrue(numpy.allclose(self.raster.bounds,
                                       BOUNDS))
