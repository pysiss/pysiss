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
from ...metadata import with_metadata, PYSISS_NAMESPACE

import pandas


@with_metadata(tag='boreholeDataset',
               subelements=[{'tag': PYSISS_NAMESPACE + 'datasetProperties'}])
class Dataset(object):

    """ Spatial extent over which properties are defined.

        This is an abstract base class

        :param index: an index for the Dataset
        :type index: an iterator
        :param ident: an identifier for the dataset
        :type ident: string
    """

    def __init__(self, index, ident=None):
        super(Dataset, self).__init__()
        self.ident = ident

        # Set up dataframe
        self._index = index
        self._dataframe = pandas.DataFrame(index=index)
        self.keys = self._dataframe.keys

    def __getitem__(self, key):
        """ Return the data associated with the current key
        """
        return self._dataframe[key]

    def __setitem__(self, ident, values):
        """ Add a new property to the Dataset

            To add metadata with a property, add it using the
            add_property method.
        """
        self.add_property(ident, values)

    def __delitem__(self, ident):
        """ Remove a property from the Dataset
        """
        super(self, Dataset).__delitem__(ident)
        del self.property_metadata[ident]

    def add_property(self, ident, values, **attributes):
        """ Add a new property
        """
        self._dataframe[ident] = values
        self.metadata['pysiss:datasetProperties'].add_subelement(
            tag=(PYSISS_NAMESPACE + 'property'),
            ident=ident,
            **attributes)

    @property
    def idents(self):
        """ Return the properties defined over this dataset
        """
        return list(self.keys())

    @property
    def data(self):
        """ Return the dataframe for the dataset
        """
        return self._dataframe

    @property
    def index(self):
        """ Return the index for the dataset
        """
        return self._dataframe.index

    def items(self):
        """ Return an iterator over the properties defined in the dataset

            Each item is a tuple containing a key, a Pandas.series with the values
            and the property attributes.
        """
        for k in self.keys():
            values = self[k]
            mdata = self.metadata.xpath('//pysiss:property[@ident={0}]'.format(k),
                                        unwrap=True)
            if mdata is not None:
                yield(k, values, mdata.attrib)
            else:
                yield(k, values, {})

    def values(self):
        """ Return an iterator over the property values defined in the dataset
        """
        return (self[k] for k in self.keys())

