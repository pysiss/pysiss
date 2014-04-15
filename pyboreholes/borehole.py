""" file:   borehole.py (pyboreholes)
    author: Jess Robertson & Ben Caradoc-Davies
            CSIRO Earth Science and Resource Engineering
    date:   September 10, 2013

    description: Borehole class implementation
"""

from .borehole_details import BoreholeDetails
from .datasets import DataSet, PointDataSet, IntervalDataSet, WaveletDataSet, TimeDataSet, TimeIntervalDataSet
from .properties import Property


class Borehole(object):

    """ Class to represent a borehole.

        Borehole has point features and datasets on which properties are
        defined. A property can be defined on multiple datasets. Features and
        datasets are containers for the properties defined on them.

        A Feature is analogous to a spatial point feature. It has a depth and
        properties but it makes no sense to perform any interpolation on these.

        An IntervalDataSet is is a sequence of borehole segments each having a
        single value for each property; this value is taken to be the same
        across the entire length of the interval. IntervalDataSets can be merged
        to form a new IntervalDataSet that has the intervals whose boundaries
        are the union of the boundaries of the source IntervalDataSets. An
        IntervalDataSet can be interpolated onto a PointDataSet.

        A PointDataSet is a sequence of depths at which continuous properties
        are sampled. Analogous to a coverage. One PointDataSet can be
        interpolated onto another.

        Depths are measured in metres down-hole from the borehole collar; depth
        sequences must be in monotonically increasing order.

        Property units are expressed as Unified Code for Units of Measure
        (UCUM): http://unitsofmeasure.org/ucum.html

        Some useful properties include:
            features - dict mapping feature name to Feature
            interval_dataset - dict mapping interval dataset name to
                IntervalDataSet
            point_dataset - dict mapping sampling dataset name to
                PointDataSet
            wavelet_datasets - dict mapping wavelet dataset names to
                WaveletDataSet instances

        :param name: An identifier for the borehole
        :type name: `string`
    """

    # Mapping dataset types to class attributes
    _type_to_attr = {
        DataSet: 'datasets',
        PointDataSet: 'point_dataset',
        IntervalDataSet: 'interval_dataset',
        TimeDataSet: 'time_datasets',
        TimeIntervalDataSet: 'time_interval_datasets',
        WaveletDataSet: 'wavelet_datasets',
    }

    def __init__(self, name):
        self.name = name
        self.collar_location = None
        self.survey = None
        self.features = dict()
        self.details = BoreholeDetails()

        # Initialize dataset lists
        for dataset_attr in self._type_to_attr.values():
            setattr(self, dataset_attr, dict())

    def __repr__(self):
        """ String representation
        """
        info_str = 'Borehole {0} contains '.format(self.name)
        n_datasets = sum([len(getattr(self, a))
                         for a in self._type_to_attr.values()])
        summary_str = '{0} datasets'.format(n_datasets)
        summary_str += ' & {0} features'.format(len(self.features))
        dataset_list = ''
        if len(self.interval_dataset) > 0:
            dataset_list += ('\nIDs: ' + '\n     '.join(
                            map(str, self.interval_dataset.values())))
        if len(self.point_dataset) > 0:
            dataset_list += ('\nSDs: ' + '\n     '.join(
                            map(str, self.point_dataset.values())))
        if len(self.wavelet_datasets) > 0:
            dataset_list += ('\nWDs: ' + '\n     '.join(
                            map(str, self.wavelet_datasets.values())))
        return info_str + summary_str + dataset_list

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

    def add_dataset(self, dataset):
        """ Add an existing dataset instance to the borehole.

            :param dataset: A precooked dataset with data
            :type dataset: subclassed from `pyboreholes.DataSet`
        """
        # Work out which attribute we should add the dataset to
        add_to_attr = self._type_to_attr[type(dataset)]

        # Add to the given attribute using the dataset name as a key
        getattr(self, add_to_attr)[dataset.name] = dataset

    def add_interval_dataset(self, name, from_depths, to_depths):
        """ Add and return a new IntervalDataSet

            :param name: The identifier for the new IntervalDataSet
            :type name: `string`
            :param from_depths: Interval start point down-hole depths in metres
                    from collar
            :type from_depths: iterable of numeric values
            :param to_depths: Interval end point down-hole depths in metres
                from collar
            :type to_depths: iterable of numeric values

            :returns: the new `pyboreholes.IntervalDataSet` instance.
        """
        self.interval_dataset[name] = \
            IntervalDataSet(name, from_depths, to_depths)
        return self.interval_dataset[name]

    def add_point_dataset(self, name, depths):
        """ Add and return a new PointDataSet.

            :param name: The identifier for the new PointDataSet
            :type name: `string`
            :param depths: Sample locations given as down-hole depths in metres
                    from collar
            :type depths: iterable of numeric values
            :returns: the new `pyboreholes.PointDataSet` instance.
        """
        self.point_dataset[name] = PointDataSet(name, depths)
        return self.point_dataset[name]

    def add_wavelet_dataset(self, name, point_dataset,
                           wavelet=None, wav_properties=None):
        """ Add and return a new WaveletDataSet.
        """
        self.wavelet_datasets[name] = WaveletDataSet(name, point_dataset,
                                                   wavelet, wav_properties)
        return self.wavelet_datasets[name]

    def desurvey(self, depths, crs):
        """ Return the depths as three-dimensional points in the given
            coordinate reference system
        """
        raise NotImplementedError

    def add_merged_interval_dataset(self, name, source_name_a, source_name_b):
        """ Add a new merged interval dataset from the two sources
        """
        raise NotImplementedError


class Feature(object):

    """A point feature with properties but no spatial extent.

        Useful properties:
            depth - down-hole depth in metres
            properties - dict mapping property name to Property

        :param name: The identifier for the new PointDataSet
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
