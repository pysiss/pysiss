""" file: test_raster.py
    author: Jess Robertson
            CSIRO Minerals Resources Flagship
    date:   Monday 25 August, 2014

    desription: Implementation of classes for raster coverage data
"""

from pysiss import coverage as cv
import unittest

# Products to pull
ASTER_PRODUCTS = [
    'AlOH_group_composition',
    'Ferric_oxide_composition',
    'MgOH_group_composition'
]
BOUNDS = (119.52, -21.6, 120.90, -20.5)
WCSURL = ('http://aster.nci.org.au/thredds/wcs/aster/vnir/'
          'Aus_Mainland/Aus_Mainland_{0}_reprojected.nc4')
TEST_FILE = 'AlOH_group_composition.geotiff'


class BoreholeTest(unittest.TestCase):

    def setUp(self):
        self.raster = cv.Raster()

    def tearDown(self):
        del self.raster

    def test_load_from_file():
        raise Exception("Finish this test!")

    def test_load_from_wcs():
        raise Exception("Finish this test!")
