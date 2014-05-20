""" file: test_siss.py

    author: David Benn
            CSIRO IM&T Scientific Computing Data Processing Services
    date: 18 February 2014

    description: Test of siss module for creating Borehole objects populated
                 with GeoSciML metadata as borehole details.
"""

import urllib

import pyboreholes as pyph
import unittest
 
class SissTest(unittest.TestCase):

    def setUp(self):
        self.siss = pyph.SISSBoreholeGenerator()

    def test_geosciml_nvcl_scanned_borehole(self):
        """ A test using an XML document corresponding to a scanned 
            borehole GeoSciML URL.
        """
        bh_urls = ['http://nvclwebservices.vm.csiro.au/resource/feature/' + 
                   'CSIRO/borehole/WTB5']
        boreholes = []

        for bh_url in bh_urls:
            bh_name = bh_url[bh_url.rfind('/') + 1:]
            boreholes.append(
                self.siss.geosciml_to_borehole(bh_name,
                                               urllib.urlopen(bh_url)))

        expected_positions = {u'WTB5': u'latitude -28.4139, '
                                       u'longitude 121.142, '
                                       u'elevation 45.0'}


        expected_details = {u'WTB5': u"{'driller': "
                                     u"BoreholeDetail(name='driller', "
                                            u"values='GSWA', "
                                            u"property_type=None), " 
                                    u"'inclination type': "
                                    u"BoreholeDetail(name='inclination type', "
                                            u"values='vertical', "
                                            u"property_type=None), "
                                    u"'drilling method': "
                                    u"BoreholeDetail(name='drilling method', "
                                            u"values='diamond core', "
                                            u"property_type=None), "
                                    u"'cored interval': "
                                    u"BoreholeDetail(name='cored interval', "
                                            u"values={'lower corner': 106.0, "
                                            u"'upper corner': 249.0}, "
                                            u"property_type=None), "
                                    u"'shape': "
                                    u"BoreholeDetail(name='shape', "
                                            u"values=[-28.4139, 121.142, " 
                                            u"-28.4139, 121.142], "
                                            u"property_type=None), "
                                    u"'start point': "
                                    u"BoreholeDetail(name='start point', "
                                            u"values='natural ground surface', "
                                            u"property_type=None), "
                                    u"'date of drilling': "
                                    u"BoreholeDetail(name='date of drilling', "
                                            u"values=datetime.datetime(2004, " 
                                            u"9, 17, 0, 0), "
                                            u"property_type=None)}"}

        for borehole in boreholes:
            print borehole.name
            print borehole.origin_position
            
            for detail in sorted(borehole.details):
                bh_detail = borehole.details[detail]
                print "{0}: {1}".format(bh_detail.name, bh_detail.values)

            self.assertEquals(expected_positions[borehole.name],
                              str(borehole.origin_position))
            
            self.assertEquals(expected_details[borehole.name],
                              str(borehole.details))
                            