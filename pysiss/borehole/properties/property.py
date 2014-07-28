""" file: property.py (pysiss.borehole.properties)
    author: Jess Robertson
            CSIRO Earth Science and Resource Engineering
    date: Sunday November 10, 2013

    description: Imports for pysiss.borehole.properties
"""

class Property(object):

    """ Container for values with type.

        Values must match the length of the dataset: for sampling and interval
        datasets, it must be a sequence of the same length as the depths. For a
        feature is should be a single value unless it is a multivalued category

        :param property_type: The property metadata for the property
        :type property_type: pysiss.borehole.properties.property_type
        :param values: A list of values to store
        :type values: iterable
    """

    def __init__(self, property_type, values):
        self.property_type = property_type
        self.values = values

    def __repr__(self):
        info = 'Property {0}: {1} values in units of {2}'
        return info.format(self.name, len(self.values),
            self.property_type.units)

    @property
    def name(self):
        """ Returns the name of the property"
        """
        return self.property_type.name

    def copy(self):
        """ Return a copy of the Property instance
        """
        return Property(self.property_type, self.values[:])
