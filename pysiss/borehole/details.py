""" file:   details.py (pysiss.borehole)
    author: Jess Robertson & Ben Caradoc-Davies
            CSIRO Earth Science and Resource Engineering
    date:   September 10, 2013

    description: Details class implementation
"""

from __future__ import division, print_function

from collections import namedtuple


def detail_type(ident, detail_attr=None):
    """ Return a detail type for use in a Details class

        This is essentially a wrapper around `collections.namedtuple`,
        for more details on the formatting of the detail_attr, see the
        Python documentation.

        :param ident: The identifier of the new detail type
        :type ident: string
        :param detail_attr: The attributes of the new detail type
        :type detail_attr: string
    """
    if detail_attr is None:
        detail_attr = 'ident values property_type'
    return namedtuple(ident, detail_attr)


class Details(dict):

    """ Class to store details about another class
    """

    detail_type = detail_type('details')

    def __init__(self):
        super(Details, self).__init__()

    def add_detail(self, ident, values, property_type=None):
        """ Add a detail to the class

            :param ident: An identifier for the detail
            :type ident: string
            :param values: The data to add
            :type values: any Python object
            :param property_type: The property type of the detail, optional,
                defaults to None
            :type property_type: `pysiss.borehole.PropertyType`
        """
        self[ident] = self.detail_type(ident=ident,
                                       values=values,
                                       property_type=property_type)
