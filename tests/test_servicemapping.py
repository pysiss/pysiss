""" file: test_servicemapping.py
    author: Jess Robertson
            CSIRO Mineral Resources Flagship
    date:   Monday February 2, 2015

    description: Tests for utilities to describe service mapping from
        values to the correct version of the OGC Webservice API.
"""

from pysiss.webservices.ogc.mapping import OGCServiceMapping, _parse_parameters
import unittest

class TestServiceMapping(unittest.TestCase):

    """ Tests for ServiceMapping object
    """

    def setUp(self):
        self.mapping = OGCServiceMapping(service='wcs', version='1.1.0')

    def test_init(self):
        print self.mapping.parameters
        print self.mapping.request(request='getcapabilities',
                                   method='get')

if __name__ == '__main__':
    unittest.main()
