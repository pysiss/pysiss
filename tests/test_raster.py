""" file: test_raster.py
    author: Jess Robertson
            CSIRO Minerals Resources Flagship
    date:   Monday 25 August, 2014

    description: Tests of classes for raster coverage data
"""

from pysiss import coverage as cv

import unittest
import numpy

# ASTER products for tests
BOUNDS = (119.52, -21.6, 120.90, -20.5)
WCSURL = ('http://aster.nci.org.au/thredds/wcs/aster/vnir/'
          'Aus_Mainland/Aus_Mainland_AlOH_group_composition_reprojected.nc4')
TEST_FILE = 'resources/AlOH_group_composition.geotiff'


class RasterTest(unittest.TestCase):

    def setUp(self):
        self.raster = cv.Raster(
            filename=TEST_FILE)

    def tearDown(self):
        del self.raster

    def test_file_init(self):
        """ Raster object should load from file with no errors
        """
        self.assertTrue(self.raster.ident is not None)
        self.assertTrue(self.raster.metadata is not None)
        self.assertTrue(self.raster.projection is not None)
        self.assertTrue(numpy.allclose(self.raster.bounds,
                                       BOUNDS))
        self.fail('Finish this test')

    def test_wcs_init(self):
        """ Raster object should load from WCS with no errors
        """
        self.fail('Finish this test')

if __name__ == '__main__':
    unittest.main()
