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
import shutil
import httmock

# ASTER products for tests
BOUNDS = (119.5, -20.6, 119.6, -20.5)
WCSURL = ('http://aster.nci.org.au/thredds/wcs/aster/vnir/'
          'Aus_Mainland/Aus_Mainland_AlOH_group_composition_reprojected.nc4')


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

    def test_get_coverage_ident(self):
        """ Passing borked ident should raise ValueError
        """
        self.assertRaises(ValueError,
                          self.wcs.get_coverage,
                          bounds=BOUNDS,
                          ident='quux')

    def test_get_coverage_bbox(self):
        """ Passing a borked projection should raise a ValueError
        """
        self.assertRaises(ValueError,
                          self.wcs.get_coverage,
                          bounds=BOUNDS,
                          ident='AlOH_group_composition',
                          projection='quux')

    def test_get_coverage_format_borked(self):
        """ Passing a borked output format should raise a ValueError
        """
        self.assertRaises(ValueError,
                  self.wcs.get_coverage,
                  bounds=BOUNDS,
                  ident='AlOH_group_composition',
                  output_format='quux')

    def test_coverage(self):
        """ Getting a coverage should work ok
        """
        with httmock.HTTMock(mock_resource):
            coverage = \
                self.wcs.get_coverage(ident='AlOH_group_composition',
                                      bounds=BOUNDS,
                                      output_format='GeoTIFF')
        self.assertTrue(coverage.ident == 'AlOH_group_composition',)
        self.assertTrue(coverage.metadata is not None)
        self.assertTrue(coverage.projection is not None)
        for idx, expected in enumerate(BOUNDS):
            self.assertTrue((expected - coverage.bounds[idx]) ** 2 < 1e-3)
        del coverage
        shutil.rmtree('coverages')

if __name__ == '__main__':
    unittest.main()
