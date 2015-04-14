""" file:   collection.py (pysiss.utilities)
    author: Jess Robertson
            CSIRO Minerals Resources Flagship
    date:   25 August 2014

    description: A utility class for forming collections of things
"""

from __future__ import print_function, division


class collection(list):

    """ A collection of things, accessible as a list or dictionary

        :param things: The things to add on initialization
        :type things: list of thing instances
    """

    def __init__(self, things=None):
        super(collection, self).__init__()
        self._index = {}

        # Add the list of things if required
        if things:
            for obj in things:
                self.append(obj)

    def __getitem__(self, ident_or_idx):
        """ Retrieve a thing from the collection

            :param ident_or_idx: Either an integer index, or a thing name.
        """
        # Try to use as an index first
        try:
            return super(collection, self).__getitem__(ident_or_idx)
        except IndexError:
            pass
        except TypeError:
            pass

        # If we're here, then it's not an index
        try:
            return super(collection, self).__getitem__(
                self._index[ident_or_idx])
        except KeyError:
            string = ('Unknown key or index {0} passed '
                      'to BoreholeCollection').format(ident_or_idx)
            raise IndexError(string)

    def __setitem__(self, index, thing):
        """ collection does not support __setitem__, use append instead
        """
        raise NotImplementedError(
            "collection does not support __setitem__, use append instead")

    def __delitem__(self, ident_or_idx):
        """ Remove a thing from the collection
        """
        # Assume it's an ident first
        try:
            # Find location of thing in list
            idx = self._index[ident_or_idx]
            ident = ident_or_idx
        except KeyError:
            # OK, we've got an index
            idx = ident_or_idx
            ident = self[idx].ident

        # Move subsequent thing indices up
        for obj in self[idx:]:
            self._index[obj.ident] -= 1

        # Delete thing
        del self._index[ident]
        del self[idx]

    def append(self, thing):
        """ Add a thing to the collection
        """
        super(collection, self).append(thing)
        self._index[thing.ident] = len(self)

    def keys(self):
        """ Return the keys of the collection
        """
        return [obj.ident for obj in self]

    def values(self):
        """ Return the values of the collection
        """
        return self

    def items(self):
        """ Return the key/value pairs of the collection
        """
        return zip(self.keys(), self.values())
