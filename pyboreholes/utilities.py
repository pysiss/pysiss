#!/usr/bin/env python
""" file:   utilities.py (cwavelet)
    author: Jess Robertson
            CSIRO Earth Science and Resource Engineering
    email:  jesse.robertson@csiro.au
    date:   Wednesday May 1, 2013

    description: Utility functions for the cwavelet module.
"""

import numpy
import scipy.optimize
import scipy.interpolate
import functools

def heaviside(values):
    r""" Heaviside function

        The Heaviside step function, or the unit step function, usually denoted by :math`H`, is a discontinuous function whose value is zero for negative argument and one for positive argument. We also take :math:`H(0) = 0`, although this rarely matters in practise.

        :param values: the argument values
        :type values: numpy.ndarray
        :return: the Heaviside function evaluated at each value
    """
    result = numpy.ones_like(values)
    result[values <= 0] = 0.
    return result

def demean(data, axis=0):
    """ Return data minus its mean along the specified axis.

        :param data: Array of data
        :type data: `numpy.ndarray`
        :param axis: Axis along which to take means
        :type axis: int
        :returns: Demeaned data
    """
    data = numpy.asarray(data)
    if axis == 0 or axis is None or data.ndim <= 1:
        return data - data.mean(axis)
    else:
        index = [slice(None)] * data.ndim
        index[axis] = numpy.newaxis
        return data - data.mean(axis)[index]

# Detrend helper functions
def _detrend_mean(data):
    """ Detrend a signal by subtracting the mean.

        This function is internal to cwavelets.utilities and should not be
        called outside of it. See cwavelets.utilities.detrend instead.

        Data is modified in place.

        :param data: the one-dimensional input data
        :type data: `numpy.array`
        :returns: None (data modified in place)
    """
    data -= data.mean()

def _detrend_function(data, func, param_guess):
    """ Detrend a signal using the given function.

        Calculates the best fit trend function using `numpy.linalg.leastsq`
        and subtracts it from the data. Data is modified in place.

        This function is internal to cwavelets.utilities and should not be
        called outside of it. See cwavelets.utilities.detrend instead.

        :param data: the one-dimensional input data
        :type data: `numpy.array`
        :param func: specify a model function to use in the
            detrending.
        :param param_guess: An initial guess at the parameters in the model. Usually an array of ones, or an array with the highest polynomial factor set to one and the rest to zero works well. A `ValueError` will be raised if `func` is specified but not `param_guess`.
        :type param_guess: `numpy.ndarray`
        :returns: None (data modified in place)
    """
    # Rescale the data to lie between 0 and 1
    drange, dmean = numpy.max(data) - numpy.min(data), data.mean()
    data_scaled = (data - dmean) / drange

    # We define the domain to just be the unit interval which is fine for most
    # detrending things, when the actual parameter values don't matter
    domain = numpy.linspace(0, 1, len(data))
    residuals = lambda p, y, x: y - func(p, x)

    # Perform least-squares fit
    param_guess = numpy.asarray(param_guess)
    param_lsq, flag = scipy.optimize.leastsq(
        residuals, param_guess, args=(data_scaled, domain))
    if flag not in [1, 2, 3, 4]:
        raise ValueError("Least-squares routine failed to converge")
    data -= drange * func(param_lsq, domain) + dmean
    return None

BUILTIN_TRENDS = {
    'none': lambda data: None, # Not sure why you'd use this
    'mean': _detrend_mean,
    'linear': lambda data: _detrend_function(data,
        func = lambda b, x: b[1] * x + b[0],
        param_guess = [1, 0]),
    'quadratic': lambda data: _detrend_function(data,
        func = lambda b, x: b[2] * x ** 2 + b[1] * x + b[0],
        param_guess = [1, 0, 0]),
    'cubic': lambda data: _detrend_function(data,
        func = lambda b, x: b[3] * x ** 3 + b[2] * x ** 2 + b[1] * x + b[0],
        param_guess = [1, 0, 0, 0])
}

def detrend(data, trend=None, func=None, param_guess=None):
    r""" Detrend a data array in-place using the given method

        The behavior of the function depends on the trend supplied:
            -   If `trend` is `none`, no detrending is done
            -   if `trend` is `mean`, the data mean is subtracted from each
                data point.
            -   If `trend` is one of `linear`, `quadratic` or `cubic`, the
                data is detrended using best least-squares fit to the relevant
                model.

        Alternatively you can supply your own function for detrending using
        the func argument. This model function should take a one-dimensional
        numpy array, plus a vector of variables which can be fit to the data
        using `scipy.optimize.leastsq`. Note that specifying both `trend` and
        `func` when calling this function will raise a ValueError.

        If no extra parameters are specified, this function performs linear
        detrending.

        Internally, the input data are rescaled to the unit inteval to improve
        the detrending. This might cause a problem for cases where the range
        of the data is very small relative to machine precision.

        :param data: the one-dimensional input data
        :type data: `numpy.array`
        :param trend: Optional, use a builtin trend model. One of 'none', 'mean', 'linear', 'quadratic' or 'cubic'. Defaults to 'linear' if
            `func` is not specified.
        :type trend: str
        :param func: Optional, specify a model function to use in the
            detrending. The function should be of the form :math:`f(p, x)` where :math:`x` is some domain parameter, and :math:`p` is a paramter vector for the model. See `scipy.optimize.leastsq` for more details on the form
            of this function.
        :param param_guess: An initial guess at the parameters in the model. Usually an array of ones, or an array with the highest polynomial factor set to one and the rest to zero works well. A `ValueError` will be raised if `func` is specified but not `param_guess`.
        :type param_guess: `numpy.ndarray`
        :returns: None (data modified in place)
    """
    # Deal with default arguments
    if trend is not None and func is not None:
        raise ValueError("You should only specify one of the trend or func "
                         "keyword arguments to detrend.")
    elif func is not None:
        if param_guess is None:
            raise ValueError("You need to specify starting parameters for "
                             "your trend model.")
        return _detrend_function(data, func, param_guess)

    # If we're here, we are going to use a builtin funciton.
    default = 'linear'
    if (trend is not None) and (trend not in BUILTIN_TRENDS.keys()):
        raise ValueError("trend should be one of {0}"\
                         .format(BUILTIN_TRENDS.keys()))
    return BUILTIN_TRENDS[trend or default](data)

def mask_all_nans(*arrays):
    """ Mask all indices where any array has a NaN.

        Example usage:

            >>> mask = mask_all_nans(array1, array2)
            >>> array1[mask]            # Both of these are guarenteed
            >>> array2[mask]            # to be nan-free

        :param *arrays: The arrays to generate masks for. They should all have the same size or a ValueError will be raised.
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

