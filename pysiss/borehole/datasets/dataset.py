""" file: dataset.py (pysiss.borehole.datasets)
    author: Jess Robertson
            CSIRO Earth Science and Resource Engineering
    date: Sunday November 10, 2013

    description: Classes to represent data datasets etc in boreholes

    This file defines the abstract base class DataSet which acts as a parent
    or all the dataset data types; it should not be instantiated by users.
"""

from __future__ import division, print_function

from ..properties import Property
from ...utilities import id_object

import pandas


class DataSet(id_object):

    """ Spatial extent over which properties are defined.

        This is an abstract base class

        :param ident: an identifier for the dataset
        :type ident: string
        :param index: an index for the DataSet
        :type index: an iterator
        :param details: Metadata for a given dataset.
        :type details: pysiss.borehole.datasets.DatasetDetails
    """

    def __init__(self, ident, index, metadata=None):
        super(DataSet, self).__init__(ident=ident)
        self._dataframe = pandas.DataFrame(index=index)
        self.metadata = metadata
        self.property_metadata = {}
        self.ident = ident

    def __additem__(self, ident, values):
        """ Add a new property to the DataSet

            To add metadata with a property, add it using the
            add_property method.
        """
        self.add_property(ident, values, metadata=None)

    def __delitem__(self, ident):
        """ Remove a property from the DataSet
        """
        super(self, DataSet).__delitem__(ident)
        del self.property_metadata[ident]

    def add_property(self, ident, values, metadata=None):
        """ Add and return a new property
        """
        self[ident] = values
        self.property_metadata[ident] = metadata

    @property
    def idents(self):
        """ Return the properties defined over this dataset
        """
        return list(self.keys())

    @property
    def dataframe(self):
        return self._dataframe

    @property
    def index(self):
        return self._dataframe.index
