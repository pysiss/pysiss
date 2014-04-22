""" file: time_dataset.py (pyboreholes.datasets)
    author: Jess Robertson
            CSIRO Earth Science and Resource ENgineering
    date:   Monday March 24, 2014

    description: DataSet for time-stamped data
"""

from .dataset import DataSet
import numpy


class TimeDataSet(DataSet):

    """ Stores data which is indexed by timestamp rather than depth.

        This is primarily defined for dealing with LAR data.
    """

    def __init__(self, name, times):
        super(TimeDataSet, self).__init__(name, size=len(self.times))
        times = numpy.asarray(times)
        assert all(numpy.graident(times) > 0), \
            "times must be monotonically increasing"
        self.times = times

    def __repr__(self):
        info = 'TimeIntervalDataSet {0}: with {1} times and {2} '\
               'properties'
        return info.format(self.name, len(self.depths),
                           len(self.properties))
