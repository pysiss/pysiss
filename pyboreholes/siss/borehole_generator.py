""" file:   siss_borehole_generator.py (pyboreholes)
    author: David Benn
            CSIRO IM&T Scientific Computing Data Processing Services
    date:   18 February 2014

    description: Borehole object creation from SISS GeoSciML metadata.
"""

import xml.etree.ElementTree
from datetime import datetime
from ..properties import PropertyType
from ..borehole import Borehole, OriginPosition

NS_DICT = {'gml': 'http://www.opengis.net/gml',
           'gsml': 'urn:cgi:xmlns:CGI:GeoSciML:2.0',
           'gsmlbh': 'http://xmlns.geosciml.org/Borehole/3.0',
           'sa': 'http://www.opengis.net/sampling/1.0',
           'xlink': 'http://www.w3.org/1999/xlink'}
              
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
        self.boreholes = []

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
            geo_tree = xml.etree.ElementTree.parse(geo_source)
            borehole_elt = self._get_borehole_elts(geo_tree)[0]

            borehole = Borehole(name=name,
                                origin_position=self._location(borehole_elt))
            self.boreholes.append(borehole)

            self._add_borehole_details(borehole_elt)

        return self.boreholes[0]

    def _get_borehole_elts(self, geo_tree):
        """ Return a list of GeoSciML Borehole elements taking into account
            tag namespace variations.

            :param geo_tree: a GeoSciML element tree
            :type geo_tree: xml.etree.ElementTree
            :returns: a list of Borehole elements
        """
        boreholes = []
        for ns_prefix in NS_DICT:
            boreholes = geo_tree.findall('.//{' + NS_DICT[ns_prefix] + '}Borehole')
            if len(boreholes) != 0:
                break

        return boreholes

    def _location(self, borehole_elt):
        """Find the borehole position (lat/lon) and elevation and return an 
           OriginPosition instance.
           
        :param borehole_elt: A GeoSciML 2.0 or 3.0 Borehole element
        :type borehole_elt: Element
        :returns: an OriginPosition instance (or None, if not found)
        """
        origin_position = None
        for ns_prefix in NS_DICT:
            latlon_xpath = './/{{{0}}}location/{{{1}}}Point/{{{2}}}pos'
            latlon = self._element_text(borehole_elt,
                                        latlon_xpath.format(NS_DICT[ns_prefix],
                                                            NS_DICT['gml'], NS_DICT['gml']))
            if latlon is not None:
                (lat, lon) = latlon.split(' ')
             
                elevation_xpath = './/{{{0}}}elevation[@uomLabels]'
                elevation_elt = borehole_elt.find(elevation_xpath.format(NS_DICT[ns_prefix]))
            
                if elevation_elt is not None:
                    elevation = float(elevation_elt.text)
                    elevation_units = elevation_elt.attrib['uomLabels']
                    # TODO: add units to elevation
                    origin_position = OriginPosition(latitude=float(lat),
                                                     longitude=float(lon),
                                                     elevation=elevation)
                    break
        return origin_position

    def _add_borehole_details(self, borehole_elt):
        """ Add borehole details.

            This top-level method calls more specific methods to add
            borehole details.

            :param borehole_elt: A GeoSciML Borehole element
            :type borehole_elt: Element
        """
        for ns_prefix in NS_DICT:
            details_elt = borehole_elt.find('.//{{{0}}}BoreholeDetails'.format(NS_DICT[ns_prefix]))
            # TODO: add another dict that maps ns_prefix to XPath string, avoiding conditional below;
            #       this will only work given enough symmetry between GeoSciML 2.0 and 3.0 
            if details_elt is not None:
                if ns_prefix == 'gsml':
                    self._add_gsml_borehole_details(borehole_elt, details_elt)
                else:
                    self._add_gsmlbh_borehole_details(borehole_elt, details_elt)
                break

    def _add_gsml_borehole_details(self, borehole_elt, details_elt):
        """Add borehole details from a GeoSciML 2.0 Borehole or BoreholeDetails element.
        
        :param borehole_elt: A GeoSciML 2.0 Borehole element
        :type borehole_elt: Element
        :param details_elt: A GeoSciML 2.0 BoreholeDetails element
        :type details_elt: Element
        """
        # Driller
        driller_xpath = './/{{{0}}}driller'.format(NS_DICT['gsml'])
        driller_attrib_xpath = '{{{0}}}title'.format(NS_DICT['xlink'])
        driller = self._element_attrib(details_elt, driller_xpath, driller_attrib_xpath)
        self.boreholes[-1].add_detail('driller', driller)

        # Drilling method
        drilling_method = self._element_text(details_elt,
                                            './/{{{0}}}drillingMethod'.format(NS_DICT['gsml']))
        self.boreholes[-1].add_detail('drilling method', drilling_method)
        
        # Date of drilling
        date_of_drilling = self._element_text(details_elt,
                                             './/{{{0}}}dateOfDrilling'.format(NS_DICT['gsml']))
        year, month, day = date_of_drilling.split('-')
        date = datetime(year=int(year), month=int(month), day=int(day))
        self.boreholes[-1].add_detail('date of drilling', date)

        # Borehole start point
        start_point = self._element_text(details_elt,
                                        './/{{{0}}}startPoint'.format(NS_DICT['gsml']))
        self.boreholes[-1].add_detail('start point', start_point)
        
        # Borehole inclination type
        inclination_type = self._element_text(details_elt,
                                        './/{{{0}}}inclinationType'.format(NS_DICT['gsml']))
        self.boreholes[-1].add_detail('inclination type', inclination_type)
        
        # Borehole shape
        # Note: This is a child of the Borehole element rather than BoreholeDetails.
        #       It seems reasonable to add it as a borehole detail however. 
        shape_xpath = './/{{{0}}}shape/{{{1}}}LineString/{{{2}}}posList'
        shape = self._element_text(borehole_elt,
                                  shape_xpath.format(NS_DICT['sa'],
                                                     NS_DICT['gml'], NS_DICT['gml']))
        shape_list = [float(x) for x in shape.split(' ')]
        self.boreholes[-1].add_detail('shape', shape_list)
        
        # Borehole cored interval
        cored_interval_xpath = './/{{{0}}}coredInterval/{{{1}}}Envelope[@uomLabels]'
        cored_interval_elt = details_elt.find(cored_interval_xpath.format(NS_DICT['gsml'],
                                                                          NS_DICT['gml']))
        cored_interval_units = cored_interval_elt.attrib['uomLabels']
        cored_interval_lower_corner = self._element_text(details_elt,
                                                         './/{{{0}}}lowerCorner'.format(NS_DICT['gml']))
        cored_interval_upper_corner = self._element_text(details_elt,
                                                         './/{{{0}}}upperCorner'.format(NS_DICT['gml']))
        envelope_dict = {'lower corner': float(cored_interval_lower_corner),
                         'upper corner': float(cored_interval_upper_corner)}
        self.boreholes[-1].add_detail('cored interval', envelope_dict,
                                      PropertyType(name='envelope', 
                                                   long_name='cored interval  envelope', 
                                                   description='cored interval envelope '
                                                               'lower and upper corner',
                                                   units=cored_interval_units))
                       
    def _add_gsmlbh_borehole_details(self, borehole_elt, details_elt):
        """Add borehole details from a GeoSciML 3.0 Borehole or BoreholeDetails element.
        
        :param borehole_elt: A GeoSciML 3.0 Borehole element
        :type borehole_elt: Element
        :param details_elt: A GeoSciML 3.0 BoreholeDetails element
        :type details_elt: Element
        """
        pass
    
    def _element_text(self, element, xpath_str):
        """Look for and return the detail corresponding to the child text 
           of the element found by the specified XPath search on the supplied 
           XML element.
           
        :param element: An XML element
        :type element: Element
        :param xpath_str: An XPath string.
        :type xpath_str: string
        :returns: child text
        """
        result = element.find(xpath_str)
       
        if result != None:
            text = result.text
        else:
            text = None
        
        return text

    def _element_attrib(self, element, elt_xpath_str, attr_xpath_str):
        """Look for and return the detail corresponding to the attribute text 
           of the element found by the specified XPath search on the supplied 
           XML element.
           
        :param element: An XML element
        :type element: Element
        :param elt_xpath_str: An XPath string to find an element.
        :type elt_xpath_str: string
        :param attr_xpath_str: An XPath string to find an attribute.
        :type attr_xpath_str: string
        :returns: attribute text
        """
        result = element.find(elt_xpath_str)
       
        if result != None:
            text = result.attrib[attr_xpath_str]
        else:
            text = None
        
        return text
