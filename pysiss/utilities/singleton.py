""" file:   singleton.py(pysiss.utilities)
    author: Jess Robertson
            CSIRO Minerals Resources Flagship
    date:   25 August 2014

    description: A singleton class instance, add __metaclass__ = singleton to
    your class to use it
"""

from __future__ import print_function, division


class singleton(type):

    """ A singleton metaclass for implementing registries.

        This metaclass implements the singleton pattern, so that only one
        instance of a class is ever instantiated. Subsequent calls to
        `__init__` will return a reference to this instantiation. To use
        this in your classes, just add

            metaclass=singleton

        to your class definition.
    """

    def __init__(cls, name, bases, dictionary):
        super(singleton, cls).__init__(name, bases, dictionary)
        cls.instance = None

    def __call__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super(singleton, cls).__call__(*args, **kwargs)
        return cls.instance
