""" file:   unmarshallers.py (pysiss.vocabulary.gml)
    author: Jess Robertson
            CSIRO Mineral Resources Flagship
    date:   Monday 25 August, 2014

    description: Unmarshalling functions for GeoSciML/GML objects
"""

from lxml import etree
import shapely

from xml_namespaces import shorten_namespace, expand_namespace, split_namespace


def gml_poslist(elem):
    """ Unmarshall a gml:posList element
    """
    pass


UNMARSHALLERS = {
    'gml:posList': gml_poslist
}

__all__ = (UNMARSHALLERS,)
