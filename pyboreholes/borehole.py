#!/usr/bin/env python
""" file:   borehole.py (pyboreholes)
    author: Jess Robertson & Ben Caradoc-Davies
            CSIRO Earth Science and Resource Engineering
    date:   September 10, 2013

    description: Borehole class implementation
"""

from .domains import SamplingDomain, IntervalDomain, WaveletDomain
from .properties import Property

from collections import namedtuple

BoreholeDetail = namedtuple('BoreholeDetail', 'name values property_type')

class Borehole(object):

    """ Class to represent a borehole.

        Borehole has point features and domains on which properties are
        defined. A property can be defined on multiple domains. Features and
        domains are containers for the properties defined on them.

        A Feature is analogous to a spatial point feature. It has a depth and
        properties but it makes no sense to perform any interpolation on these.

        An IntervalDomain is is a sequence of borehole segments each having a
        single value for each property; this value is taken to be the same
        across the entire length of the interval. IntervalDomains can be merged
        to form a new IntervalDomain that has the intervals whose boundaries
        are the union of the boundaries of the source IntervalDomains. An
        IntervalDomain can be interpolated onto a SamplingDomain.

        A SamplingDomain is a sequence of depths at which continuous properties
        are sampled. Analogous to a coverage. One SamplingDomain can be
        interpolated onto another.

        Depths are measured in metres down-hole from the borehole collar; depth
        sequences must be in monotonically increasing order.

        Property units are expressed as Unified Code for Units of Measure
        (UCUM): http://unitsofmeasure.org/ucum.html

        Some useful properties include:
            features - dict mapping feature name to Feature
            interval_domains - dict mapping interval domain name to
                IntervalDomain
            sampling_domains - dict mapping sampling domain name to
                SamplingDomain
            wavelet_domains - dict mapping wavelet domain names to
                WaveletDomain instances
                
        :param name: An identifier for the borehole
        :type name: `string`
        :param origin_position: The borehole's position (lat/long; defaults to None)
        :type origin_position: OriginPosition class

    """

    # Mapping domain types to class attributes
    _type_to_attr = {
        SamplingDomain: 'sampling_domains',
        IntervalDomain: 'interval_domains',
        WaveletDomain: 'wavelet_domains',
    }

    def __init__(self, name, origin_position=None):
        self.name = name
        self.origin_position = origin_position
        self.details = BoreholeDetails()
        self.survey = None
        self.features = dict()

        # Initialize domain lists
        for domain_attr in self._type_to_attr.values():
            setattr(self, domain_attr, dict())

    def __repr__(self):
        """ String representation
        """
        info = 'Borehole {0} at origin position {1} contains '
        info_str = info.format(self.origin_position, self.name)
        n_domains = sum([len(getattr(self, a))
                         for a in self._type_to_attr.values()])
        summary_str = '{0} domains'.format(n_domains)
        summary_str += ' & {0} features'.format(len(self.features))
        domain_list = ''
        if len(self.interval_domains) > 0:
            domain_list += ('\nIDs: ' + '\n     '.join(
                            map(str, self.interval_domains.values())))
        if len(self.sampling_domains) > 0:
            domain_list += ('\nSDs: ' + '\n     '.join(
                            map(str, self.sampling_domains.values())))
        if len(self.wavelet_domains) > 0:
            domain_list += ('\nWDs: ' + '\n     '.join(
                            map(str, self.wavelet_domains.values())))
        if len(self.details.values()) > 0:
            borehole_details_str = '\nBorehole details: {0}'.format(self.details)
        else:
            borehole_details_str = ''
                
        return info_str + summary_str + domain_list + borehole_details_str

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

    def add_interval_domain(self, name, from_depths, to_depths):
        """ Add and return a new IntervalDomain

            :param name: The identifier for the new IntervalDomain
            :type name: `string`
            :param from_depths: Interval start point down-hole depths in metres
                    from collar
            :type from_depths: iterable of numeric values
            :param to_depths: Interval end point down-hole depths in metres
                from collar
            :type to_depths: iterable of numeric values

            :returns: the new `pyboreholes.IntervalDomain` instance.
        """
        self.interval_domains[name] = \
            IntervalDomain(name, from_depths, to_depths)
        return self.interval_domains[name]

    def add_sampling_domain(self, name, depths):
        """ Add and return a new SamplingDomain.

            :param name: The identifier for the new SamplingDomain
            :type name: `string`
            :param depths: Sample locations given as down-hole depths in metres
                    from collar
            :type depths: iterable of numeric values
            :returns: the new `pyboreholes.SamplingDomain` instance.
        """
        self.sampling_domains[name] = SamplingDomain(name, depths)
        return self.sampling_domains[name]

    def add_wavelet_domain(self, name, sampling_domain,
                           wavelet=None, wav_properties=None):
        """ Add and return a new WaveletDomain.
        """
        self.wavelet_domains[name] = WaveletDomain(name, sampling_domain,
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

    def add_detail(self, name, values, property_type=None):
        """ Add a detail to this borehole object. 

            :param name: An identifier for the detail
            :type name: string
            :param values: The data to add
            :type values: any Python object
            :param property_type: The property type of the detail, optional,
                   defaults to None
            :type property_type: pyboreholes.PropertyType
        """
        self.details.add_detail(name, values, property_type);
        
class Feature(object):

    """A point feature with properties but no spatial extent.

        Useful properties:
            depth - down-hole depth in metres
            properties - dict mapping property name to Property

        :param name: The identifier for the new SamplingDomain
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


class OriginPosition(object):
    
    """Representation of borehole origin position in terms of latitude 
       and longitude.
    """
    
    def __init__(self, latitude, longitude):
        self.latitude = latitude
        self.longitude = longitude
        
    def __repr__(self):
        """ String representation
        """
        info = "Origin position: latitude {0}, longitude {1}"
        return info.format(self.latitude, self.longitude)
   
     
class BoreholeDetails(dict):

    """ Class to store details about drilling a borehole.
    """

    def __init__(self):
        super(BoreholeDetails, self).__init__()

    def add_detail(self, name, values, property_type=None):
        """ Add a detail to this borehole object.

            :param name: An identifier for the detail
            :type name: string
            :param values: The data to add
            :type values: any Python object
            :param property_type: The property type of the detail, optional,
                   defaults to None
            :type property_type: pyboreholes.PropertyType
        """
        # TODO: implement Flyweight in terms of immutable named tuples; may not
        # be necessary by virtue of this immutability if each BoreholeDetail
        # instance is canonical/uniquely interned
        self[name] = BoreholeDetail(name=name,
                                    values=values,
                                    property_type=property_type)
                
    def __repr__(self):
        """ String representation of all borehole details.
        """
        return "\n".join(["Borehole detail: {0}".format(detail) for detail in self.values()])
        
    def __setattr__(self):
        """ Disable setattr method
        """
        raise NotImplementedError('Use add_detail to add details')