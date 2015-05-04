""" file: metadata_object.py (pysiss)
    author: Jess Robertson
            CSIRO Earth Science and Resource Engineering
    email:  jesse.robertson@csiro.au
    date:   Wednesday May 1, 2013

    description: Some basic metaclasses etc for defining pysiss classes
"""

from __future__ import print_function, division

import uuid

class metadata_object(id_object):

    """ A mixin class to store metadata about an object

        This metaclass generates a UUID for a class at initialization,
        and defines the class __eq__ method to use this UUID.

        This metaclass generates a metadata record for a class at
        initialization, and defines a set of methods for serializing and
        deserializing that metadata
    """

    def __init__(self, ident=None, *args, **kwargs):
        super(metadata_object, self).__init__(*args, **kwargs)
        if ident:
            self.uuid = uuid.uuid5(uuid.NAMESPACE_DNS, ident)
        else:
            self.uuid = uuid.uuid4()
            self.ident = self.uuid

        # Construct metadata attributes
        if hasattr(self, __metadata_tag__):
            self.metadata = Metadata(ident=self.ident,
                                     tag=self.__metadata_tag__)
        else:
            self.metadata = Metadata(ident=self.ident)

    def __eq__(self, other):
        """ Equality test

            Class instances are equal if their UUIDs match
        """
        return self.uuid == other.uuid
