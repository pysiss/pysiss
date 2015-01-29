""" file:   __init__.py (pysiss.metadata)
    author: Jess Robertson
            CSIRO Minerals Resources Flagship
    date:   Wednesday 27 August, 2014

    description: Functions to deal with metadata
"""

from .registry import MetadataRegistry
from .metadata import Metadata
from .vocabulary import NamespaceRegistry, unmarshal, unmarshal_all

__all__ = ['MetadataRegistry', 'Metadata', 'namespaces',
           'unmarshal', 'unmarshal_all']
