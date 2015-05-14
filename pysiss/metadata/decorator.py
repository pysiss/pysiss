""" file: decorator.py (pysiss.metadata)
    author: Jess Robertson
            CSIRO Earth Science and Resource Engineering
    email:  jesse.robertson@csiro.au
    date:   Wednesday May 1, 2013

    description: Some basic metaclasses etc for defining pysiss classes
"""

from __future__ import print_function, division

from .metadata import Metadata, PYSISS_NAMESPACE

from uuid import uuid5 as uuid
from uuid import NAMESPACE_DNS
import types


def with_metadata(tag, subelements=None):
    """ A decorator to store metadata about an object

        This decorator generates a UUID for a class at initialization,
        and defines the class __eq__ method to use this UUID.

        This decorator generates a metadata record for a class at
        initialization, and defines a set of methods for serializing and
        deserializing that metadata

        The optional subelements parameter allows classes to define an initial
        structure for their metadata tree. Subelements should be a dictionary 
        defining keyword arguments which can be passed to `Metadata.add_subelement` 

        Parameters:
            tag - the tag for the metadata tree
            subelements - a list of dictionaries, defining subelements of the
                metadata instance.
    """
    def _md_wrapper(cls):
        """ Wrapper to add metadata
        """
        # Generate a new identity if required, & construct metadata attributes
        cls.uuid = uuid(NAMESPACE_DNS, tag)
        if not hasattr(cls, 'ident') or cls.ident is None:
            cls.ident = str(cls.uuid)
        cls.metadata = Metadata(tag=PYSISS_NAMESPACE + tag,
                                ident=cls.ident)

        # Add subelements if required
        if subelements:
            for subelement in subelements:
                cls.metadata.add_subelement(**subelement)

        # Add equality test to match instances if their uuids match
        setattr(cls, '__eq__', lambda self, other: self.uuid == other.uuid)
        cls.__eq__.__doc__ = \
            """ Equality test

                Class instances are equal if their UUIDs match
            """

        return cls  
    return _md_wrapper
