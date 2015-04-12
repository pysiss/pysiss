""" file: property_type.py (pysiss.borehole.properties)
    author: Jess Robertson
            CSIRO Earth Science and Resource Engineering
    date: Sunday November 10, 2013

    description: Imports for pysiss.borehole.properties
"""

from __future__ import division, print_function

class PropertyType(object):

    """ The metadata for a property.

        :param ident: Property ident
        :type ident: string
        :param long_name: Name for presentation to the user
        :type long: atring or `None`
        :param description: Descriptive phrase
        :type description: string
        :param units: Unit in Unified Code for Units of Measure (UCUM)
        :type units: string or None
        :param isnumeric: Whether the property is numeric or categorical
        :type isnumeric: bool
    """

    def __init__(self, ident, long_name=None, description=None, units=None,
                 isnumeric=True, detection_limit=None):
        self.ident = ident
        self._long_name = long_name
        self.description = description
        self.units = units
        self.isnumeric = isnumeric
        self.detection_limit = detection_limit

    def __repr__(self):
        info = 'PropertyType {0}: long name is "{1}", units are {2}'
        return info.format(self.ident, self.long_name, self.units)

    @property
    def long_name(self):
        """ Return long name or ident if no long name.
        """
        return self._long_name if self._long_name is not None else self.ident

    def copy(self):
        """ Return a copy of the PropertyType instance
        """
        return PropertyType(self.ident, self.long_name, self.description,
                            self.units)
