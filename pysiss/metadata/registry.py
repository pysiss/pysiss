""" file:   registry.py (pysiss.metadata)
    author: Jess Robertson
            CSIRO Minerals Resources Flagship
    date:   Wednesday 27 August, 2014

    description: Functions to deal with metadata objects

    Metadata descriptions can be shared by many different objects, so it makes
    sense to seperate these out into a seperate registry.
"""

from ..utilities import Singleton

import logging

LOGGER = logging.getLogger('pysiss')


class MetadataRegistry(dict):

    """ A registry to store metadata instances

        Since GeoSciML allows metadata reuse, we need to have a central
        repository of metadata which stores the actual etrees, and objects can
        refer to keys within this repository.
    """

    __metaclass__ = Singleton
    registered_ids = set()

    def register(self, metadata_item, replace_existing=False, verbose=False):
        """ Register a metadata item in the registry
        """
        # Check to see whether the item already exists
        if not replace_existing:
            if metadata_item.ident in self.registered_ids and verbose:
                LOGGER.warn(('Metadata ID {0} already exists, skipping'
                               ' registration').format(metadata_item.ident))
            return

        # If it doesn't already exist
        self[metadata_item.ident] = metadata_item

    def deregister(self, metadata_key):
        """ Deregister the given metadata item given by the key
        """
        del self[metadata_key]
