""" file:   unmarshallers.py (pysiss.vocabulary.gml)
    author: Jess Robertson
            CSIRO Mineral Resources Flagship
    date:   Monday 25 August, 2014

    description: Unmarshalling functions for GeoSciML/GML objects
"""

from ..namespaces import NamespaceRegistry

NAMESPACES = NamespaceRegistry()


UNMARSHALLERS = {}

__all__ = (UNMARSHALLERS,)
