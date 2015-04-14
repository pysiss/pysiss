""" file: coverageservice.py
    author: Jess Robertson
            CSIRO Minerals Resources Flagship
    date:   January 2015

    description: Class to handle WCS endpoints
"""


from collections import defaultdict


class accumulator(object):

    """ Class providing a dictionary where repeated entries to
        a key generate a list rather than overwriting
    """

    def __init__(self, *args, **kwargs):
        super(accumulator, self).__init__()
        self._dict = defaultdict(list)
        self.update(*args, **kwargs)

    def __str__(self):
        """ String representation
        """
        return 'acumulator(' + ', '.join(['{0}={1:s}'.format(*it)
                                          for it in self.items()])

    def update(self, *args, **kwargs):
        """ Update the accumulator with a new set of pairs, a dictionary
            or a set of keyword arguments
        """
        # Update using argument which may be dictionaries
        # or lists of key, value pairs
        if args:
            for arg in args:
                try:
                    for key, value in arg.items():
                        self[key] = value
                except AttributeError:
                    # We have a list of pairs
                    for key, value in arg:
                        self[key] = value

        # Update using keyword arguments
        if kwargs:
            for key, value in kwargs.items():
                self[key] = value

    def replace(self, key, value):
        """ Explicitly replace the current value of key with the given value
        """
        del self._dict[key]
        self[key] = value

    def __setitem__(self, key, value):
        """ Setting items adds them to a list of values, rather than
            overwriting
        """
        self._dict[key].append(value)

    def __getitem__(self, key):
        """ Return items from the dictionary
        """
        item = self._dict[key]
        if len(item) == 1:
            return item[0]
        else:
            return item

    def __delitem__(self, key):
        """ Remove an item from the dictionary
        """
        del self._dict[key]

    def keys(self):
        """ Return the keys from the dictionary
        """
        return self._dict.keys()

    def values(self):
        """ Return the values from the dictionary
        """
        return [v[0] if len(v) == 1 else v for v in self._dict.values()]

    def items(self):
        """ Return the items from the dictionary
        """
        return zip(self.keys(), self.values())

