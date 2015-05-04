""" file: dataset.py (pysiss.borehole.datasets)
    author: Jess Robertson
            CSIRO Earth Science and Resource Engineering
    date: Sunday November 10, 2013

    description: Classes to represent data datasets etc in boreholes

    This file defines the abstract base class Dataset which acts as a parent
    or all the dataset data types; it should not be instantiated by users.
"""

from __future__ import division, print_function

from ..properties import Property
from ...metadata import Metadata, ObjectWithMetadata, PYSISS_NAMESPACE

import pandas


class Dataset(ObjectWithMetadata):

    """ Spatial extent over which properties are defined.

        This is an abstract base class

        :param ident: an identifier for the dataset
        :type ident: string
        :param index: an index for the Dataset
        :type index: an iterator
        :param details: Metadata for a given dataset.
        :type details: pysiss.borehole.datasets.DatasetDetails
    """

    __metadata_tag__ = 'boreholeDataset'

    def __init__(self, ident, index, metadata=None):
        super(Dataset, self).__init__(ident=ident)

        # Add metadata
        if metadata:
            self.metadata.extend(metadata)
        self.metadata.append(tag=(PYSISS_NAMESPACE + 'boreholeProperties'))

        # Set up dataframe
        self._dataframe = pandas.DataFrame(index=index)

    def __getitem__(self, key):
        """ Return the data associated with the current key
        """
        return self._dataframe[key]

    def __additem__(self, ident, values):
        """ Add a new property to the Dataset

            To add metadata with a property, add it using the
            add_property method.
        """
        self.add_property(ident, values, metadata=None)

    def __delitem__(self, ident):
        """ Remove a property from the Dataset
        """
        super(self, Dataset).__delitem__(ident)
        del self.property_metadata[ident]

    def add_property(self, ident, values, **attributes):
        """ Add and return a new property
        """
        self._dataframe[ident] = values
        self.metadata['pysiss:boreholeProperties'].append(
            tag=(PYSISS_NAMESPACE + 'boreholeProperty'),
            ident=ident,
            **attributes)

    @property
    def idents(self):
        """ Return the properties defined over this dataset
        """
        return list(self.keys())

    @property
    def data(self):
        return self._dataframe

    @property
    def index(self):
        return self._dataframe.index
