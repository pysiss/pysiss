#!/usr/bin/env python
""" Classes to represent data domains etc in boreholes

    An IntervalDomain is is a sequence of borehole segments each having a
    single value for each property; this value is taken to be the same across
    the entire length of the interval. IntervalDomains can be merged to form a
    new IntervalDomain that has the intervals whose boundaries are the union of
    the boundaries of the source IntervalDomains. An IntervalDomain can be
    interpolated onto a SamplingDomain.

    A SamplingDomain is a sequence of depths at which continuous properties are
    sampled. Analogous to a coverage. One SamplingDomain can be interpolated
    onto another.
"""

import numpy
from scipy.interpolate import InterpolatedUnivariateSpline as Spline

class Domain(object):

    """Spatial extent over which properties are defined.

    This is an abstract base class

    Properties:

    properties -- dict mapping property name to Property
    """

    def __init__(self, name, size):
        assert size > 0, "domain must have at least one element"
        self.properties = dict()
        self.size = size  # size of all values sequences
        self.name = name
        self.subdomains = None
        self.gaps = None

    def add_property(self, property_type, values):
        """ Add and return a new property
        """
        assert self.size == len(values), ("values must have the same number "
            "of elements as the domain")
        self.properties[property_type.name] = Property(property_type, values)
        return self.properties[property_type.name]

    def get_property_names(self):
        """ Return the properties defined over this domain
        """
        return self.properties.keys()

class IntervalDomain(Domain):

    """ IntervalDomain contains data which is defined over some depth interval.

        An IntervalDomain is is a sequence of borehole segments each having a
        single value for each property; this value is taken to be the same
        across the entire length of the interval. IntervalDomains can be merged
        to form a new IntervalDomain that has the intervals whose boundaries
        are the union of the boundaries of the source IntervalDomains. An
        IntervalDomain can be interpolated onto a SamplingDomain.

        Intervals must be in depth order and not overlap, but there might
        be gaps between intervals.

        name -- identifier (string)
        from_depths -- interval start point down-hole depths in metres
            from collar (any sequence, could be a list or numpy array)
        to_depths -- interval end point down-hole depths in metres from
            collar (any sequence, could be a list or numpy array)
    """

    def __init__(self, name, from_depths, to_depths):
        super(IntervalDomain, self).__init__(name, len(from_depths))
        assert len(from_depths) == len(to_depths)
        for i in range(self.size - 1):
            assert from_depths[i] < from_depths[i + 1], \
                "from_depths must be monotonically increasing"
            assert to_depths[i] < to_depths[i + 1], \
                "to_depths must be monotonically increasing"
            assert to_depths[i] <= from_depths[i + 1], \
                "intervals must not overlap"
        for i in range(self.size):
            assert from_depths[i] < to_depths[i], \
                "intervals must have positive length"
        self.from_depths = from_depths
        self.to_depths = to_depths

    def __repr__(self):
        info = 'IntervalDomain {0}: with {1} depth intervals and {2} '\
               'properties'
        return info.format(self.name, len(self.from_depths),
            len(self.properties))

    def get_interval(self, from_depth, to_depth, domain_name=None):
        """ Return the data between the given depths as as new IntervalDomain

            Only intervals completely contained by the from_depth/to_depth
            interval are returned.
        """
        # Specify a name if not already passed
        if domain_name is None:
            domain_name = '{0}: subdomain {1} to {2}'.format(
                self.name, from_depth, to_depth)

        # Select a data mask
        indices = numpy.where(
            numpy.logical_and(self.from_depths >= from_depth,
                              self.to_depths <= to_depth))

        # Generate a new SamplingDomain
        newdom = IntervalDomain(domain_name,
            self.from_depths[indices],
            self.to_depths[indices])
        for prop in self.properties.values():
            newdom.add_property(
                property_type=prop.property_type,
                values=prop.values[indices])
        return newdom

    def split_at_gaps(self):
        """ Split a domain by finding significant gaps in the domain.

            A metric to define 'gaps' is required. Currently we only have
            'spacing_median', which is really only suitable for SamplingDomain
            instances.

            Available metrics:
                'spacing_median': a gap is defined as a spacing between
                    samples which is an order of magnitude above the median
                    sample spacing in a domain.
        """
        # Generate gap locations
        gap_indices = numpy.flatnonzero(
            self.from_depths[1:] - self.to_depths[:-1])

        # Aggregate gap intervals
        self.gaps = []
        for idx in gap_indices:
            self.gaps.append((self.to_depths[idx], self.from_depths[idx + 1]))

        # We need to include the start and end of the domain!
        gap_indices = [0] + list(gap_indices) + [-1]

        # Form a list of data subdomains
        self.subdomains = []
        for idx in range(len(gap_indices) - 1):
            # Domains start _after_ the gap & end with next gap
            self.subdomains.append((
                self.from_depths[gap_indices[idx] + 1],
                self.to_depths[gap_indices[idx + 1]]))
        return self.subdomains, self.gaps

class SamplingDomain(Domain):

    """ Domain for data defined at points in the domain.

        A SamplingDomain is a sequence of depths at which continuous
        properties are sampled. Analogous to a coverage. One SamplingDomain
        can be interpolated onto another.

        Depths must be in monotonically increasing order.

        name -- identifier (string)
        depths -- sample down-hole depths in metres from collar (any sequence,
            could be a list or numpy array)
    """

    def __init__(self, name, depths):
        super(SamplingDomain, self).__init__(name, len(depths))
        for i in range(self.size - 1):
            assert depths[i] < depths[i + 1], \
                "depths must be monotonically increasing"
        self.depths = depths

    def __repr__(self):
        info = 'SamplingDomain {0}: with {1} depths and {2} '\
               'properties'
        return info.format(self.name, len(self.depths),
            len(self.properties))

    def get_interval(self, from_depth, to_depth, domain_name=None):
        """ Return the data between the given depths as as new SamplingDomain
        """
        # Specify a name if not already passed
        if domain_name is None:
            domain_name = '{0}: subdomain {1} to {2}'.format(
                self.name, from_depth, to_depth)

        # Generate a new SamplingDomain
        indices = self.get_interval_indices(from_depth, to_depth)
        newdom = SamplingDomain(domain_name, self.depths[indices])
        for prop in self.properties.values():
            newdom.add_property(
                property_type=prop.property_type,
                values=prop.values[indices])
        return newdom

    def get_interval_indices(self, from_depth, to_depth):
        """ Returns the indices for the depths in the given interval
        """
        return numpy.where(
            numpy.logical_and(self.depths >= from_depth,
                              self.depths <= to_depth))[0]

    def split_at_gaps(self, gap_metric='spacing_median', threshold=10):
        """ Split a domain by finding significant gaps in the domain.

            A metric to define 'gaps' is required. Currently we only have
            'spacing_median', which is really only suitable for SamplingDomain
            instances. A gap is found where the sample spacing is greater than
            threshold * <gap_metric>.

            Available metrics:
                'spacing_median': a gap is defined as a spacing between
                    samples which is an order of magnitude above the median
                    sample spacing in a domain.
        """
        # We need to add a small amount to the dataset so that the interval
        # picker works well in the case of subdomains with only one value
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

        # We need to include the start and end of the domain!
        gap_indices = [0] + list(gap_indices) + [-1]

        # Form a list of data subdomains
        self.subdomains = []
        for idx in range(len(gap_indices) - 1):
            # Domains start _after_ the gap & end with next gap
            from_depth = depths[gap_indices[idx] + 1]
            to_depth = depths[gap_indices[idx + 1]]

            # Check whether we need to jitter
            if gap_indices[idx] + 1 == gap_indices[idx + 1]:
                from_depth, to_depth = jitter(from_depth, to_depth)
            self.subdomains.append((from_depth, to_depth))
        return self.subdomains, self.gaps

    def regularize(self, npoints=None, domain_name=None, fill_method='median',
        degree=0):
        """ Resample domain onto regular grid.

            This regularizes the data so that all sample spacings are equal to the median spacing of the raw data. Returns a new SamplingDomain instance with the new data.

            Arguments:
                npoints - the number of new points. Optional, if not specified then the reinterpolated data will have the median spacing of the raw data.
                domain_name - the name for the returned SamplingDomain. Optional, defaults to "<current_name> resampled".
                fill_method - the method for filling the gaps. 'interpolate' uses the interpolated spline, 'mean' fills gaps with the mean value for the borehole.
                degree - the degree of the interpolation. Optional, defaults to 1 (i.e. linear interpolation). Values > 0 denote polynomial interpolation, a value of 0 uses nearest-neighbour interpolation.
        """
        # We need to identify gaps first
        if self.gaps is None:
            print "Warning - your domain hasn't been analysed for gaps yet. " \
                + "I'm going to assume you just want to use the default values"
            self.split_at_gaps()

       # Specify name & number of points if not already passed
        if domain_name is None:
            domain_name = '{0} resampled'.format(self.name)
        if npoints is None:
            spacing = float(numpy.median(numpy.diff(self.depths)))
            npoints = abs(self.depths[-1] - self.depths[0]) / spacing

        # Generate a new Domain with the resampled data
        new_depths = numpy.linspace(self.depths[0], self.depths[-1], npoints)
        newdom = SamplingDomain(domain_name, new_depths)

        # If we're doing nearest neighbours then we only need to work out the
        # interpolation once
        if degree == 0:
            # This line generates a set of indices which will reconstruct a
            # new signal using nearest neighbours, just do:
            # >>> property.values[interp_indices]
            interp_indices = numpy.argmin(
                numpy.asarray([
                    (self.depths - new_depths[:, numpy.newaxis]) ** 2]),
                axis=-1)[0]

        # Get gap indices etc and store for faster lookup
        if fill_method in ['mean', 'median', 'local mean', 'local median']:
            # These methods need gap indices
            gap_idxs = [newdom.get_interval_indices(*gap) for gap in self.gaps]
        if fill_method in ['local mean', 'local median']:
            # These methods need subdomain indices from the old domain
            sdom_idxs = [self.get_interval_indices(*sdom)
                for sdom in self.subdomains]

        # Resample properties
        for prop in self.properties.values():
            if prop.property_type.isnumeric is False:
                # We can't interpolate non-numeric data
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

            # Push back to new domain
            newdom.add_property(prop.property_type, new_values)

        # Copy over gaps and subdomains
        newdom.gaps = self.gaps
        newdom.subdomains = self.subdomains
        return newdom


class PropertyType(object):

    """The metadata for a property."""

    def __init__(self, name, long_name=None, description=None, units=None,
        isnumeric=True, detection_limit=None):
        """

        name -- identifier (string)
        long_name -- name for presentation to user (string) or None
        description -- descriptive phrase (string)
        units -- unit in Unified Code for Units of Measure (UCUM) (string)
        isnumeric -- whether property is numeric or categorical
        """
        self.name = name
        self._long_name = long_name
        self.description = description
        self.units = units
        self.isnumeric = isnumeric
        self.detection_limit = detection_limit

    def __repr__(self):
        info = 'PropertyType {0}: long name is "{1}", units are {2}'
        return info.format(self.name, self.long_name, self.units)

    @property
    def long_name(self):
        "Return long name or name if no long name."
        return self._long_name if self._long_name is not None else self.name

    def copy(self):
        """ Return a copy of the PropertyType instance
        """
        return PropertyType(self.name, self.long_name, self.description,
            self.units)


class Property(object):

    """ Container for values with type.

        Values must match the length of the domain: for sampling and interval
        domains, it must be a sequence of the same length as the depths. For a
        feature is should be a single value unless it is a multivalued category
    """

    def __init__(self, property_type, values):
        self.property_type = property_type
        self.values = values

    def __repr__(self):
        info = 'Property {0}: {1} values in units of {2}'
        return info.format(self.name, len(self.values),
            self.property_type.units)

    @property
    def name(self):
        "The name of the property"
        return self.property_type.name

    def copy(self):
        """ Return a copy of the Property instance
        """
        return Property(self.property_type, self.values[:])
