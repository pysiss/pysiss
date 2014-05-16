""" file:   borehole.py (pyboreholes)
    author: Jess Robertson & Ben Caradoc-Davies
            CSIRO Earth Science and Resource Engineering
    date:   September 10, 2013

    description: BoreholeDetails class implementation
"""

from collections import namedtuple

BoreholeDetail = namedtuple('BoreholeDetail', 'name values property_type')


class BoreholeDetails(dict):

    """ Class to store details about drilling a borehole
    """

    def __init__(self):
        super(BoreholeDetails, self).__init__()

    def add_detail(self, name, values, property_type=None):
        """ Add a detail to the class

            :param name: An identifier for the detail
            :type name: string
            :param values: The data to add
            :type values: any Python object
            :param property_type: The property type of the detail, optional,
                defaults to None
            :type property_type: `pyboreholes.PropertyType`
        """
        self[name] = BoreholeDetail(name=name,
                                    values=values,
                                    property_type=property_type)

    def __setattr__(self):
        """ Disable setattr method
        """
        raise NotImplementedError('Use add_detail to add details')
