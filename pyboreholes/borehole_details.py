""" file:   borehole.py (pyboreholes)
    author: Jess Robertson & Ben Caradoc-Davies
            CSIRO Earth Science and Resource Engineering
    date:   September 10, 2013

    description: BoreholeDetails class implementation
"""

from collections import namedtuple

BoreholeDetail = namedtuple('BoreholeDetail', 'name data property_type')

class BoreholeDetails(dict):
    
    """ Class to store details about drilling a borehole
    """
    
    def __init__(self):
        super(BoreholeDetails, self).__init__()

    def add_detail(self, name, data, property_type=None):
        """ Add a detail to the class

            :param name: An identifier for the detail
            :type name: string
            :param data: The data to add
            :type data: any Python object
            :param property_type: The property type of the detail, optional, defaults to None
            :type property_type: `pyboreholes.PropertyType`
        """
        self[name] = BoreholeDetail(name=name,
                                    data=data,
                                    property_type=property_type)

    def __setattr__(self):
        """ Disable setattr method
        """ 
        raise NotImplementedError('Use add_detail to add details')