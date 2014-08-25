""" file:   singleton.py(pysiss.utilities)
    author: Jess Robertson
            CSIRO Minerals Resources Flagship
    date:   25 August 2014

    description: A Singleton class instance, add __metaclass__ = Singleton to
    your class to use it
"""


class Singleton(type):

    """ A singleton metaclass for implementing registries.

        This metaclass implements the Singleton pattern, so that only one
        instance of a class is ever instantiated. Subsequent calls to
        `__init__` will return a reference to this instantiation. To use
        this in your classes, just add

            __metaclass__ = Singleton

        to your class definition.
    """

    def __init__(cls, name, bases, dictionary):
        super(Singleton, cls).__init__(name, bases, dictionary)
        cls.instance = None

    def __call__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super(Singleton, cls).__call__(*args, **kwargs)
        return cls.instance
