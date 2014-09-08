""" file:   collection.py (pysiss.utilities)
    author: Jess Robertson
            CSIRO Minerals Resources Flagship
    date:   25 August 2014

    description: A utility class for forming collections of objects
"""


class Collection(list):

    """ A collection of objects, accessible as a list or dictionary

        :param objects: The objects to add on initialization
        :type objects: list of object instances
    """

    def __init__(self, objects=None):
        super(Collection, self).__init__()
        self._index = {}

        # Add the list of objects if required
        if objects:
            for bh in objects:
                self.append(bh)

    def __getitem__(self, ident_or_idx):
        """ Retrieve a object from the collection

            :param ident_or_idx: Either an integer index, or a object name.
        """
        try:
            return super(Collection, self).__getitem__(ident_or_idx)
        except IndexError:
            try:
                return super(Collection, self).__getitem__(self._index[ident_or_idx])
            except KeyError:
                str = ('Unknown key or index {0} passed '
                       'to BoreholeCollection').format(ident_or_idx)
                raise IndexError(str)

    def __setitem__(self, object):
        """ Add a object to the collection
        """
        self.append(object)
        self._index[object.name] = len(self)

    def __delitem__(self, object_name):
        """ Remove a object from the collection
        """
        # Find location of object in list
        idx = self._index[object_name]

        # Move subsequent object indices up
        for obj in self[idx:]:
            self._index[obj.name] -= 1

        # Delete object
        del self._index[object_name]
        del self[idx]

    def keys(self):
        return [obj.name for obj in self]

    def values(self):
        return self

    def items(self):
        return zip(self.keys(), self.values())

    @property
    def shapes(self):
        return (obj.shape for obj in self)
