""" file:   utilities.py (pyboreholes)
    author: Jess Robertson
            CSIRO Earth Science and Resource Engineering
    email:  jesse.robertson@csiro.au
    date:   Wednesday May 1, 2013

    description: Utility functions for the cwavelet module.
"""

import numpy
import functools


class Singleton(type):

    """ A singleton metaclass for implementing registries.

        This metaclass implements the Singleton pattern, so that only one
        instance of a class is ever instantiated. Subsequent calls to
        `__init__` will return a reference to this instantiation. To use
        this in your classes, just add

            __metaclass__ = Singleton

        to your class definition. There's a bunch of Python black magic
        (subclassing from type) which happens behind the scenes to make
        sure that only one class instance is instantiated.
    """

    def __init__(cls, name, bases, dic):
        super(Singleton, cls).__init__(name, bases, dic)
        cls.instance = None

    def __call__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super(Singleton, cls).__call__(*args, **kwargs)
        return cls.instance


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
