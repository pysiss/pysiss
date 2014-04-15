""" file: dataset.py (pyboreholes.datasets)
    author: Jess Robertson
            CSIRO Earth Science and Resource Engineering
    date: Sunday November 10, 2013

    description: Classes to represent data datasets etc in boreholes

    This file defines the abstract base class DataSet which acts as a parent
    or all the dataset data types; it should not be instantiated by users.
"""

from ..properties import Property


class DataSet(object):

    """ Spatial extent over which properties are defined.

        This is an abstract base class

        Some important properties are:
            properties - dict mapping property name to Property
            size - the size of all the values sequences
            name - an identifier
            subdatasets - a list of subdataset locations
            gaps - a list of gap locations
    """

    def __init__(self, name, size):
        assert size > 0, "dataset must have at least one element"
        self.properties = dict()
        self.size = size  # size of all values sequences
        self.name = name
        self.subdatasets = None
        self.gaps = None

    def add_property(self, property_type, values):
        """ Add and return a new property
        """
        assert self.size == len(values), ("values must have the same number "
                                          "of elements as the dataset")
        self.properties[property_type.name] = Property(property_type, values)
        return self.properties[property_type.name]

    def get_property_names(self):
        """ Return the properties defined over this dataset
        """
        return self.properties.keys()
