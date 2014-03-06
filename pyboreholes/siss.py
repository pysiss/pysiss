#!/usr/bin/env python
""" file: siss.py
    author: David Benn
            CSIRO IM&T Science Data Services 
    date: 18 February 2014

    description: Conversion of SISS GeoSciML metadata to PropertyType objects.
"""

import urllib
from xml.dom.minidom import parse

from properties import PropertyType

# Questions:
# - Is my use of name, long_name in PropertyType useful/OK?
# - Return a dictionary of BH IDs to PropertyType instances
#   or consider making PropertyType a Composite object?
# - Don't create a property for ID since we return a dictionary keyed on ID?
# - Propagate exceptions?
                
class SISS:
    """ Spatial Information Services Stack class: creates pyboreholes
        property type objects given GeoSciML input.

        The following GeoSciML version/namespace variations are handled:

            xmlns:gsml => urn:cgi:xmlns:CGI:GeoSciML:2.0
            xmlns:gsmlbh => http://xmlns.geosciml.org/Borehole/3.0
    """

    def __init__(self):
        """ Construct a SISS instance.
        """
        self.ns_prefixes = ['gsml', 'gsmlbh']
        self.prop_types = {}
        
    def geosciml_to_prop_types(self, geo_url):
        """ Given a GeoSciML URL, return a list of property type objects.
        :param geo_url: A GeoSciML URL
        :type geo_url: string
        :returns: a dictionary of borehole IDs => list of PropertyType objects
        """
        if geo_url is not None:
            geo_stream = urllib.urlopen(geo_url)
            geo_dom = parse(geo_stream)
            boreholes = self._get_borehole_elts(geo_dom)

            for borehole in boreholes:
                # Borehole ID
                borehole_id = borehole.getAttribute('gml:id')    
                self.prop_types[borehole_id] = []
                self._add_borehole_id(borehole, borehole_id)

                # Borehole location (lat, lon)
                self._add_borehole_location(borehole, borehole_id)

                # Borehole details (driller, date and method of drilling, ...)
                self._add_borehole_details(borehole, borehole_id)
            
        return self.prop_types

    def _get_borehole_elts(self, geo_dom):
        """ Return a list of Borehole elements taking into account
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

    def _add_borehole_id(self, borehole, borehole_id):
        """Add the borehole location (lat/lon).
        :param borehole: A GeoSciML Borehole element
        :type borehole: xml.dom.minidom.Element
        :param borehole_id: The borehole ID
        :type borehole_id: String
        """
        id_prop_type = PropertyType(name=borehole_id,
                                    long_name='Borehole ID: %s' % borehole_id,
                                    description='gml:id',
                                    isnumeric=False)
        
        self.prop_types[borehole_id].append(id_prop_type)

    def _add_borehole_location(self, borehole, borehole_id):
        """Add the borehole location (lat/lon).
        :param borehole: A GeoSciML Borehole element
        :type borehole: xml.dom.minidom.Element
        :param borehole_id: The borehole ID
        :type borehole_id: String
        """
        for ns_prefix in self.ns_prefixes:
            locations = borehole.getElementsByTagName(ns_prefix + ':location')
            if len(locations) != 0:
                points = locations[0].getElementsByTagName('gml:Point')
                if len(points) != 0:
                    positions = points[0].getElementsByTagName('gml:pos')
                    if len(positions) != 0:
                        latlon_str = positions[0].childNodes[0].nodeValue
                        (lat, lon) = latlon_str.split(' ')
                        lat_prop = PropertyType(name='%s degs lat' % lat,
                                                long_name= \
                                                '%s degrees latitude' % lat,
                                                description=\
                                                'borehole latitude',
                                                units='degrees',
                                                isnumeric=True)
                        self.prop_types[borehole_id].append(lat_prop)
                        lon_prop = PropertyType(name='%s degs lon' % lon,
                                                long_name=\
                                                '%s degrees longitude' % lon,
                                                description=\
                                                'borehole longitude',
                                                units='degrees',
                                                isnumeric=True)
                        self.prop_types[borehole_id].append(lon_prop)
                        break

    def _add_borehole_details(self, borehole, borehole_id):
        """Add borehole details.
        :param borehole: A GeoSciML Borehole element
        :type borehole: xml.dom.minidom.Element
        :param borehole_id: The borehole ID
        :type borehole_id: String
        """
        for ns_prefix in self.ns_prefixes:
            details = borehole.getElementsByTagName(ns_prefix + \
                                                    ':BoreholeDetails')
            if len(details) != 0:
                if details[0].tagName[0:5] == 'gsml':
                    self._add_gsml_borehole_details(details[0],
                                                    borehole_id)
                else:
                    self._add_gsmlbh_borehole_details(details[0],
                                                      borehole_id)
                break

    def _add_gsml_borehole_details(self, details, borehole_id):
        """Add gsml borehole details.
        :param details: A GeoSciML BoreholeDetails element
        :type details: xml.dom.minidom.Element
        :param borehole_id: The borehole ID
        :type borehole_id: String
        """
        drilling_method = details.getElementsByTagName('gsml:drillingMethod')
        drilling_method_text = details.childNodes[0].nodeValue
        drilling_method_prop = PropertyType(name=drilling_method_text,
                                            long_name=\
                                            'drilling method: ' % \
                                            drilling_method_text,
                                            description=\
                                            'drilling method',
                                            isnumeric=False)
        self.prop_types[borehole_id].append(drilling_method_prop)            

    def _add_gsmlbh_borehole_details(self, details, borehole_id):
        """Add gsmlbh borehole details.
        :param details: A GeoSciML BoreholeDetails element
        :type details: xml.dom.minidom.Element
        :param borehole_id: The borehole ID
        :type borehole_id: String
        """
        pass
