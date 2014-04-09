""" file: test_siss.py

    author: David Benn
            CSIRO IM&T Science Data Services 
    date: 18 February 2014

    description: Test of siss module for creating PropertyType objects from
                 GeoSciML.
"""

import pyboreholes as pybh
import unittest

class SissTest(unittest.TestCase):

    def setUp(self):
        self.siss = pybh.SISSBoreholeGenerator()

    def test_geosciml_nvcl_1(self):
        """
        NVCL URL from GeoSciML https://twiki.auscope.org/wiki/CoreLibrary/NVCLGovHackOverview#Requesting_Boreholes
        """
        url = 'http://nvclwebservices.vm.csiro.au/geoserverBH/wfs?service=WFS&version=1.1.0&request=GetFeature&typeName=gsml:Borehole&maxFeatures=5'
        
        boreholes = self.siss.geosciml_to_boreholes(url)
                        
        expected_positions = {u'gsml.borehole.150390': u'Origin position: latitude -29.804238, longitude 139.007411',
                          u'gsml.borehole.205822': u'Origin position: latitude -29.804238, longitude 139.007411',
                          u'gsml.borehole.BUGD049': u'Origin position: latitude -30.5278, longitude 121.058',
                          u'gsml.borehole.EBSAE6': u'Origin position: latitude -31.1104, longitude 137.149',
                          u'gsml.borehole.GSDD006': u'Origin position: latitude -30.0897, longitude 121.02'}

        expected_details = {u'gsml.borehole.150390': u"Borehole detail: BoreholeDetail(name='drilling method', values=u'Diamond', property_type=None)",
                          u'gsml.borehole.205822': u"Borehole detail: BoreholeDetail(name='drilling method', values=u'Diamond', property_type=None)",
                          u'gsml.borehole.BUGD049': u"Borehole detail: BoreholeDetail(name='drilling method', values=u'diamond core', property_type=None)",
                          u'gsml.borehole.EBSAE6': u"Borehole detail: BoreholeDetail(name='drilling method', values=u'diamond core', property_type=None)",
                          u'gsml.borehole.GSDD006': u"Borehole detail: BoreholeDetail(name='drilling method', values=u'diamond core', property_type=None)"}
        
        for borehole in boreholes:
            self.assertEquals(expected_positions[borehole.name], str(borehole.origin_position))
            self.assertEquals(expected_details[borehole.name], str(borehole.details))
            