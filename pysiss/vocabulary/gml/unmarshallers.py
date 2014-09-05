""" file:   unmarshallers.py (pysiss.vocabulary.gml)
    author: Jess Robertson
            CSIRO Mineral Resources Flagship
    date:   Monday 25 August, 2014

    description: Unmarshalling functions for GeoSciML/GML objects
"""

from shapely.geometry import Polygon, LineString
from ..namespaces import NamespaceRegistry

NAMESPACES = NamespaceRegistry()


def position(elem):
    """ Unmarshal a gml:posList, gml:pos or gml:coordinates element
    """
    if elem.text:
        token_pairs = elem.text.split('\n')[1:-1]
        return [map(float, p.split()) for p in token_pairs]
    else:
        return None


def polygon(elem):
    """ Unmarshal a gml:Polygon element
    """
    # Get the projection
    projection = elem.xpath('.//@srsName',
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
            'shape': Polygon(outer, inners)}


def linestring(elem):
    """ Unmarshal a gml:LineString element
    """
    # Get the projection
    projection = elem.xpath('.//@srsName',
                            namespaces=NAMESPACES)[0]

    # Get the LineString text
    string = position(
        elem.xpath('./gml:posList',
                   namespaces=NAMESPACES)[0])

    return {'projection': projection,
            'shape': LineString(string)}


def description(elem):
    """ Unmarshal a gml:description element
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
