""" file: ObjectWithMetadata.py (pysiss)
    author: Jess Robertson
            CSIRO Earth Science and Resource Engineering
    email:  jesse.robertson@csiro.au
    date:   Wednesday May 1, 2013

    description: Some basic metaclasses etc for defining pysiss classes
"""

from __future__ import print_function, division

import uuid

from .metadata import Metadata
from .pysiss_namespace import PYSISS_NAMESPACE

class ObjectWithMetadata(object):

    """ A mixin class to store metadata about an object

        This metaclass generates a UUID for a class at initialization,
        and defines the class __eq__ method to use this UUID.

        This metaclass generates a metadata record for a class at
        initialization, and defines a set of methods for serializing and
        deserializing that metadata
    """

    def __init__(self, ident=None, *args, **kwargs):
        # Pass through initialization to object
        super(ObjectWithMetadata, self).__init__()
        self.ident = ident

        # Generate a new identity if required, & construct metadata attributes
        if hasattr(self, '__metadata_tag__'):
            self.uuid = uuid.uuid5(uuid.NAMESPACE_DNS,
                                   PYSISS_NAMESPACE + self.__metadata_tag__)
            self.ident = self.ident or str(self.uuid)
            self.metadata = Metadata(tag=(PYSISS_NAMESPACE +
                                          self.__metadata_tag__),
                                     ident=self.ident)

        else:
            self.ident = self.uuid = uuid.uuid4()
            self.ident = self.ident or str(self.uuid)
            self.metadata = Metadata(tag=(PYSISS_NAMESPACE + ':' + 'unknown'),
                                     ident=self.ident)

    def __eq__(self, other):
        """ Equality test

            Class instances are equal if their UUIDs match
        """
        return self.uuid == other.uuid

