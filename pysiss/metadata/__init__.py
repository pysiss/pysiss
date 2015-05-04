""" file:   __init__.py (pysiss.metadata)
    author: Jess Robertson
            CSIRO Minerals Resources Flagship
    date:   Wednesday 27 August, 2014

    description: Functions to deal with metadata
"""

from .registry import MetadataRegistry
from .metadata import Metadata, yamlify, xml_to_metadata
from .namespaces import NamespaceMap
from .vocabulary import unmarshal, unmarshal_all
from .metadata_object import ObjectWithMetadata, PYSISS_NAMESPACE

__all__ = ['MetadataRegistry', 'Metadata', 'NamespaceMap',
           'unmarshal', 'unmarshal_all', 'yamlify', 'PYSISS_NAMESPACE',
           'ObjectWithMetadata', 'xml_to_metadata']
