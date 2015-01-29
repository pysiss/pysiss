""" file:  test_aster.py
    author: Jess Robertson
            Minerals Resources National Research Flagship
    date:   Wednesday January 14, 2015

    description: Functional tests using ASTER data and GA's WFS
"""

# import matplotlib.pyplot as plt
# import numpy as np
import rasterio
import os

import unittest
from decorators import slow

from pysiss.geospatial import coverage
from pysiss.webservices import CoverageService

ASTER_PRODUCTS = [
    'AlOH_group_composition',
    'Ferric_oxide_composition',
    'MgOH_group_composition'
]
BOUNDS = (119.52, -21.6, 120.90, -20.5)
WCSURL = 'http://aster.nci.org.au/thredds/wcs/aster/vnir/Aus_Mainland/' \
         'Aus_Mainland_{0}_reprojected.nc4'


class ASTERTest(unittest.TestCase):

    """ Run a functional test using ASTER data
    """

    def setUp(self):

        self.test_dir = os.path.dirname(os.path.realpath(__file__))
        # Just look at the first image we have
        self.filename = os.path.join(self.test_dir, 'geotiffs',
                                     ASTER_PRODUCTS[0] + '.geotiff')

    @unittest.skip("Skipping aster tests for now")
    def test_open_image(self):
        """ Test that we can use rasterio to open the images
        """
        # Use rasterio to load the geotiff
        with rasterio.drivers():
            with rasterio.open(self.filename) as src:
                self.assertEqual(src.crs_wkt,
                                 'GEOGCS["WGS 84",DATUM["WGS_1984",'
                                 'SPHEROID["WGS 84",6378137,298.257223563,'
                                 'AUTHORITY["EPSG","7030"]],'
                                 'AUTHORITY["EPSG","6326"]],'
                                 'PRIMEM["Greenwich",0],'
                                 'UNIT["degree",0.0174532925199433],'
                                 'AUTHORITY["EPSG","4326"]]')
                for sbound, bound in zip(src.bounds, BOUNDS):
                    self.assertTrue((sbound - bound) ** 2 < 0.01)

    @unittest.skip("Skipping aster tests for now")
    def test_get_aster_images(self):
        """ Test that we can get ASTER images from the webservice
        """
        url = WCSURL.format(ASTER_PRODUCTS[0])

        # Generate a coverage object from a coverage reader
        requester = CoverageService(url)
        src = requester.request(bounds=BOUNDS)
        self.assertEqual(
            src.crs_wkt,
            'GEOGCS["WGS 84",DATUM["WGS_1984",'
            'SPHEROID["WGS 84",6378137,298.257223563,'
            'AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],'
            'PRIMEM["Greenwich",0],UNIT["degree",0.0174532925199433],'
            'AUTHORITY["EPSG","4326"]]')
        for sbound, bound in zip(src.bounds, BOUNDS):
            self.assertTrue((sbound - bound) ** 2 < 0.01)
