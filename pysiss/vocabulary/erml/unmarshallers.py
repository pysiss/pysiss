""" file:   unmarshallers.py (pysiss.vocabulary.gml)
    author: Jess Robertson
            CSIRO Mineral Resources Flagship
    date:   Monday 25 August, 2014

    description: Unmarshalling functions for GeoSciML/GML objects
"""

from ..utilities import xml_namespaces

NAMESPACES = xml_namespaces.NamespaceRegistry()


UNMARSHALLERS = {}

__all__ = (UNMARSHALLERS,)
