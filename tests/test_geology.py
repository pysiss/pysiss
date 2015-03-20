""" file:  test_geology.py
    author: Jess Robertson
            Minerals Resources National Research Flagship
    date:   Wednesday January 14, 2015

    description: Functional tests using geology data and GA's WFS
"""

import unittest
from decorators import slow

from pysiss.geospatial import feature

BOUNDS = (119.52, -21.6, 120.90, -20.5)
WFSURL = "http://www.ga.gov.au/geows/{0}/oneg_wa_1m/wfs"
GEOLOGIC_OBJECTS = ('contacts', 'faults', 'geologicunits')

@unittest.skip("Skipping geology for now")
class GeologyTest(unittest.TestCase):

    """ Run a functional test using geological WFS data
    """

    @unittest.skip("Skipping feature request for now")
    def test_getting_geology(self):
        """ Test recovery of geology data from GA's WFS
        """
        url = WFSURL.format(GEOLOGIC_OBJECTS[2])
        requester = vector.WFSRequester(url)
        response = requester.request(bounds=BOUNDS)

        # Check that we get back some gsml:GeologicUnit features
        geologic_units = response['gsml:GeologicUnit']
        self.assertNotEqual(geologic_units, [],
                            'vector requester should return gsml:GeologicUnit '
                            'features')
        unit = geologic_units[0]
        self.assertEquals(unit.metadata.tree.tag,
                          '{urn:cgi:xmlns:CGI:GeoSciML:2.0}GeologicUnit')
        self.assertEquals(self.ns.shorten(unit.metadata.tree.tag),
                          'gsml:GeologicUnit')
