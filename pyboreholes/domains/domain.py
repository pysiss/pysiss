#!/usr/bin/env python
""" file: domain.py
    author: Jess Robertson
            CSIRO Earth Science and Resource Engineering
    date: Sunday November 10, 2013

    description: Classes to represent data domains etc in boreholes

    This file defines the abstract base class Domain which acts as a parent
    or all the domain data types; it should not be instantiated by users.
"""

from ..properties import Property

class Domain(object):

    """Spatial extent over which properties are defined.

    This is an abstract base class

    Some important properties are:
        properties - dict mapping property name to Property
        size - the size of all the values sequences
        name - an identifier
        subdomains - a list of subdomain locations
        gaps - a list of gap locations
    """

    def __init__(self, name, size):
        assert size > 0, "domain must have at least one element"
        self.properties = dict()
        self.size = size  # size of all values sequences
        self.name = name
        self.subdomains = None
        self.gaps = None

    def add_property(self, property_type, values):
        """ Add and return a new property
        """
        assert self.size == len(values), ("values must have the same number "
            "of elements as the domain")
        self.properties[property_type.name] = Property(property_type, values)
        return self.properties[property_type.name]

    def get_property_names(self):
        """ Return the properties defined over this domain
        """
        return self.properties.keys()

