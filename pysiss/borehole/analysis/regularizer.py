""" file: regularizer.py (pysiss.borehole.analysis)
    author: Jess Robertson
            CSIRO Earth Science and Resource Engineering
    date: Sunday November 10, 2013

    description: Utilities to generate regularly spaced data from irregular
        grids.
"""

import numpy
import scipy.interpolate

# Reinterpolate functions
def unique(array, return_index=True, sort_method='heapsort', eqtest=None):
    """ Find the unique elements of an array.

        Returns the sorted unique elements of an array. There are two optional
        outputs in addition to the unique elements: the indices of the input
        array that give the unique values, and the indices of the unique array
        that reconstruct the input array.

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
    """ Resamples a dataset over a given dataset onto a regularly
        gridded dataset.

        On initialisation, a spline fit to the signal is generated. Subsequent
        calls to the ReSampler instance will use this spline to generate the
        resampled arrays.

        This is really just a wrapper around `scipy.interpolate.
        InterpolatedUnivariateSpline` which adds some cruft to generate a
        uniform grid. If you want a non-uniform grid then you might like to
        take a look at that function.

        :param dataset: the locations of each signal value in the dataset.
            Optional, if `spline` is specified then these signal will be
            ignored.
        :type dataset: `numpy.ndarray`
        :param signal: the signal evaluated at a given set of points. If
            `spline` is specified then these signal will be ignored.
        :type signal: `numpy.ndarray`
        :param order: the interpolation order for the spline. Optional,
            defaults to 3 (giving cubic interpolation)
        :type order: `int`
    """

    def __init__(self, dataset, signal, order=3):
        """ Initialise the ReSampler instance
        """
        # Check inputs
        if dataset is None or signal is None:
            raise ValueError("You must specify both signal and locations to"
                " resample signal.")
        elif len(dataset) != len(signal):
            raise ValueError("DataSet and value arrays are different lengths.")
        self.dataset, self.signal = dataset, signal
        self.order = order

        # Data points must be increasing, perform a sort if not
        sorted_signal, sorted_index = \
            unique(self.dataset, sort_method='heapsort',
                eqtest=lambda a, b: (a - b) ** 2 / numpy.abs(a) <= 1e-12)
        sorted_dataset = self.dataset[sorted_index]
        sorted_signal = self.signal[sorted_index]

        # Get dataset bounds
        self.dataset_bounds = (sorted_dataset[0], sorted_dataset[-1])

        # Initialise underlying Spline instance
        super(ReSampler, self).__init__(
            x=sorted_dataset, y=sorted_signal, w=None,
            bbox=self.dataset_bounds, k=self.order)

    def resample(self, nsamples, dataset_bounds=None, derivative=0):
        """ Generate a resampled dataset.

            The locations of the resampled points are uniformly distributed over the range specified in `dataset_bounds`, which defaults to the range of dataset values supplied.

            :param nsamples: number of resampled points
            :type nsamples: int
            :param dataset_bounds: the range to resample over, given as a pair `(dmin, dmax)`. Optional - if the dataset_values array not is specified, this defaults to the max and min of the input data.
            :type dataset_bounds: 2-tuple of int
            :param derivative: The order of derivative to return. `derivative=0` returns the value at x, `derivative=1` the first derivative and so on...
            :type derivative: int
            :returns: Two `numpy.ndarray` of length nsamples containing the resampled dataset and the dataset grid
        """
        if dataset_bounds is None:
            dataset_bounds = self.dataset_bounds
        resampled_dataset = numpy.linspace(dataset_bounds[0],
            dataset_bounds[1], nsamples)
        resampled_data = super(ReSampler, self).__call__(
            x=resampled_dataset, nu=derivative)
        return resampled_dataset, resampled_data
