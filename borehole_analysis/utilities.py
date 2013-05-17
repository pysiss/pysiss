#!/usr/bin/env python
""" file:   utilities.py (cwavelet)
    author: Jess Robertson
            CSIRO Earth Science and Resource Engineering
    email:  jesse.robertson@csiro.au
    date:   Wednesday May 1, 2013

    description: Utility functions for the cwavelet module.
"""

import numpy
import scipy.optimize, scipy.interpolate

__all__ = ['heaviside', 'demean', 'detrend', 'ReSampler']

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

# Reinterpolate functions
def unique(array, return_index=True, sort_method='heapsort', eqtest=None):
    """ Find the unique elements of an array.

        Returns the sorted unique elements of an array. There are two optional outputs in addition to the unique elements: the indices of the input array that give the unique values, and the indices of the unique array that reconstruct the input array.

        :param array: Input array. This will be flattened if it is not already 1-D.
        :type array: array_like
        :param return_index: If True, also return the indices of `array` that result in the unique array. Optional, defaults to True.
        :type return_index: bool
        :param sort_method: The method used to sort the array. Defaults to 'heapsort', which has the best worst-case running time for pre-sorted arrays.
        :type sort_method: one of 'quicksort', 'mergesort' or 'heapsort'
        :param eqtest: Equality test function used to determine whether two elements are equal. The test function should take two numpy arrays and return a numpy bool array with the result of an elementwise test. Defaults to `lambda a, b: a ==b`.
        :type eqtest: numpy.ufunc
        :returns: The sorted unique values, and optionally the indices of the first occurrences of the unique values in the (flattened) original array (if `return_index` is True).
    """
    # Sort out array input
    try:
        array = array.flatten()
    except AttributeError:
        array = numpy.asanyarray(array).flatten()
    if array.size == 0:
        return array, numpy.empty(0, numpy.bool)

    # Set default equality test
    if eqtest is None:
        eqtest = lambda a, b: a == b

    # Do sort
    perm = array.argsort(kind=sort_method)
    aux = array[perm]

    # Check for inequality (i.e. we want to mask values with False in the mask 
    # array for which eqtest is true)
    neqflag = numpy.concatenate(([True], 
        numpy.logical_not(eqtest(aux[1:], aux[:-1]))))
    if return_index:
        return aux[neqflag], perm[neqflag]
    else:
        return aux[neqflag]


class ReSampler(scipy.interpolate.InterpolatedUnivariateSpline):
    """ Resamples a dataset over a given domain onto a regularly 
        gridded dataset.

        On initialisation, a spline fit to the signal is generated. Subsequent calls to the ReSampler instance will use this spline to generate the resampled arrays.

        This is really just a wrapper around `scipy.interpolate.InterpolatedUnivariateSpline` which adds some cruft to generate a uniform grid. If you want a non-uniform grid then you might like to take a look at that function.

        :param domain: the locations of each signal value in the domain. Optional, if `spline` is specified then these signal will be ignored.
        :type domain: `numpy.ndarray`
        :param signal: the signal evaluated at a given set of points. If `spline` is specified then these signal will be ignored.
        :type signal: `numpy.ndarray`
        :param order: the interpolation order for the spline. Optional, defaults to 3 (giving cubic interpolation)
        :type order: `int`
    """

    def __init__(self, domain, signal, order=3):
        """ Initialise the ReSampler instance
        """
        # Check inputs
        if domain is None or signal is None:
            raise ValueError("You must specify both signal and locations to"
                " resample signal.")
        elif len(domain) != len(signal):
            raise ValueError("Domain and value arrays are different lengths.")
        self.domain, self.signal = domain, signal
        self.order = order

        # Data points must be increasing, perform a sort if not
        sorted_signal, sorted_index = \
            unique(self.domain, sort_method='heapsort',
                eqtest=lambda a, b: (a - b) ** 2 / numpy.abs(a) <= 1e-12)
        sorted_domain = self.domain[sorted_index]
        sorted_signal = self.signal[sorted_index]

        # Get domain bounds
        self.domain_bounds = (sorted_domain[0], sorted_domain[-1])

        # Initialise underlying Spline instance
        super(ReSampler, self).__init__(
            x=sorted_domain, y=sorted_signal, w=None,
            bbox=self.domain_bounds, k=self.order)

    def resample(self, nsamples, domain_bounds=None, derivative=0):
        """ Generate a resampled dataset.

            The locations of the resampled points are uniformly distributed over the range specified in `domain_bounds`, which defaults to the range of domain values supplied. 

            :param nsamples: number of resampled points
            :type nsamples: int
            :param domain_bounds: the range to resample over, given as a pair `(dmin, dmax)`. Optional - if the domain_values array not is specified, this defaults to the max and min of the input data.
            :type domain_bounds: 2-tuple of int
            :param derivative: The order of derivative to return. `derivative=0` returns the value at x, `derivative=1` the first derivative and so on...
            :type derivative: int
            :returns: Two `numpy.ndarray` of length nsamples containing the resampled dataset and the domain grid
        """
        if domain_bounds is None:
            domain_bounds = self.domain_bounds
        resampled_domain = numpy.linspace(domain_bounds[0], 
            domain_bounds[1], nsamples)
        resampled_data = super(ReSampler, self).__call__(
            x=resampled_domain, nu=derivative)
        return resampled_domain, resampled_data


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
