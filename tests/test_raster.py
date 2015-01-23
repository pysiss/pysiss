""" file: test_raster.py
    author: Jess Robertson
            CSIRO Minerals Resources Flagship
    date:   January 2015

    description: Tests of classes for raster coverage data
"""

from pysiss import coverage, webservices

import unittest
import numpy
import os

# ASTER products for tests
BOUNDS = (119.52, -21.6, 120.90, -20.5)
WCSURL = ('http://aster.nci.org.au/thredds/wcs/aster/vnir/'
          'Aus_Mainland/Aus_Mainland_AlOH_group_composition_reprojected.nc4')
TEST_FILE = '{0}/resources/MgOH_group_composition.geotiff'


class WCSTest(unittest.TestCase):

    def test_wcs_init(self):
        """ WebCoverageService should initialize without errors
        """
        wcs = webservices.CoverageService(WCSURL)
        self.assertTrue(wcs.version is not None)
        self.assertTrue(wcs.endpoint == WCSURL.split('?')[0])
        self.assertTrue(wcs.capabilities is not None)
        self.assertTrue(wcs.descriptions is not None)
        self.fail('Finish this test')


class RasterTest(unittest.TestCase):

    def setUp(self):
        test_dir = os.path.dirname(os.path.realpath(__file__))
        self.raster = coverage.Raster(
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
