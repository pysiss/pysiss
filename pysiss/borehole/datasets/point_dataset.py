""" file:   point_dataset.py (pysiss.borehole.datasets)
    author: Jess Robertson & Ben Caradoc-Davies
            CSIRO Earth Science and Resource Engineering
    date:   Sunday November 10, 2013

    description: DataSet for point sample data (data sampled at a finite set of
            points down a borehole)
"""

from .dataset import DataSet

import numpy
from scipy.interpolate import InterpolatedUnivariateSpline as Spline
import pandas


class PointDataSet(DataSet):

    """ DataSet for data defined at points in the dataset.

        A PointDataSet is a sequence of depths at which continuous
        properties are sampled. Analogous to a coverage. One PointDataSet
        can be interpolated onto another.

        Depths must be in monotonically increasing order.

        :param name: identifier for the dataSet
        :type name: string
        :param depths: sample down-hole depths in metres from collar
        :type depths: iterable
        :param details: The metadata associated with the dataset. Optional,
            defaults to None.
        :type details: pysiss.borehole.dataset.DatasetDetails
    """

    def __init__(self, name, depths, details=None):
        super(PointDataSet, self).__init__(
            name, len(depths), details=details)
        depths = numpy.asarray(depths)
        assert all(numpy.diff(depths) > 0), \
            "depths must be monotonically increasing"
        self.depths = depths

    def __repr__(self):
        info = 'PointDataSet {0}: with {1} depths and {2} '\
               'properties'
        return info.format(self.name, len(self.depths),
                           len(self.properties))

    def get_interval(self, from_depth, to_depth, dataset_name=None):
        """ Return the data between the given depths as as new PointDataSet
        """
        # Specify a name if not already passed
        if dataset_name is None:
            dataset_name = '{0}: subdataset {1} to {2}'.format(
                self.name, from_depth, to_depth)

        # Generate a new PointDataSet
        indices = self.get_interval_indices(from_depth, to_depth)
        newdom = PointDataSet(dataset_name, self.depths[indices])
        for prop in self.properties.values():
            newdom.add_property(prop.property_type, prop.values[indices])
        return newdom

    def get_interval_indices(self, from_depth, to_depth):
        """ Returns the indices for the depths in the given interval
        """
        return numpy.where(
            numpy.logical_and(self.depths >= from_depth,
                              self.depths <= to_depth))[0]

    def split_at_gaps(self, gap_metric='spacing_median', threshold=10):
        """ Split a dataset by finding significant gaps in the dataset.

            A metric to define 'gaps' is required. Currently we only have
            'spacing_median', which is really only suitable for PointDataSet
            instances. A gap is found where the sample spacing is greater than
            threshold * <gap_metric>.

            Available metrics:
                'spacing_median': a gap is defined as a spacing between
                    samples which is an order of magnitude above the median
                    sample spacing in a dataset.
        """
        # We need to add a small amount to the dataset so that the interval
        # picker works well in the case of subdatasets with only one value
        epsilon = 1e-10
        jitter = lambda a, b: (a - epsilon, b + epsilon)

        # Select gap metric to use, generate gap locations
        depths = self.depths
        spacing = numpy.diff(depths)
        if gap_metric is 'spacing_median':
            med_spacing = numpy.median(spacing)
            gap_indices = numpy.flatnonzero(spacing > threshold * med_spacing)
        else:
            raise NotImplementedError(
                "Unknown gap metric {0}".format(gap_metric))

        # Aggregate gap intervals
        self.gaps = []
        for idx in gap_indices:
            self.gaps.append((depths[idx], depths[idx + 1]))

        # We need to include the start and end of the dataset!
        gap_indices = [0] + list(gap_indices) + [-1]

        # Form a list of data subdatasets
        self.subdatasets = []
        for idx in range(len(gap_indices) - 1):
            # DataSets start _after_ the gap & end with next gap
            from_depth = depths[gap_indices[idx] + 1]
            to_depth = depths[gap_indices[idx + 1]]

            # Check whether we need to jitter
            if gap_indices[idx] + 1 == gap_indices[idx + 1]:
                from_depth, to_depth = jitter(from_depth, to_depth)
            self.subdatasets.append((from_depth, to_depth))
        return self.subdatasets, self.gaps

    def regularize(self, npoints=None, dataset_name=None, fill_method='median',
                   degree=0):
        """ Resample dataset onto regular grid.

            This regularizes the data so that all sample spacings are equal to
            the median spacing of the raw data. Returns a new PointDataSet
            instance with the new data.

            Arguments:
                npoints - the number of new points. Optional, if not specified
                    then the reinterpolated data will have the median spacing
                    of the raw data.
                dataset_name - the name for the returned PointDataSet.
                    Optional, defaults to "<current_name> resampled".
                fill_method - the method for filling the gaps. 'interpolate'
                    uses the interpolated spline, 'mean' fills gaps with the
                    mean value for the borehole.
                degree - the degree of the interpolation. Optional, defaults
                    to 1 (i.e. linear interpolation). Values > 0 denote
                    polynomial interpolation, a value of 0 uses nearest-
                    neighbour interpolation.
        """
        # We need to identify gaps first
        if self.gaps is None:
            print ("Warning - your dataset hasn't been analysed for gaps yet. "
                   "I'm going to assume you just want to use the default "
                   "values")
            self.split_at_gaps()

       # Specify name & number of points if not already passed
        if dataset_name is None:
            dataset_name = '{0} resampled'.format(self.name)
        if npoints is None:
            spacing = float(numpy.median(numpy.diff(self.depths)))
            npoints = abs(self.depths[-1] - self.depths[0]) / spacing

        # Generate a new DataSet with the resampled data
        new_depths = numpy.linspace(self.depths[0], self.depths[-1], npoints)
        newdom = PointDataSet(dataset_name, new_depths)

        # If we're doing nearest neighbours then we only need to work out the
        # interpolation once
        if degree == 0:
            # This line generates a set of indices which will reconstruct a
            # new signal using nearest neighbours, just do:
            # property.values[interp_indices]
            interp_indices = numpy.argmin(
                numpy.asarray([
                    (self.depths - new_depths[:, numpy.newaxis]) ** 2]),
                axis=-1)[0]

        # Get gap indices etc and store for faster lookup
        if fill_method in ['mean', 'median', 'local mean', 'local median']:
            # These methods need gap indices
            gap_idxs = [newdom.get_interval_indices(*gap) for gap in self.gaps]
        if fill_method in ['local mean', 'local median']:
            # These methods need subdataset indices from the old dataset
            sdom_idxs = [self.get_interval_indices(*sdom)
                         for sdom in self.subdatasets]

        # Resample properties
        for prop in self.properties.values():
            if prop.property_type.isnumeric is False:
                # We can't interpolate non-numeric data
                print ("Property {0} in dataset {1} is not numeric so I'm "
                       "skipping it. If this is a suprise to you, maybe you "
                       "should check whether you've correctly set the "
                       "is_numeric flag in the PropertyType class for this "
                       "property."
                       ).format(prop.property_type.name, self.name)
                continue

            # Generate spline fit if required, else use nearest-neighbours
            if degree == 0:
                new_values = prop.values[interp_indices]
            else:
                spl = Spline(self.depths, prop.values, k=degree)
                new_values = spl(new_depths)

            # Deal with gaps
            if fill_method == 'interpolate':
                # We've already generated an interpolated value, so move on
                # This option is here for error checking purposes
                pass

            elif fill_method == 'mean':
                # Mean value in gaps, poly interp otherwise
                meanval = prop.values.mean()
                for gidx in gap_idxs:
                    new_values[gidx] = meanval

            elif fill_method == 'median':
                # Median value in gaps
                medval = numpy.median(prop.values)
                for gidx in gap_idxs:
                    new_values[gidx] = medval

            elif fill_method == 'local mean':
                # local mean value in gaps
                smeans = [prop.values[s].mean() for s in sdom_idxs]
                for sma, gidx, smb in zip(smeans[:-1], gap_idxs, smeans[1:]):
                    new_values[gidx] = (sma + smb) / 2.

            elif fill_method == 'local median':
                # local median value in gaps
                gap_neighbours = zip(sdom_idxs[:-1], gap_idxs, sdom_idxs[1:])
                for sidxa, gidx, sidxb in gap_neighbours:
                    new_values[gidx] = numpy.median(numpy.concatenate(
                        prop.values[sidxa],
                        prop.values[sidxb]))

            else:
                raise NotImplementedError

            # Push back to new dataset
            newdom.add_property(prop.property_type, new_values)

        # Copy over gaps and subdatasets
        newdom.gaps = self.gaps
        newdom.subdatasets = self.subdatasets
        return newdom

    def resample(self, new_depths, dataset_name=None, fill_method='median',
                 degree=0):
        """ Resample dataset onto regular grid.

            Returns a new PointDataSet instance with the new data.

            Arguments:
                new_depths - The new depths to resample at.
                dataset_name - the name for the returned PointDataSet.
                    Optional, defaults to "<current_name> resampled".
                fill_method - the method for filling the gaps. 'interpolate'
                    uses the interpolated spline, 'mean' fills gaps with the
                    mean value for the borehole.
                degree - the degree of the interpolation. Optional, defaults
                    to 1 (i.e. linear interpolation). Values > 0 denote
                    polynomial interpolation, a value of 0 uses nearest-
                    neighbour interpolation.
        """
        # We need to identify gaps first
        if self.gaps is None:
            print ("Warning - your dataset hasn't been analysed for gaps yet. "
                   "I'm going to assume you just want to use the default "
                   "values")
            self.split_at_gaps()

       # Specify name & number of points if not already passed
        if dataset_name is None:
            dataset_name = '{0} resampled'.format(self.name)

        # Generate a new DataSet with the resampled data
        newdom = PointDataSet(dataset_name, new_depths)

        # If we're doing nearest neighbours then we only need to work out the
        # interpolation once
        if degree == 0:
            # This line generates a set of indices which will reconstruct a
            # new signal using nearest neighbours, just do:
            # property.values[interp_indices]
            interp_indices = numpy.argmin(
                numpy.asarray([
                    (self.depths - new_depths[:, numpy.newaxis]) ** 2]),
                axis=-1)[0]

        # Get gap indices etc and store for faster lookup
        if fill_method in ['mean', 'median', 'local mean', 'local median']:
            # These methods need gap indices
            gap_idxs = [newdom.get_interval_indices(*gap) for gap in self.gaps]
        if fill_method in ['local mean', 'local median']:
            # These methods need subdataset indices from the old dataset
            sdom_idxs = [self.get_interval_indices(*sdom)
                         for sdom in self.subdatasets]

        # Resample properties
        for prop in self.properties.values():
            if prop.property_type.isnumeric is False:
                # We can't interpolate non-numeric data
                print ("Property {0} in dataset {1} is not numeric so I'm "
                       "skipping it. If this is a suprise to you, maybe you "
                       "should check whether you've correctly set the "
                       "is_numeric flag in the PropertyType class for this "
                       "property."
                       ).format(prop.property_type.name, self.name)
                continue

            # Generate spline fit if required, else use nearest-neighbours
            if degree == 0:
                new_values = prop.values[interp_indices]
            else:
                spl = Spline(self.depths, prop.values, k=degree)
                new_values = spl(new_depths)

            # Deal with gaps
            if fill_method == 'interpolate':
                # We've already generated an interpolated value, so move on
                # This option is here for error checking purposes
                pass

            elif fill_method == 'mean':
                # Mean value in gaps, poly interp otherwise
                meanval = prop.values.mean()
                for gidx in gap_idxs:
                    new_values[gidx] = meanval

            elif fill_method == 'median':
                # Median value in gaps
                medval = numpy.median(prop.values)
                for gidx in gap_idxs:
                    new_values[gidx] = medval

            elif fill_method == 'local mean':
                # local mean value in gaps
                smeans = [prop.values[s].mean() for s in sdom_idxs]
                for sma, gidx, smb in zip(smeans[:-1], gap_idxs, smeans[1:]):
                    new_values[gidx] = (sma + smb) / 2.

            elif fill_method == 'local median':
                # local median value in gaps
                gap_neighbours = zip(sdom_idxs[:-1], gap_idxs, sdom_idxs[1:])
                for sidxa, gidx, sidxb in gap_neighbours:
                    new_values[gidx] = numpy.median(numpy.concatenate(
                        prop.values[sidxa],
                        prop.values[sidxb]))

            else:
                raise NotImplementedError

            # Push back to new dataset
            newdom.add_property(prop.property_type, new_values)

        # Copy over gaps and subdatasets
        newdom.gaps = self.gaps
        newdom.subdatasets = self.subdatasets
        return newdom

    def to_dataframe(self):
        """ Tranform the data in the dataset into a Pandas dataframe.
        """
        return pandas.DataFrame(
            data=dict(((k, self.properties[k].values)
                       for k in self.properties.keys())),
            index=self.depths)
