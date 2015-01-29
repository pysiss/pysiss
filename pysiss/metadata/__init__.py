""" file:   __init__.py (pysiss.metadata)
    author: Jess Robertson
            CSIRO Minerals Resources Flagship
    date:   Wednesday 27 August, 2014

    description: Functions to deal with metadata
"""

from .registry import MetadataRegistry
from .metadata import Metadata
from .namespaces import NamespaceRegistry, add_namespace, shorten_namespace, \
    expand_namespace, split_namespace

__all__ = ['MetadataRegistry', 'Metadata',
           'unmarshal', 'unmarshal_all', 'NamespaceRegistry', 'add_namespace',
           'shorten_namespace', 'expand_namespace', 'split_namespace']
