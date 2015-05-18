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
class Dataset(pandas.DataFrame):

    """ Spatial extent over which properties are defined.

        This is an abstract base class

        :param index: an index for the Dataset
        :type index: an iterator
        :param ident: an identifier for the dataset
        :type ident: string
    """

    def __init__(self, ident=None):
        super(Dataset, self).__init__()
        self.ident = ident

    def __getitem__(self, key):
        """ Return the data associated with the current key
        """
        return self.data[key]

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
        del self.metadata[ident]

    def add_property(self, property_id, values, **attributes):
        """ Add a new property with attributes

            Parameters;
                ident - an identifier for the dataset.
                values - the values for the dataset. Must be broadcastable to
                    the same length as the dataset or a ValueError is raised.
                    If a scalar value, all values are set to be the same
        """
        import ipdb; ipdb.set_trace()
        super(self, __setitem__)(ident, values)
        if attributes:
            self.add_attributes(ident=ident, **attributes)

    def add_attributes(self, ident, **attributes):
        """ Add the given attributes to the property
        """
        mdata = self.metadata['pysiss:datasetProperties']
        for attr, value in attributes.items():
            mdata.add_subelement(
                tag=(PYSISS_NAMESPACE + 'property'),
                ident=property_id,
                **attributes)

    def get_attributes(self, property_id):
        """ Return the property attributes associated with the given property

            Parameters:
                ident - the identifier for the property

            Returns:
                a dictionary of attributes
        """
        mdata = self.metadata.xpath('//pysiss:property[@ident={0}]'.format(k),
                                    unwrap=True)
        if mdata:
            return (mdata.attrib or {})
        else:
            return {}

    def get_property(self, property_id):
        """ Return the values and metadata associated with the given property
        """
        return self[property_id], self.get_attributes(property_id)

    @property
    def idents(self):
        """ Return the properties defined over this dataset
        """
        return list(self.keys())

