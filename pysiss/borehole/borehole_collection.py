""" file:   borehole_collection.py (pysiss.borehole)
    author: Jess Robertson
            CSIRO Earth Science and Resource Engineering
    date:   September 10, 2013

    description: BoreholeCollection class implementation
"""


class BoreholeCollection(list):

    """ A collection of boreholes, accessible as a list or dictionary

        :param boreholes: The boreholes to add on initialization
        :type boreholes: list of `pysiss.borehole.Borehole` instances
    """

    def __init__(self, boreholes=None):
        super(BoreholeCollection, self).__init__()
        self._index = {}

        # Add the list of boreholes if required
        if boreholes:
            for bh in boreholes:
                self.append(bh)

    def __getitem__(self, ident_or_idx):
        """ Retrieve a borehole from the collection

            :param ident_or_idx: Either an integer index, or a borehole name.
        """
        try:
            return self[ident_or_idx]
        except IndexError:
            try:
                return self[self._index[ident_or_idx]]
            except KeyError:
                str = ('Unknown key or index {0} passed '
                       'to BoreholeCollection').format(ident_or_idx)
                raise IndexError(str)

    def __setitem__(self, borehole):
        """ Add a borehole to the collection
        """
        self.append(borehole)
        self._index[borehole.name] = len(self)

    def __delitem__(self, borehole_name):
        """ Remove a borehole from the collection
        """
        # Find location of borehole in list
        idx = self._index[borehole_name]

        # Move subsequent borehole indices up
        for bh in self[idx:]:
            self._index[bh.name] -= 1

        # Delete borehole
        del self._index[borehole_name]
        del self[idx]

    def keys(self):
        return [bh.name for bh in self]

    def values(self):
        return self

    def items(self):
        return zip(self.keys(), self.values())
