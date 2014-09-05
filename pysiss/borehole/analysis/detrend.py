""" file: detrend.py (pysiss.borehole.analysis)
    author: Jess Robertson
            CSIRO Earth Science and Resource Engineering
    date: Sunday November 10, 2013

    description: Utilities to low-pass filter regularly spaced data in a
    PointDataSet instance (i.e. detrending).
"""

import numpy
import scipy.optimize


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
        :param param_guess: An initial guess at the parameters in the model.
            Usually an array of ones, or an array with the highest polynomial
            factor set to one and the rest to zero works well. A `ValueError`
            will be raised if `func` is specified but not `param_guess`.
        :type param_guess: `numpy.ndarray`
        :returns: None (data modified in place)
    """
    # Rescale the data to lie between 0 and 1
    drange, dmean = numpy.max(data) - numpy.min(data), data.mean()
    data_scaled = (data - dmean) / drange

    # We define the dataset to just be the unit interval which is fine for most
    # detrending things, when the actual parameter values don't matter
    dataset = numpy.linspace(0, 1, len(data))
    residuals = lambda p, y, x: y - func(p, x)

    # Perform least-squares fit
    param_guess = numpy.asarray(param_guess)
    param_lsq, flag = scipy.optimize.leastsq(
        residuals, param_guess, args=(data_scaled, dataset))
    if flag not in [1, 2, 3, 4]:
        raise ValueError("Least-squares routine failed to converge")
    data -= drange * func(param_lsq, dataset) + dmean
    return None


BUILTIN_TRENDS = {
    'none': lambda data: None,  # Not sure why you'd use this
    'mean': _detrend_mean,
    'linear': lambda data: _detrend_function(
        data,
        func=lambda b, x: b[1] * x + b[0],
        param_guess=[1, 0]),
    'quadratic': lambda data: _detrend_function(
        data,
        func=lambda b, x: b[2] * x ** 2 + b[1] * x + b[0],
        param_guess=[1, 0, 0]),
    'cubic': lambda data: _detrend_function(
        data,
        func=lambda b, x: b[3] * x ** 3 + b[2] * x ** 2 + b[1] * x + b[0],
        param_guess=[1, 0, 0, 0])
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
        :param trend: Optional, use a builtin trend model. One of 'none',
            'mean', 'linear', 'quadratic' or 'cubic'. Defaults to 'linear' if
            `func` is not specified.
        :type trend: str
        :param func: Optional, specify a model function to use in the
            detrending. The function should be of the form :math:`f(p, x)`
            where :math:`x` is some dataset parameter, and :math:`p` is a
            paramter vector for the model. See `scipy.optimize.leastsq` for
            more details on the form of this function.
        :param param_guess: An initial guess at the parameters in the model.
            Usually an array of ones, or an array with the highest polynomial
            factor set to one and the rest to zero works well. A `ValueError`
            will be raised if `func` is specified but not `param_guess`.
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
        raise ValueError("trend should be one of {0}"
                         .format(BUILTIN_TRENDS.keys()))
    return BUILTIN_TRENDS[trend or default](data)
