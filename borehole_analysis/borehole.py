#!/usr/bin/env python
"""Classes to represent a borehole.

Borehole has point features and domains on which properties are defined.
A property can be defined on multiple domains. Features and domains are containers for
the properties defined on them.

A Feature is analogous to a spatial point feature. It has a depth and properties
but it makes no sense to perform any interpolation on these.

An IntervalDomain is is a sequence of borehole segments each having a single value for each property;
this value is taken to be the same across the entire length of the interval.
IntervalDomains can be merged to form a new IntervalDomain that has the intervals whose
boundaries are the union of the boundaries of the source IntervalDomains. An IntervalDomain can be
interpolated onto a SamplingDomain.

A SamplingDomain is a sequence of depths at which continuous properties are sampled.
Analogous to a coverage. One SamplingDomain can be interpolated onto another.

Depths are measured in metres down-hole from the borehole collar;
depth sequences must be in monotonically increasing order.

Property units are expressed as Unified Code for Units of Measure (UCUM):
http://unitsofmeasure.org/ucum.html
"""


class Borehole(object):

    """Borehole model.

    Properties:

    features -- dict mapping feature name to Feature
    interval_domains -- dict mapping interval domain name to IntervalDomain
    sampling_domains -- dict mapping sampling domain name to SamplingDomain
    """

    def __init__(self, name):
        """Constructor.

        name -- identifier (string)
        """
        self.name = name
        self.collar_location = None
        self.survey = None
        self.features = dict()
        self.interval_domains = dict()
        self.sampling_domains = dict()

    def add_feature(self, name, depth):
        """Add and return a new Feature.

        name -- identifier (string)
        depth -- down-hole depth in metres from collar (numeric)
        """
        self.features[name] = Feature(name, depth)
        return self.features[name]

    def add_interval_domain(self, name, from_depth, to_depths):
        """Add and return a new IntervalDomain

        name -- identifier (string)
        from_depths -- interval start point down-hole depths in metres from collar (any sequence, could be a list or numpy array)
        to_depths -- interval end point down-hole depths in metres from collar (any sequence, could be a list or numpy array)
        """
        self.interval_domains[name] = IntervalDomain(name, from_depth, to_depths)
        return self.interval_domains[name]

    def add_sampling_domain(self, name, depths):
        """Add and return a new SamplingDomain.

        depths -- sampling point down-hole depths in metres from collar (any sequence, could be a list or numpy array)
        """
        self.sampling_domains[name] = SamplingDomain(name, depths)
        return self.sampling_domains[name]

    def desurvey(self, depths, crs):
        """"Return the depths as three-dimensional points in the given coordinate reference system"""
        raise NotImplementedError

    def add_merged_interval_domain(self, name, source_name_one, source_name_two):
        """Add a new merged interval domain from the two sources"""
        raise NotImplementedError


class Feature(object):

    """A point feature with properties but no spatial extent.

    Properties:

    depth -- down-hole depth in metres
    properties -- dict mapping property name to Property
    """

    def __init__(self, name, depth):
        self.name = name
        self.depth = depth
        self.properties = dict()

    def add_property(self, property_type, values):
        """Add a property to this feature.

        values -- a single value or multiple values for a multivalued property
        """
        self.properties[property_type.name] = Property(property_type, values)

    def get_property_names(self):
        return self.properties.keys()

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

    @property
    def name(self):
        return self.property_type.name


class CoordinateReferenceSystem(object):

    """System for describing a spatial location as a tuple of real numbers."""

    def  __init__(self):
        raise NotImplementedError


class Survey(object):

    """The spatial shape of the borehole path in three dimensions from the collar.
    Used to convert a sequence of down-hole depths into a sequence of three-dimensional
    points in some coordinate reference system.
    """

    def __init__(self):
        raise NotImplementedError


