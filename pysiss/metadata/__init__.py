""" file:   __init__.py (pysiss.metadata)
    author: Jess Robertson
            CSIRO Minerals Resources Flagship
    date:   Wednesday 27 August, 2014

    description: Functions to deal with metadata
"""

from .registry import MetadataRegistry
from .metadata import Metadata
from .namespaces import Namespace
from .vocabulary import unmarshal, unmarshal_all
from .regularize import regularize

__all__ = ['MetadataRegistry', 'Metadata', 'Namespace',
           'unmarshal', 'unmarshal_all']
