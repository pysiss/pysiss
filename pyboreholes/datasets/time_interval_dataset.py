""" file: time_interval_dataset.py (pyboreholes.datasets)
    author: Jess Robertson
            CSIRO Earth Science and Resource ENgineering
    date:   Monday March 24, 2014

    description: DataSet for time-stamped data
"""

from .dataset import DataSet

import numpy
from scipy.interpolate import InterpolatedUnivariateSpline as Spline
from scipy.optimize import brentq as brent


class TimeIntervalDataSet(DataSet):

    """ Stores data which is indexed by timestamp rather than depth.

        This is primarily defined for dealing with LAR data.
    """

    def __init__(self, name, from_times, to_times):
        super(TimeIntervalDataSet, self).__init__(name, size=len(from_times))
        
        # Check inputs
        from_times = numpy.asarray(from_times)
        to_times = numpy.asarray(to_times)
        assert len(from_times) == len(to_times), \
            "from_ and to_times must be same length"
        assert all(numpy.gradient(from_times) > 0), \
            "from_times must be monotonically increasing"
        assert all(numpy.gradient(to_times) > 0), \
            "to_times must be monotonically increasing"
        assert all(to_times - from_times > 0), \
            "intervals must have positive length"
        assert all(to_times[:-1] <= from_times[1:]), \
            "intervals must not overlap"
        self.from_times = from_times
        self.to_times = to_times
   
    def __repr__(self):
        info = 'TimeIntervalDataSet {0}: with {1} times and {2} '\
               'properties'
        return info.format(self.name, len(self.depths),
                           len(self.properties))
    