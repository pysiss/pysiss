#!/usr/bin/env python
""" Classes to represent data domains etc in boreholes

An IntervalDomain is is a sequence of borehole segments each having a single
value for each property; this value is taken to be the same across the entire
length of the interval. IntervalDomains can be merged to form a new
IntervalDomain that has the intervals whose boundaries are the union of the
boundaries of the source IntervalDomains. An IntervalDomain can be
interpolated onto a SamplingDomain.

A SamplingDomain is a sequence of depths at which continuous properties are
sampled. Analogous to a coverage. One SamplingDomain can be interpolated onto
another.
"""

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

    def add_property(self, property_type, values):
        """Add and return a new property"""
        assert self.size == len(values), "values must have the same number of elements as the domain"
        self.properties[property_type.name] = Property(property_type, values)
        return self.properties[property_type.name]

    def get_property_names(self):
        return self.properties.keys()


class IntervalDomain(Domain):

    def __init__(self, name, from_depths, to_depths):
        """Constructor.

        Intervals must be in depth order and not overlap, but there might be gaps between intervals.

        name -- identifier (string)
        from_depths -- interval start point down-hole depths in metres from collar (any sequence, could be a list or numpy array)
        to_depths -- interval end point down-hole depths in metres from collar (any sequence, could be a list or numpy array)
        """
        Domain.__init__(self, name, len(from_depths))
        assert len(from_depths) == len(to_depths)
        for i in range(self.size - 1):
            assert from_depths[i] < from_depths[i + 1], "from_depths must be monotonically increasing"
            assert to_depths[i] < to_depths[i + 1], "to_depths must be monotonically increasing"
            assert to_depths[i] <= from_depths[i + 1], "intervals must not overlap"
        for i in range(self.size):
            assert from_depths[i] < to_depths[i], "intervals must have positive length"
        self.from_depths = from_depths
        self.to_depths = to_depths


class SamplingDomain(Domain):

    def __init__(self, name, depths):
        """Constructor.

        Depths must be in monotonically increasing order.

        name -- identifier (string)
        depths -- sample down-hole depths in metres from collar (any sequence, could be a list or numpy array)
        """
        Domain.__init__(self, name, len(depths))
        for i in range(self.size - 1):
            assert depths[i] < depths[i + 1], "depths must be monotonically increasing"
        self.depths = depths




class PropertyType(object):

    """The metadata for a property."""

    def __init__(self, name, long_name=None, description=None, units=None):
        """

        name -- identifier (string)
        long_name -- name for presentation to user (string) or None
        description -- descriptive phrase (string)
        units -- unit in Unified Code for Units of Measure (UCUM) (string)
        """
        self.name = name
        self._long_name = long_name
        self.description = description
        self.units = units

    @property
    def long_name(self):
        """Return long name or name if no long name."""
        return self._long_name if self._long_name is not None else self.name


class Property(object):

    """Container for values with type.

    values must match the length of the domain: for sampling and interval domains,
    it must be a sequence of the same length as the depths. For a feature is should be
    a single value unless it is a multivalued category.
    """

    def __init__(self, property_type, values):
        self.property_type = property_type
        self.values = values

    def __repr__(self):
        """ String representation
        """
        info = 'Property {0}: type {1} with {2} values'
        return info.format(self.name, self.property_type.long_name(),
            len(self.values))

    @property
    def name(self):
        return self.property_type.name


## Transfer functions
def interpolate_property(interval_domain, sampling_domain, method='linear'):
    """ Interpolate a property from an IntervalDomain to a SamplingDomain.
    """
    raise NotImplementedError

def average_property(sampling_domain, interval_domain, method='mean'):
    """ Average a property from a SamplingDomain to an IntervalDomain
    """
    raise NotImplementedError

## Splitting functions
def split_at_gaps(domain, gap_metric='spacing_median'):
    """ Split a domain by finding significant gaps in the domain.

        A metric to define 'gaps' is required. Currently we only have 'spacing_median', which is really only suitable for SamplingDomain instances.

        Available metrics:
            'spacing_median': a gap is defined as a spacing between samples which is an order of magnitude above the median sample spacing in a domain.
    """
    # Select gap metric to use, generate gap locations
    spacing = numpy.diff(domain)
    if gap_metric is 'spacing_mean':
        med_spacing = numpy.median(spacing)
        gap_indices = numpy.flatnonzero(spacing > 10 * med_spacing)
    else:
        raise NotImplementedError("Unknown gap metric {0}".format(gap_metric))

    # We need to include the start and end of the domain!
    gap_indices = [0] + list(gap_indices) + [-1]

    # Form a list of data subdomains
    for idx in range(len(gap_indices) - 1):
        # Domains start _after_ the gap & end with next gap
        subdomains.append((
            domain.depths[(gap_indices[idx] + 1):(gap_indices[idx + 1])]))
    subdomains.append((self.domain[gap_indices[-1] + 1], self.domain[-1]))
    return subdomains

def spacing_split_metric(coeff):
    """ Specifies a gap in data based on sample spacing relative to mean
        sample spacing.
    """
