""" file:   borehole.py (pyboreholes)
    author: Jess Robertson & Ben Caradoc-Davies
            CSIRO Earth Science and Resource Engineering
    date:   September 10, 2013

    description: Borehole class implementation
"""

from .borehole_details import BoreholeDetails
from .domains import Domain, PointSamples, IntervalSamples, WaveletDomain, TimeDomain, TimeIntervalSamples
from .properties import Property


class Borehole(object):

    """ Class to represent a borehole.

        Borehole has point features and domains on which properties are
        defined. A property can be defined on multiple domains. Features and
        domains are containers for the properties defined on them.

        A Feature is analogous to a spatial point feature. It has a depth and
        properties but it makes no sense to perform any interpolation on these.

        An IntervalSamples is is a sequence of borehole segments each having a
        single value for each property; this value is taken to be the same
        across the entire length of the interval. IntervalSampless can be merged
        to form a new IntervalSamples that has the intervals whose boundaries
        are the union of the boundaries of the source IntervalSampless. An
        IntervalSamples can be interpolated onto a PointSamples.

        A PointSamples is a sequence of depths at which continuous properties
        are sampled. Analogous to a coverage. One PointSamples can be
        interpolated onto another.

        Depths are measured in metres down-hole from the borehole collar; depth
        sequences must be in monotonically increasing order.

        Property units are expressed as Unified Code for Units of Measure
        (UCUM): http://unitsofmeasure.org/ucum.html

        Some useful properties include:
            features - dict mapping feature name to Feature
            interval_samples - dict mapping interval domain name to
                IntervalSamples
            point_samples - dict mapping sampling domain name to
                PointSamples
            wavelet_domains - dict mapping wavelet domain names to
                WaveletDomain instances

        :param name: An identifier for the borehole
        :type name: `string`
    """

    # Mapping domain types to class attributes
    _type_to_attr = {
        Domain: 'domains',
        PointSamples: 'point_samples',
        IntervalSamples: 'interval_samples',
        TimeDomain: 'time_domains',
        TimeIntervalSamples: 'time_interval_domains',
        WaveletDomain: 'wavelet_domains',
    }

    def __init__(self, name):
        self.name = name
        self.collar_location = None
        self.survey = None
        self.features = dict()
        self.details = BoreholeDetails()

        # Initialize domain lists
        for domain_attr in self._type_to_attr.values():
            setattr(self, domain_attr, dict())

    def __repr__(self):
        """ String representation
        """
        info_str = 'Borehole {0} contains '.format(self.name)
        n_domains = sum([len(getattr(self, a))
                         for a in self._type_to_attr.values()])
        summary_str = '{0} domains'.format(n_domains)
        summary_str += ' & {0} features'.format(len(self.features))
        domain_list = ''
        if len(self.interval_samples) > 0:
            domain_list += ('\nIDs: ' + '\n     '.join(
                            map(str, self.interval_samples.values())))
        if len(self.point_samples) > 0:
            domain_list += ('\nSDs: ' + '\n     '.join(
                            map(str, self.point_samples.values())))
        if len(self.wavelet_domains) > 0:
            domain_list += ('\nWDs: ' + '\n     '.join(
                            map(str, self.wavelet_domains.values())))
        return info_str + summary_str + domain_list

    def add_feature(self, name, depth):
        """ Add and return a new Feature.

            :param name: The identifier for the new feature
            :type name: `string`
            :param depth: Down-hole depth in metres from collar
            :type depth: `int` or `float`
            :returns: the new `pyboreholes.Feature` instance
        """
        self.features[name] = Feature(name, depth)
        return self.features[name]

    def add_domain(self, domain):
        """ Add an existing domain instance to the borehole.

            :param domain: A precooked domain with data
            :type domain: subclassed from `pyboreholes.Domain`
        """
        # Work out which attribute we should add the domain to
        add_to_attr = self._type_to_attr[type(domain)]

        # Add to the given attribute using the domain name as a key
        getattr(self, add_to_attr)[domain.name] = domain

    def add_interval_samples(self, name, from_depths, to_depths):
        """ Add and return a new IntervalSamples

            :param name: The identifier for the new IntervalSamples
            :type name: `string`
            :param from_depths: Interval start point down-hole depths in metres
                    from collar
            :type from_depths: iterable of numeric values
            :param to_depths: Interval end point down-hole depths in metres
                from collar
            :type to_depths: iterable of numeric values

            :returns: the new `pyboreholes.IntervalSamples` instance.
        """
        self.interval_samples[name] = \
            IntervalSamples(name, from_depths, to_depths)
        return self.interval_samples[name]

    def add_point_samples(self, name, depths):
        """ Add and return a new PointSamples.

            :param name: The identifier for the new PointSamples
            :type name: `string`
            :param depths: Sample locations given as down-hole depths in metres
                    from collar
            :type depths: iterable of numeric values
            :returns: the new `pyboreholes.PointSamples` instance.
        """
        self.point_samples[name] = PointSamples(name, depths)
        return self.point_samples[name]

    def add_wavelet_domain(self, name, point_samples,
                           wavelet=None, wav_properties=None):
        """ Add and return a new WaveletDomain.
        """
        self.wavelet_domains[name] = WaveletDomain(name, point_samples,
                                                   wavelet, wav_properties)
        return self.wavelet_domains[name]

    def desurvey(self, depths, crs):
        """ Return the depths as three-dimensional points in the given
            coordinate reference system
        """
        raise NotImplementedError

    def add_merged_interval_domain(self, name, source_name_a, source_name_b):
        """ Add a new merged interval domain from the two sources
        """
        raise NotImplementedError


class Feature(object):

    """A point feature with properties but no spatial extent.

        Useful properties:
            depth - down-hole depth in metres
            properties - dict mapping property name to Property

        :param name: The identifier for the new PointSamples
        :type name: `string`
        :param depth: Feature location given as down-hole depth in metres
                from collar
        :type depth: numeric value
    """

    def __init__(self, name, depth):
        self.name = name
        self.depth = depth
        self.properties = dict()

    def __repr__(self):
        """ String representation
        """
        info = 'Feature {0}: at {1} depth with {2} properties'
        return info.format(self.name, len(self.depth), len(self.properties))

    def add_property(self, property_type, values):
        """ Add a property to this feature.

            values - a single value or multiple values for a multivalued
                property
        """
        self.properties[property_type.name] = Property(property_type, values)

    def get_property_names(self):
        """ Return the names of the available properties for this feature
        """
        return self.properties.keys()


class CoordinateReferenceSystem(object):

    """System for describing a spatial location as a tuple of real numbers."""

    def __init__(self):
        raise NotImplementedError


class Survey(object):

    """ The spatial shape of the borehole path in three dimensions from the
        collar.

        Used to convert a sequence of down-hole depths into a sequence of
        three-dimensional points in some coordinate reference system.
    """

    def __init__(self):
        raise NotImplementedError
