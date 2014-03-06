#!/usr/bin/env python
""" file: test_siss.py

    author: David Benn
            CSIRO IM&T Science Data Services 
    date: 18 February 2014

    description: Test of siss module for creating PropertyType objects from
                 GeoSciML.
"""

import pyboreholes as pybh
import unittest
from pprint import pprint

class SissTest(unittest.TestCase):

     def setUp(self):
         self.siss = pybh.SISS()

     def test_geosciml_nvcl_1(self):
         """
         NVCL URL from GeoSciML https://twiki.auscope.org/wiki/CoreLibrary/NVCLGovHackOverview#Requesting_Boreholes
         """
         url = 'http://nvclwebservices.vm.csiro.au/geoserverBH/wfs?service=WFS&version=1.1.0&request=GetFeature&typeName=gsml:Borehole&maxFeatures=5'

         prop_type_dict = self.siss.geosciml_to_prop_types(url)
         
         keys = sorted(prop_type_dict)
         
         self.assertEquals(5, len(keys))
         
         expected_props = {u'gsml.borehole.150390': [u'gsml.borehole.150390',
                                                     u'-29.804238 degs lat',
                                                     u'139.007411 degs lon'],
                           u'gsml.borehole.205822': [u'gsml.borehole.205822',
                                                     u'-29.804238 degs lat',
                                                     u'139.007411 degs lon'],
                           u'gsml.borehole.BUGD049': [u'gsml.borehole.BUGD049',
                                                      u'-30.5278 degs lat',
                                                      u'121.058 degs lon'],
                           u'gsml.borehole.EBSAE6': [u'gsml.borehole.EBSAE6',
                                                     u'-31.1104 degs lat',
                                                     u'137.149 degs lon'],
                           u'gsml.borehole.GSDD006': [u'gsml.borehole.GSDD006',
                                                      u'-30.0897 degs lat',
                                                      u'121.02 degs lon']}

         for borehole_id in keys:
              prop_types = prop_type_dict[borehole_id]
              expected = [name for name in expected_props[borehole_id]]
              actual = [prop_type.name for prop_type in prop_types]
              self.assertEquals(expected, actual)
             
if __name__ == '__main__':
    unittest.main()
