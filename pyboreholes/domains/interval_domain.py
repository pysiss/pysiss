""" file:   interval_domain.py (pyboreholes.domains)
    author: Jess Robertson & Ben Caradoc-Davies
            CSIRO Earth Science and Resource Engineering
    date:   Sunday November 10, 2013

    description: Domain for interval data (data defined over an interval in
        the borehole).

    An IntervalDomain is is a sequence of borehole segments each having a
    single value for each property; this value is taken to be the same across
    the entire length of the interval. IntervalDomains can be merged to form a
    new IntervalDomain that has the intervals whose boundaries are the union
    of the boundaries of the source IntervalDomains. An IntervalDomain can be
    interpolated onto a SamplingDomain.

    Intervals must be in depth order and not overlap, but there might
    be gaps between intervals.
"""

from .domain import Domain
import numpy


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

        # Generate a new IntervalDomain
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