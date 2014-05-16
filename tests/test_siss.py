""" file: test_siss.py

    author: David Benn
            CSIRO IM&T Science Data Services
    date: 18 February 2014

    description: Test of siss module for creating PropertyType objects from
                 GeoSciML.
"""

from owslib.wfs import WebFeatureService
import pyboreholes.importers.nvcl as nvcl
import urllib
import xml.etree.ElementTree

import pyboreholes as pybh
import unittest

from pprint import pprint


class SissTest(unittest.TestCase):

    def setUp(self):
        self.siss = pybh.SISSBoreholeGenerator()

    def test_geosciml_nvcl_scanned_borehole(self):
        """ A test using one of the scanned borehole GeoSciML URLs returned by
            nvcl.get_borehole_ids()
        """
        bh_urls = ['http://nvclwebservices.vm.csiro.au/resource/feature/' +
                   'CSIRO/borehole/WTB5']
        boreholes = []

        for bh_url in bh_urls:
            bh_name = bh_url[bh_url.rfind('/') + 1:]
            boreholes.append(
                self.siss.geosciml_to_borehole(bh_name,
                                               urllib.urlopen(bh_url)))

        expected_positions = {u'WTB5': u'latitude -28.4139, longitude 121.142'}

        expected_details = {u'WTB5': u"{'drilling method': "
                                     u"BoreholeDetail(name='drilling method', "
                                     u"values='diamond core', "
                                     u"property_type=None)}"}

        for borehole in boreholes:
            self.assertEquals(expected_positions[borehole.name],
                              str(borehole.origin_position))
            self.assertEquals(expected_details[borehole.name],
                              str(borehole.details))

    def _test_wfs(self):
        """ WFS test (exploratory)
        """
        providerkey = 'CSIRO'
        endpoint = nvcl.NVCL_ENDPOINTS[providerkey]
        wfs = WebFeatureService(endpoint['wfsurl'], version='1.1.0')
        wfsresponse = wfs.getfeature(typename='gsml:Borehole', maxfeatures=5)
        xmltree = xml.etree.ElementTree.parse(wfsresponse)
        pprint(xmltree)
        matches = xmltree.findall('.//{http://www.opengis.net/gml}id')
        print matches
        matches = xmltree.findall('.//{http://www.opengis.net/gml}Point')
        print matches
        matches = xmltree.findall(
            './/{urn:cgi:xmlns:CGI:GeoSciML:2.0}Borehole')
        print matches
