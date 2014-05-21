""" file:   utilities.py (pyboreholes)
    author: Jess Robertson
            CSIRO Earth Science and Resource Engineering
    email:  jesse.robertson@csiro.au
    date:   Wednesday May 1, 2013

    description: Utility functions for the cwavelet module.
"""

import numpy
import functools
import uuid


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


class id_object(object):

    """ A mixin class to implement UUID comparisons for child classes

        This metaclass generates a UUID for a class at initialization,
        and defines the class __eq__ method to use this UUID.
    """

    def __init__(self, name, *args, **kwargs):
        super(id_object, self).__init__(*args, **kwargs)
        self.uuid = uuid.uuid5(uuid.NAMESPACE_DNS, name)

    def __eq__(self, other):
        """ Equality test

            Class instances are equal if their UUIDs match
        """
        return self.uuid == other.uuid


def heaviside(values):
    r""" Heaviside function.

        The Heaviside step function, or the unit step function, usually
        denoted by :math`H`, is a discontinuous function whose value is zero
        for negative argument and one for positive argument. We also take
        :math:`H(0) = 0`, although this rarely matters in practise.

        :param values: the argument values
        :type values: numpy.ndarray
        :return: the Heaviside function evaluated at each value
    """
    result = numpy.ones_like(values)
    result[values <= 0] = 0.
    return result


def same_sign(value1, value2):
    """ Determine whether two values have the same sign

    """
    return numpy.sign(value1, dtype=int) == numpy.sign(value2, dtype=int)


def integrate(times, values):
    """ Return the definite integral of the given data at the given
        times
    """
    times = numpy.asarray(times)
    values = numpy.asarray(values)
    return numpy.cumsum(numpy.gradient(times) * values)


def mask_all_nans(*arrays):
    """ Mask all indices where any array has a NaN.

        Example usage:

            mask = mask_all_nans(array1, array2)
            array1[mask]            # Both of these are guarenteed
            array2[mask]            # to be nan-free

        :param *arrays: The arrays to generate masks for. They should all have
            the same size or a ValueError will be raised.
        :type *arrays: `numpy.ndarrays`
        :returns: A `numpy.boolean_array` which can be used as a mask.
    """
    # Convert arrays to numpy arrays if required
    try:
        arrays = [numpy.asarray(a, dtype=numpy.float_) for a in arrays]
    except ValueError:
        raise ValueError("Arrays supplied to mask_all_nans must be able to be "
                         "converted to floats!")

    # Check that everything has the same shape
    shapes = [a.shape for a in arrays]
    if any([s != shapes[0] for s in shapes]):
        raise ValueError("Arrays supplied to mask_all_nans must be the same "
                         "size (arrays have shapes {0})".format(shapes))

    # Return the non-nan indices
    return numpy.logical_not(functools.reduce(numpy.logical_or,
                             [numpy.isnan(a) for a in arrays]))


def try_float(value_str):
    """ Tries to make str a value, returns NaN if not
    """
    try:
        return float(value_str)
    except ValueError:
        return numpy.nan
