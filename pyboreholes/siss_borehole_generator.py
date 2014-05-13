""" file:   siss_borehole_generator.py (pyboreholes)
    author: David Benn
            CSIRO IM&T Science Data Services
    date:   18 February 2014

    description: Borehole object creation from SISS GeoSciML metadata.
"""

#from xml.dom.minidom import parse
import xml.etree.ElementTree

# from properties import PropertyType
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
        self.geo_ns_dict = {'gsml': 'urn:cgi:xmlns:CGI:GeoSciML:2.0',
                            'gsmlbh': 'http://xmlns.geosciml.org/Borehole/3.0'}
        self.gml_ns = 'http://www.opengis.net/gml'
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
                                origin_position=self._position(borehole_elt))

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
        for ns_prefix in self.geo_ns_dict:
            geo_ns = self.geo_ns_dict[ns_prefix]
            boreholes = geo_tree.findall('.//{' + geo_ns + '}Borehole')
            if len(boreholes) != 0:
                break

        return boreholes

    def _position(self, borehole_elt):
        """ Find the borehole position (lat/lon) and return an
            OriginPosition instance.

            :param borehole_elt: A GeoSciML Borehole element
            :type borehole_elt: Element
            :returns: an OriginPosition instance (or None, if not found)
        """
        origin_position = None
        for ns_prefix in self.geo_ns_dict:
            geo_ns = self.geo_ns_dict[ns_prefix]
            position = borehole_elt.find(
                './/{%s}location/{%s}Point/{%s}pos' %
                (geo_ns, self.gml_ns, self.gml_ns))
            if position is not None:
                latlon_str = position.text
                (lat, lon) = latlon_str.split(' ')
                origin_position = OriginPosition(latitude=lat, longitude=lon)
                break

        return origin_position

    def _add_borehole_details(self, borehole_elt):
        """ Add borehole details.

            This top-level method calls more specific methods to add
            borehole details.

            :param borehole_elt: A GeoSciML Borehole element
            :type borehole_elt: Element
        """
        for ns_prefix in self.geo_ns_dict:
            geo_ns = self.geo_ns_dict[ns_prefix]
            details = borehole_elt.find('.//{%s}BoreholeDetails' % geo_ns)
            # TODO: make this and callee code polymorphic wrt geo_ns
            if details is not None:
                if ns_prefix == 'gsml':
                    self._add_gsml_borehole_details(details)
                else:
                    self._add_gsmlbh_borehole_details(details)
                break

    def _add_gsml_borehole_details(self, details_elt):
        """ Add gsml borehole details_elt.

            :param details_elt: A GeoSciML BoreholeDetails element
            :type details_elt: Element
        """
        drilling_method = details_elt.find(
            './/{%s}drillingMethod' % self.geo_ns_dict['gsml'])
        drilling_method_text = drilling_method.text
        self.boreholes[-1].add_detail('drilling method', drilling_method_text)

    def _add_gsmlbh_borehole_details(self, details_elt):
        """ Add gsmlbh borehole details.

            :param details_elt: A GeoSciML BoreholeDetails element
            :type details_elt: Element
        """
        # TODO
        pass
