""" file: test_siss.py

    author: David Benn
            CSIRO IM&T Scientific Computing Data Processing Services
    date: 18 February 2014

    description: Test of siss module for creating Borehole objects populated
                 with GeoSciML metadata as borehole details.
"""

from datetime import datetime
import os
import unittest
import requests

import pysiss.borehole as pybh


class SissTest(unittest.TestCase):

    def setUp(self):
        self.siss = pybh.SISSBoreholeGenerator()
        self.test_dir = os.path.dirname(os.path.realpath(__file__))

    def tearDown(self):
        if os.path.exists('test_response_file.xml'):
            os.remove('test_response_file.xml')

    def test_geosciml_2_borehole(self):
        """ A test of GeoSciML 2.0 handling in SISSBoreholeGenerator.
            Here we read a test XML file.
        """
        xml_file = '{0}/geosciml/geo2test.xml'.format(self.test_dir)
        bh = self.siss.geosciml_to_borehole('geosciml2_test', xml_file)

        self.assertEquals(-29.804238 * self.siss.unit_reg.degree,
                          bh.origin_position.latitude)
        self.assertEquals(139.007411 * self.siss.unit_reg.degree,
                          bh.origin_position.longitude)
        self.assertEquals(0.0 * self.siss.unit_reg.meter,
                          bh.origin_position.elevation)
        self.assertEquals('elevation: Gravity-related height',
                          bh.origin_position.property_type.description)

        self.assertEquals('DMITRE', bh.details.get('driller').values)
        self.assertEquals('Diamond', bh.details.get('drilling method').values)
        self.assertEquals(datetime(year=2009, month=7, day=27),
                          bh.details.get('date of drilling').values)
        self.assertEquals('natural ground surface',
                          bh.details.get('start point').values)
        self.assertEquals('vertical',
                          bh.details.get('inclination type').values)
        self.assertEquals([90.0, 0.0, 90.0, 0.0],
                          bh.details.get('shape').values)
        self.assertEquals({'lower corner': 279.0 * self.siss.unit_reg.meter,
                           'upper corner': 351.29 * self.siss.unit_reg.meter},
                          bh.details.get('cored interval').values)
        self.assertEquals(1 * self.siss.unit_reg.meter,
                          bh.details.get('cored interval').property_type.units)

    def test_geosciml_3_borehole(self):
        """ A test of GeoSciML 3.0 handling in SISSBoreholeGenerator.
            Here we read a test XML file.
        """
        xml_file = "{0}/geosciml/geo3test.xml".format(self.test_dir)
        bh = self.siss.geosciml_to_borehole("geosciml3_test", xml_file)

        self.assertEquals(-25.0 * self.siss.unit_reg.degree,
                          bh.origin_position.latitude)
        self.assertEquals(119.0 * self.siss.unit_reg.degree,
                          bh.origin_position.longitude)
        self.assertEquals(210.0 * self.siss.unit_reg.meter,
                          bh.origin_position.elevation)
        self.assertEquals('description: Rotary Table Position',
                          bh.origin_position.property_type.description)

        self.assertEquals('Gelogical Survey of Finland',
                          bh.details.get('driller').values)
        self.assertEquals('diamond core',
                          bh.details.get('drilling method').values)
        self.assertEquals(datetime(year=1984, month=5, day=15),
                          bh.details.get('date of drilling').values)
        self.assertEquals('natural ground surface',
                          bh.details.get('start point').values)
        self.assertEquals('inclined down',
                          bh.details.get('inclination type').values)
        self.assertEquals([-25.0, 119.0, 210, -25.0, 119.01, 177],
                          bh.details.get('shape').values)
        self.assertEquals({'lower corner': 0,
                           'upper corner': 125.0},
                          bh.details.get('cored interval').values)

    def test_geosciml_nvcl_scanned_borehole(self):
        """ A test using an XML document corresponding to a scanned
            borehole GeoSciML URL.
            Note: this test has a dependency upon a NVCL web resource existing!
        """
        bh_name = 'WTB5'
        bh_url = ('http://nvclwebservices.vm.csiro.au/resource/'
                  'feature/CSIRO/borehole/WTB5')
        response = requests.get(bh_url)
        self.assertTrue(response.ok)
        with open('test_response_file.xml', 'wb') as fhandle:
            fhandle.write(response.content)
        bh = self.siss.geosciml_to_borehole(bh_name, 'test_response_file.xml')

        self.assertEquals(-28.4139 * self.siss.unit_reg.degree,
                          bh.origin_position.latitude)
        self.assertEquals(121.142 * self.siss.unit_reg.degree,
                          bh.origin_position.longitude)
        self.assertEquals(45.0 * self.siss.unit_reg.meter,
                          bh.origin_position.elevation)
        self.assertEquals('elevation: Gravity-related height',
                          bh.origin_position.property_type.description)

        self.assertEquals('GSWA', bh.details.get('driller').values)
        self.assertEquals('diamond core',
                          bh.details.get('drilling method').values)
        self.assertEquals(datetime(year=2004, month=9, day=17),
                          bh.details.get('date of drilling').values)
        self.assertEquals('natural ground surface',
                          bh.details.get('start point').values)
        self.assertEquals('vertical',
                          bh.details.get('inclination type').values)
        self.assertEquals([-28.4139, 121.142, -28.4139, 121.142],
                          bh.details.get('shape').values)
        self.assertEquals({'lower corner': 106.0 * self.siss.unit_reg.meter,
                           'upper corner': 249.0 * self.siss.unit_reg.meter},
                          bh.details.get('cored interval').values)
        self.assertEquals(1 * self.siss.unit_reg.meter,
                          bh.details.get('cored interval').property_type.units)
