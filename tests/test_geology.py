""" file:  test_geology.py
    author: Jess Robertson
            Minerals Resources National Research Flagship
    date:   Wednesday January 14, 2015

    description: Functional tests using geology data and GA's WFS
"""

import unittest
from decorators import slow

from pysiss.coverage import vector

BOUNDS = (119.52, -21.6, 120.90, -20.5)
WFSURL = 'http://aster.nci.org.au/thredds/wcs/aster/vnir/Aus_Mainland/' \
         'Aus_Mainland_{0}_reprojected.nc4'


class GeologyTest(unittest.TestCase):

    """ Run a functional test using geological WFS data
    """

    def setUp(self):
        pass

    @slow
    def test_getting_geology(self):
        """ Test recovery of geology data from GA's WFS
        """
        url = WFSURL.format()
        requester = vector.WFSRequester(url)
