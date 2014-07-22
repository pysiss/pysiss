""" file:   borehole_generator.py (pyboreholes)
    author: David Benn
            CSIRO IM&T Scientific Computing Data Processing Services
    date:   18 February 2014

    description: Borehole object creation from SISS GeoSciML metadata.
"""

import re
import xml.etree.ElementTree
from datetime import datetime
from pint import UnitRegistry

from ..properties import PropertyType
from ..borehole import Borehole, OriginPosition

# General namespace URIs for GeoSciML
NS = {'gsml': 'urn:cgi:xmlns:CGI:GeoSciML:2.0',
      'gsmlbh': 'http://xmlns.geosciml.org/Borehole/3.0',
      'xlink': 'http://www.w3.org/1999/xlink'}

# GeoSciML version dependent 'gml' namespace URIs
GML_NS = {'gsml': 'http://www.opengis.net/gml',
          'gsmlbh': 'http://www.opengis.net/gml/3.2'}

# GeoSciML version dependent shape namespace URIs
SHAPE_NS = {'gsml': 'http://www.opengis.net/sampling/1.0',
            'gsmlbh': 'http://www.opengis.net/samplingSpatial/2.0'}
              
class SISSBoreholeGenerator:

    """ Spatial Information Services Stack borehole generator class.
        Creates borehole objects from GeoSciML input.

        The following GeoSciML namespace variations are handled:

            xmlns:gsml => urn:cgi:xmlns:CGI:GeoSciML:2.0
            xmlns:gsmlbh => http://xmlns.geosciml.org/Borehole/3.0
            
        Borehole details that are in common across GeoSciML 2.0 and 3.0
        are extracted.
    """

    def __init__(self):
        """ Construct a SISS borehole generator instance.
        """
        self.unit_reg = UnitRegistry() 

        self.geosciml_handlers = {}
        self.geosciml_handlers['gsml'] = self._add_gsml_borehole_details
        self.geosciml_handlers['gsmlbh'] = self._add_gsmlbh_borehole_details

        self.whitespace_pattern = re.compile('\s+')
        
        self.geo_tree = None
        self.borehole = None

    """
    Question: If the expectation is that only one borehole element should be 
              found, should we raise an exception if there is more than one?
              Or, should we check that the name is the same as the borehole's 
              identifier? Since the caller can currently pass whatever name 
              he/she desires, that test may fail of course.
    """
    
    def geosciml_to_borehole(self, name, geo_source):
        """ Given a GeoSciML scanned borehole URL, return a Borehole object
            initialised with origin position and borehole details. In the case
            where there is more than one Borehole element, the first will be
            returned.

            :param name: The name to assign to the Borehole object
            :type name: string
            :param geo_source: A file-like object opened from a GeoSciML
                scanned borehole URL
            :type geo_source: file-like object
            :returns: a Borehole object initialised with origin position and
                borehole details
        """
        if geo_source is not None:
            self.geo_tree = xml.etree.ElementTree.parse(geo_source)
            borehole_elts = self._get_borehole_elts(self.geo_tree)

            if len(borehole_elts) != 0:
                self.borehole = Borehole(name=name,
                            origin_position=self._location(borehole_elts[0]))
    
                self._add_borehole_details(borehole_elts[0])

        return self.borehole

    def _get_borehole_elts(self, geo_tree):
        """ Return a list of GeoSciML Borehole elements taking into account
            tag namespace variations.

            :param geo_tree: a GeoSciML element tree
            :type geo_tree: xml.etree.ElementTree
            :returns: a list of Borehole elements
        """
        boreholes = []
        for ns_prefix in ['gsml', 'gsmlbh']:
            boreholes = geo_tree.findall('.//{' + NS[ns_prefix] + '}Borehole')
            if len(boreholes) != 0:
                break

        return boreholes

    def _location(self, borehole_elt):
        """Find the GeoSciML 2.0 or 3.0 borehole position (lat/lon) and 
           elevation and return an OriginPosition instance.
           
        :param borehole_elt: A GeoSciML 2.0 or 3.0 Borehole element
        :type borehole_elt: Element
        :returns: an OriginPosition instance (or None, if not found)
        """
        origin_position = None
        for ns_prefix in ['gsml', 'gsmlbh']:
            
            latlon_xpath = './/{{{0}}}location/{{{1}}}Point/{{{2}}}pos'
            latlon = self._element_text(borehole_elt,
                                    latlon_xpath.format(NS[ns_prefix],
                                                        GML_NS[ns_prefix],
                                                        GML_NS[ns_prefix]))
            if latlon is not None:
                (lat, lon) = latlon.split(' ')
             
                elevation_xpath = './/{{{0}}}elevation[@uomLabels]'
                elevation_elt = \
                    borehole_elt.find(elevation_xpath.format(NS[ns_prefix]))
                
                if elevation_elt is not None:
                    elevation_units = \
                        self.unit_reg[elevation_elt.attrib['uomLabels']]
                else:
                    elevation_units = None
                    
                if ns_prefix == 'gsml':
                    property_type = \
                        self._gsml_location_property(borehole_elt,
                                                     elevation_units)
                else:
                    property_type = self._gsmlbh_location_property(borehole_elt)
                    
                origin_position = \
                    OriginPosition(latitude=float(lat) * self.unit_reg.degree,
                        longitude=float(lon) * self.unit_reg.degree,
                        elevation=float(elevation_elt.text) * elevation_units,
                        property_type=property_type)
                break

        return origin_position

    def _gsml_location_property(self, borehole_elt, units):
        """Return a GeoSciML 2.0 location (elevation) property object.
        
        :param borehole_elt: A GeoSciML 2.0 Borehole element
        :type borehole_elt: Element
        :param units: elevation units
        :type units: A Pint elevation unit (e.g. meters)
        :returns: a location (elevation) property (or None, if not found)
        """
        ns_prefix = 'gsml'
        property_type = None
        
        elevation_desc_xpath = './/{{{0}}}elevation[@axisLabels]'
        elevation_elt = \
            borehole_elt.find(elevation_desc_xpath.format(NS[ns_prefix]))
        if elevation_elt is not None:
            elevation_axis_desc = \
                'elevation: {0}'.format(elevation_elt.attrib['axisLabels'])
            property_type = PropertyType(name='origin position elevation',
                                         long_name='origin position elevation',
                                         description=elevation_axis_desc,
                                         units=units)
            
        return property_type
    
    def _gsmlbh_location_property(self, borehole_elt):
        """Return a GeoSciML 3.0 location (description) property object.
        
        :param borehole_elt: A GeoSciML 2.0 Borehole element
        :type borehole_elt: Element
        :returns: a location (description) property (or None, if not found)
        """
        ns_prefix = 'gsmlbh'

        description_xpath = \
            './/{{{0}}}location/{{{1}}}Point/{{{2}}}description'
            
        description_text = self._element_text(borehole_elt,
                                        description_xpath.format(NS[ns_prefix],
                                                  GML_NS[ns_prefix], 
                                                  GML_NS[ns_prefix]))
        
        description_text = 'description: {0}'.format(description_text)
        
        return PropertyType(name='origin position',
                            long_name='origin position',
                            description=description_text)
    
    def _add_borehole_details(self, borehole_elt):
        """ Add borehole details.

            This top-level method calls more specific methods to add
            borehole details.

            :param borehole_elt: A GeoSciML Borehole element
            :type borehole_elt: Element
        """
        for ns_prefix in ['gsml', 'gsmlbh']:
            details_elt = \
            borehole_elt.find('.//{{{0}}}BoreholeDetails'.format(NS[ns_prefix]))
            if details_elt is not None:
                if ns_prefix in ('gsml', 'gsmlbh'):
                    return self.geosciml_handlers[ns_prefix](borehole_elt,
                                                             details_elt)
                break

    def _add_gsml_borehole_details(self, borehole_elt, details_elt):
        """Add borehole details from a GeoSciML 2.0 Borehole or
            BoreholeDetails element.
        
        :param borehole_elt: A GeoSciML 2.0 Borehole element
        :type borehole_elt: Element
        :param details_elt: A GeoSciML 2.0 BoreholeDetails element
        :type details_elt: Element
        """
        # Driller
        driller_xpath = './/{{{0}}}driller'.format(NS['gsml'])
        driller_attrib_xpath = '{{{0}}}title'.format(NS['xlink'])
        driller = self._element_attrib(details_elt, driller_xpath, 
                                       driller_attrib_xpath)
        self.borehole.add_detail('driller', driller)

        # Drilling method
        drilling_method = \
            self._element_text(details_elt,
                               './/{{{0}}}drillingMethod'.format(NS['gsml']))
        self.borehole.add_detail('drilling method', drilling_method)
        
        # Date of drilling
        date_of_drilling = \
            self._element_text(details_elt,
                               './/{{{0}}}dateOfDrilling'.format(NS['gsml']))
        year, month, day = date_of_drilling.split('-')
        date = datetime(year=int(year), month=int(month), day=int(day))
        self.borehole.add_detail('date of drilling', date)

        # Borehole start point
        start_point = \
            self._element_text(details_elt,
                               './/{{{0}}}startPoint'.format(NS['gsml']))
        self.borehole.add_detail('start point', start_point)
        
        # Borehole inclination type
        inclination_type = \
            self._element_text(details_elt,
                               './/{{{0}}}inclinationType'.format(NS['gsml']))
        self.borehole.add_detail('inclination type', inclination_type)
        
        # Borehole shape
        # Note: This is a child of the Borehole element rather than
        #       BoreholeDetails. 
        shape_xpath = './/{{{0}}}shape/{{{1}}}LineString/{{{2}}}posList'
        shape = \
            self._element_text(borehole_elt,
                               shape_xpath.format(SHAPE_NS['gsml'],
                                                  GML_NS['gsml'], 
                                                  GML_NS['gsml']))
        shape_list = [float(x) for x in self.whitespace_pattern.split(shape)]
        self.borehole.add_detail('shape', shape_list)
        
        # Borehole cored interval
        cored_interval_xpath = \
            './/{{{0}}}coredInterval/{{{1}}}Envelope[@uomLabels]'
        cored_interval_elt = \
            details_elt.find(cored_interval_xpath.format(NS['gsml'],
                                                         GML_NS['gsml']))
        cored_interval_units = \
            self.unit_reg[cored_interval_elt.attrib['uomLabels']]
            
        cored_interval_lower_corner = \
            self._element_text(cored_interval_elt,
                               './/{{{0}}}lowerCorner'.format(GML_NS['gsml']))
        cored_interval_upper_corner = \
            self._element_text(cored_interval_elt, 
                               './/{{{0}}}upperCorner'.format(GML_NS['gsml']))
            
        lower_corner = float(cored_interval_lower_corner)*cored_interval_units
        upper_corner = float(cored_interval_upper_corner)*cored_interval_units
        envelope_dict = {'lower corner': lower_corner,
                         'upper corner': upper_corner}
        
        # Question: How useful is the property here in fact if we have units
        #           for each value?
        self.borehole.add_detail('cored interval', envelope_dict,
                            PropertyType(name='envelope',
                                         long_name='cored interval envelope',
                                         description='cored interval envelope '
                                                     'lower and upper corner',
                                         units=cored_interval_units))
                       
    def _add_gsmlbh_borehole_details(self, borehole_elt, details_elt):
        """Add borehole details from a GeoSciML 3.0 Borehole or
           BoreholeDetails element.
        
        :param borehole_elt: A GeoSciML 3.0 Borehole element
        :type borehole_elt: Element
        :param details_elt: A GeoSciML 3.0 BoreholeDetails element
        :type details_elt: Element
        """

        # Driller
        driller_xpath = './/{{{0}}}driller'.format(NS['gsmlbh'])
        driller_attrib_xpath = '{{{0}}}title'.format(NS['xlink'])
        driller = self._element_attrib(details_elt, driller_xpath, 
                                       driller_attrib_xpath)
        self.borehole.add_detail('driller', driller)

        # Drilling method
        # Note:  This is a child of the Borehole element rather than
        #        BoreholeDetails. 
        drilling_method_xpath = ('.//{{{0}}}downholeDrillingDetails'
                                 '/{{{1}}}DrillingDetails'
                                 '/{{{2}}}drillingMethod'). \
                                 format(NS['gsmlbh'], 
                                        NS['gsmlbh'], 
                                        NS['gsmlbh'])                                 
        drilling_method_attrib_xpath = '{{{0}}}title'.format(NS['xlink'])
        drilling_method = self._element_attrib(borehole_elt, 
                                               drilling_method_xpath, 
                                               drilling_method_attrib_xpath)
        self.borehole.add_detail('drilling method', drilling_method)

        # Date of drilling
        # Note: Both start and end time are available; currently extracting
        #       only start time.
        date_of_drilling_xpath = ('.//{{{0}}}dateOfDrilling/{{{1}}}TimePeriod'
                                  '/{{{2}}}begin/{{{3}}}TimeInstant'
                                  '/{{{4}}}timePosition').format(NS['gsmlbh'],
                                                        GML_NS['gsmlbh'],
                                                        GML_NS['gsmlbh'], 
                                                        GML_NS['gsmlbh'], 
                                                        GML_NS['gsmlbh'])
        date_of_drilling = self._element_text(details_elt, date_of_drilling_xpath)
        year, month, day = date_of_drilling.split('-')
        date = datetime(year=int(year), month=int(month), day=int(day))
        self.borehole.add_detail('date of drilling', date)

        # Borehole start point
        start_point_xpath = './/{{{0}}}startPoint'.format(NS['gsmlbh'])
        start_point_attrib_xpath = '{{{0}}}title'.format(NS['xlink'])
        start_point = self._element_attrib(details_elt, start_point_xpath, 
                                           start_point_attrib_xpath)
        self.borehole.add_detail('start point', start_point)

        # Borehole inclination type
        inclination_type_xpath = './/{{{0}}}inclinationType'.format(NS['gsmlbh'])
        inclination_type_attrib_xpath = '{{{0}}}title'.format(NS['xlink'])
        inclination_type = self._element_attrib(details_elt, inclination_type_xpath, 
                                                inclination_type_attrib_xpath)
        self.borehole.add_detail('inclination type', inclination_type)
        
        # Borehole shape
        # Notes: 
        # o This is a child of the Borehole element rather than BoreholeDetails.
        # o Currently chooses the first one (if more than one exists).
        shape_xpath = './/{{{0}}}shape/{{{1}}}CompositeCurve/{{{2}}}curveMember' \
                      '/{{{3}}}LineString/{{{4}}}posList'
        shape = \
            self._element_text(borehole_elt,
                               shape_xpath.format(SHAPE_NS['gsmlbh'],
                                                  GML_NS['gsmlbh'],
                                                  GML_NS['gsmlbh'], 
                                                  GML_NS['gsmlbh'],
                                                  GML_NS['gsmlbh']))
        shape_list = [float(x) for x in self.whitespace_pattern.split(shape)]
        self.borehole.add_detail('shape', shape_list)
        
        # Borehole cored interval
        # Note: No units; haven't used a PropertyType here.
        cored_interval_xpath = ('.//{{{0}}}downholeDrillingDetails'
                                 '/{{{1}}}DrillingDetails'
                                 '/{{{2}}}interval/{{{3}}}LineString'
                                 '/{{{4}}}posList'). \
                                 format(NS['gsmlbh'], 
                                        NS['gsmlbh'], 
                                        NS['gsmlbh'],
                                        GML_NS['gsmlbh'], GML_NS['gsmlbh'])
        
        cored_interval = self._element_text(borehole_elt, 
                                            cored_interval_xpath)
        cored_interval_list = self.whitespace_pattern.split(cored_interval)
        lower_corner = float(cored_interval_list[0])
        upper_corner = float(cored_interval_list[1])
        envelope_dict = {'lower corner': lower_corner,
                         'upper corner': upper_corner}
        self.borehole.add_detail('cored interval', envelope_dict)
        
    def _element_text(self, element, xpath_str):
        """Look for and return the detail corresponding to the text 
           of the child element found by the specified XPath search
           on the supplied element.
           
        :param element: An XML element
        :type element: Element
        :param xpath_str: An XPath string.
        :type xpath_str: string
        :returns: child text
        """
        result = element.find(xpath_str)
       
        if result is not None:
            text = result.text
        else:
            text = None
        
        return text

    def _element_attrib(self, element, elt_xpath_str, attr_xpath_str):
        """Look for and return the detail corresponding to the attribute 
           text of the child element found by the specified XPath search
           on the supplied element.
           
        :param element: An XML element
        :type element: Element
        :param elt_xpath_str: An XPath string to find an element.
        :type elt_xpath_str: string
        :param attr_xpath_str: An XPath string to find an attribute.
        :type attr_xpath_str: string
        :returns: attribute text
        """
        result = element.find(elt_xpath_str)
       
        if result is not None:
            text = result.attrib[attr_xpath_str]
        else:
            text = None
        
        return text
