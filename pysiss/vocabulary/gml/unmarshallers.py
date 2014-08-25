""" file:   unmarshallers.py (pysiss.vocabulary.gml)
    author: Jess Robertson
            CSIRO Mineral Resources Flagship
    date:   Monday 25 August, 2014

    description: Unmarshalling functions for GeoSciML/GML objects
"""

import shapely
from ..utilities import xml_namespaces

NAMESPACES = xml_namespaces.NamespaceRegistry()


def position(elem):
    """ Unmarshall a gml:posList, gml:pos or gml:coordinates element
    """
    if elem.text:
        token_pairs = elem.text.split('\n')[1:-1]
        return [map(float, p.split()) for p in token_pairs]
    else:
        return None


def polygon(elem):
    """ Unmarshall a gml:Polygon element
    """
    # Get the projection
    projection = elem.xpath('./gml:Polygon/@srsName',
                            namespaces=NAMESPACES)[0]

    # Get outer boundary first, we always have this
    outer = position(
        elem.xpath('.//gml:outerBoundaryIs//gml:posList',
                   namespaces=NAMESPACES)[0])

    # We may have 0, 1 or more inner boundaries
    inners = elem.xpath('.//gml:innerBoundaryIs//gml:posList',
                        namespaces=NAMESPACES)
    if not inners:
        inners = None
    else:
        inners = map(position, inners)

    return {'projection': projection,
            'shape': shapely.Polygon(outer, inners)}


def linestring(elem):
    """ Unmarshall a gml:LineString element
    """
    # Get the projection
    projection = elem.xpath('./gml:Polygon/@srsName',
                            namespaces=NAMESPACES)[0]

    # Get the LineString text
    string = position(
        elem.xpath('.//gml:LineString/gml:posList',
                   namespaces=NAMESPACES))

    return {'projection': projection,
            'shape': shapely.LineString(string)}


def description(elem):
    """ Unmarshall a gml:description element
    """
    return elem.text


UNMARSHALLERS = {
    'gml:posList': position,
    'gml:pos': position,
    'gml:coordinates': position,
    'gml:Polygon': polygon,
    'gml:LineString': linestring,
    'gml:description': description,
}

__all__ = (position, polygon, linestring, UNMARSHALLERS)
