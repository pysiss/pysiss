""" file:   interval_dataset.py (pysiss.borehole.datasets)
    author: Jess Robertson & Ben Caradoc-Davies
            CSIRO Earth Science and Resource Engineering
    date:   Sunday November 10, 2013

    description: DataSet for interval data (data defined over an interval in
        the borehole).

    An IntervalDataSet is is a sequence of borehole segments each having a
    single value for each property; this value is taken to be the same across
    the entire length of the interval. IntervalSampling can be merged to form a
    new IntervalDataSet that has the intervals whose boundaries are the union
    of the boundaries of the source IntervalSampling. An IntervalDataSet can be
    interpolated onto a PointDataSet.

    Intervals must be in depth order and not overlap, but there might
    be gaps between intervals.
"""

from __future__ import division, print_function

from .dataset import DataSet
from .point_dataset import PointDataSet

import numpy
import pandas

def make_depth_index(from_depths, to_depths):
    """ Make a depth index for depth intervals

        Also checks that the depth interval data is ok
    """
    from_depths = numpy.asarray(from_depths)
    to_depths = numpy.asarray(to_depths)
    if not len(from_depths) == len(to_depths):
        raise ValueError("from_ and to_depths must be same length")
    elif not all(numpy.diff(from_depths) > 0):
        raise ValueError("from_depths must be monotonically increasing")
    elif not all(numpy.diff(to_depths) > 0):
        raise ValueError("to_depths must be monotonically increasing")
    elif not all(to_depths - from_depths > 0):
        raise ValueError("intervals must have positive length")
    elif not all(to_depths[:-1] <= from_depths[1:]):
        raise ValueError("intervals must not overlap")
    index = pandas.Index(numpy.vstack([from_depths, to_depths]).transpose())
    return index


class IntervalDataSet(DataSet):

    """ IntervalDataSet contains data which is defined over some depth
        interval.

        An IntervalDataSet is is a sequence of borehole segments each having a
        single value for each property; this value is taken to be the same
        across the entire length of the interval. IntervalSampling can be
        merged to form a new IntervalDataSet that has the intervals whose
        boundaries are the union of the boundaries of the source
        IntervalSampling. An IntervalDataSet can be interpolated onto a
        PointDataSet.

        Intervals must be in depth order and not overlap, but there might
        be gaps between intervals.

        :param ident: identifier for the dataSet
        :type ident: string
        :param from_depths: interval start point down-hole depths in metres
            from collar
        :type from_depths: iterable
        :param to_depths: interval end point down-hole depths in metres from
            collar
        :type to_depths: iterable
        :param metadata: The metadata associated with the dataset. Optional,
            defaults to None.
        :type metadata: pysiss.borehole.dataset.DatasetDetails
    """

    def __init__(self, ident, from_depths, to_depths, metadata=None):
        # Generate depth interval index
        index = make_depth_index(from_depths, to_depths)
        super(IntervalDataSet, self).__init__(ident, index, metadata)
        self.from_depths = self.index[:, 0]
        self.to_depths = self.index[:, 1]

    def __repr__(self):
        info = 'IntervalDataSet {0}: with {1} depth intervals and {2} '\
               'properties'
        return info.format(self.ident, len(self.from_depths),
                           len(self.properties))

    def get_interval(self, from_depth, to_depth, dataset_ident=None):
        """ Return the data between the given depths as as new IntervalDataSet

            Only intervals completely contained by the from_depth/to_depth
            interval are returned.
        """
        # Specify a ident if not already passed
        if dataset_ident is None:
            dataset_ident = '{0}: subdataset {1} to {2}'.format(
                self.ident, from_depth, to_depth)

        # Select a data mask
        indices = numpy.where(
            numpy.logical_and(self.from_depths >= from_depth,
                              self.to_depths <= to_depth))

        # Generate a new IntervalDataSet
        newdom = IntervalDataSet(dataset_ident,
                                 self.from_depths[indices],
                                 self.to_depths[indices])
        for prop in self.properties.values():
            newdom.add_property(
                property_type=prop.property_type,
                values=prop.values[indices])
        return newdom

    def split_at_gaps(self):
        """ Split a dataset by finding significant gaps in the dataset.

            A metric to define 'gaps' is required. Currently we only have
            'spacing_median', which is really only suitable for PointDataSet
            instances.

            Available metrics:
                'spacing_median': a gap is defined as a spacing between
                    samples which is an order of magnitude above the median
                    sample spacing in a dataset.
        """
        # Generate gap locations
        gap_indices = numpy.flatnonzero(
            self.from_depths[1:] - self.to_depths[:-1])

        # Aggregate gap intervals
        self.gaps = []
        for idx in gap_indices:
            self.gaps.append((self.to_depths[idx], self.from_depths[idx + 1]))

        # We need to include the start and end of the dataset!
        gap_indices = [0] + list(gap_indices) + [-1]

        # Form a list of data subdatasets
        self.subdatasets = []
        for idx in range(len(gap_indices) - 1):
            # DataSets start _after_ the gap & end with next gap
            self.subdatasets.append((
                self.from_depths[gap_indices[idx] + 1],
                self.to_depths[gap_indices[idx + 1]]))
        return self.subdatasets, self.gaps

    def to_point_dataset(self, ident=None, depths='midpoint'):
        """ Convert an IntervalDataSet to a PointDataSet

            Uses the specified method to recalculate the depths of the
            PointDataSet points. Defaults to using the midpoint of each
            interval.

            Available depth converters:
                'midpoint': Uses the midpoint of the sampled interval
                'from': Uses the upper depth of the sampled interval
                'to': Uses the lower depths of the sampled interval

            :param ident: The identifier for the new dataset. Optional,
                defaults to the same ident as the interval dataset.
            :type ident: string
            :param depths: the depth converter to use
            :returns: the new PointDataSet instance
        """
        # Generate ident
        if ident is None:
            ident = self.ident

        # Generate new depths
        if depths == 'midpoint':
            depths = (self.from_depths + self.to_depths) / 2.
        elif depths == 'from':
            depths = self.from_depths
        elif depths == 'to':
            depths = self.to_depths
        else:
            raise ValueError(
                'Unknown depth conversion method {0}'.format(depths))

        # Generate new dataset
        sdom = PointDataSet(ident=ident, depths=depths)
        sdom.properties = self.properties.copy()
        return sdom

    @property
    def dataframe(self):
        """ Tranform the data in the dataset into a Pandas dataframe.
        """
        return pandas.DataFrame(
            data=dict(((k, self.properties[k].values)
                       for k in self.properties.keys())),
            index=list(zip(self.from_depths, self.to_depths)))
