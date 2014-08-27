""" file:   registry.py (pysiss.metadata)
    author: Jess Robertson
            CSIRO Minerals Resources Flagship
    date:   Wednesday 27 August, 2014

    description: Functions to deal with metadata objects

    Metadata descriptions can be shared by many different objects, so it makes
    sense to seperate these out into a seperate registry.
"""

from ..utilities import Singleton


class MetadataRegistry(dict):

    """ A registry to store metadata instances

        Since GeoSciML allows metadata reuse, we need to have a central
        repository of metadata which stores the actual etrees, and objects can
        refer to keys within this repository.
    """

    __metaclass__ = Singleton

    def register(self, metadata_item):
        """ Register a metadata item in the registry
        """
        self[metadata_item.ident] = metadata_item

    def deregister(self, metadata_key):
        """ Deregister the given metadata item given by the key
        """
        del self[metadata_key]
