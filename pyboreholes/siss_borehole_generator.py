""" file: siss.py
    author: David Benn
            CSIRO IM&T Science Data Services 
    date: 18 February 2014

    description: Conversion of SISS GeoSciML metadata to PropertyType objects.
"""

import urllib
from xml.dom.minidom import parse

from properties import PropertyType
from borehole import Borehole, OriginPosition
                
class SISSBoreholeGenerator:
    """ Spatial Information Services Stack class: creates borehole
        property type objects given GeoSciML input.

        The following GeoSciML version/namespace variations are handled:

            xmlns:gsml => urn:cgi:xmlns:CGI:GeoSciML:2.0
            xmlns:gsmlbh => http://xmlns.geosciml.org/Borehole/3.0
    """

    def __init__(self):
        """ Construct a SISS instance.
        """
        self.ns_prefixes = ['gsml', 'gsmlbh']
        self.boreholes = []
        
    def geosciml_to_boreholes(self, geo_url):
        """ Given a GeoSciML URL, return a list of Borehole objects
            initialised with origin position and borehole details.
        
        :param geo_url: A GeoSciML URL
        :type geo_url: string
        :returns: a list of Borehole objects
        """
        if geo_url is not None:
            geo_stream = urllib.urlopen(geo_url)
            geo_dom = parse(geo_stream)
            borehole_elts = self._get_borehole_elts(geo_dom)

            for borehole_elt in borehole_elts:
                borehole_id = borehole_elt.getAttribute('gml:id')    

                borehole = Borehole(name=borehole_id, 
                                    origin_position=self._position(borehole_elt))
                
                self.boreholes.append(borehole)

                self._add_borehole_details(borehole_elt, borehole_id)
                
        return self.boreholes

    def _get_borehole_elts(self, geo_dom):
        """ Return a list of GeoSciML Borehole elements taking into account
            tag namespace variations.
        
        :param geo_dom: a GeoSciML DOM
        :type geo_dom: xml.dom.minidom.Document
        :returns: a list of Borehole elements  
        """
        boreholes = []
        for ns_prefix in self.ns_prefixes:
            boreholes = geo_dom.getElementsByTagName(ns_prefix + ':Borehole')
            if len(boreholes) != 0:
                break
            
        return boreholes

    def _position(self, borehole):
        """Find the borehole position (lat/lon) and return an 
           OriginPosition instance.
           
        :param borehole: A GeoSciML Borehole element
        :type borehole: xml.dom.minidom.Element
        :returns: an OriginPosition instance (or None, if not found)
        """
        origin_position = None
        for ns_prefix in self.ns_prefixes:
            locations = borehole.getElementsByTagName(ns_prefix + ':location')
            if len(locations) != 0:
                points = locations[0].getElementsByTagName('gml:Point')
                if len(points) != 0:
                    positions = points[0].getElementsByTagName('gml:pos')
                    if len(positions) != 0:
                        latlon_str = positions[0].childNodes[0].nodeValue
                        (lat, lon) = latlon_str.split(' ')
                        origin_position = OriginPosition(latitude=lat, longitude=lon)
                        break
                    
        return origin_position
    
    def _add_borehole_details(self, borehole_elt, borehole_id):
        """Add borehole details.
           This top-level method calls more specific methods to add
           borehole details.
           
        :param borehole_elt: A GeoSciML Borehole element
        :type borehole_elt: xml.dom.minidom.Element
        :param borehole_id: The borehole ID
        :type borehole_id: String
        """
        for ns_prefix in self.ns_prefixes:
            details = borehole_elt.getElementsByTagName(ns_prefix + \
                                                    ':BoreholeDetails')
            if len(details) != 0:
                if details[0].tagName[0:4] == 'gsml':
                    self._add_gsml_borehole_details(details[0],
                                                    borehole_id)
                else:
                    self._add_gsmlbh_borehole_details(details[0],
                                                      borehole_id)
                break

    def _add_gsml_borehole_details(self, details_elt, borehole_id):
        """Add gsml borehole details_elt.
        
        :param details_elt: A GeoSciML BoreholeDetails element
        :type details_elt: xml.dom.minidom.Element
        :param borehole_id: The borehole ID
        :type borehole_id: String
        """
        drilling_methods = details_elt.getElementsByTagName('gsml:drillingMethod')
        drilling_method_text = drilling_methods[0].childNodes[0].nodeValue
        self.boreholes[-1].add_detail('drilling method', drilling_method_text)            

    def _add_gsmlbh_borehole_details(self, details, borehole_id):
        """Add gsmlbh borehole details.
        
        :param details: A GeoSciML BoreholeDetails element
        :type details: xml.dom.minidom.Element
        :param borehole_id: The borehole ID
        :type borehole_id: String
        """
        # TODO
        pass
