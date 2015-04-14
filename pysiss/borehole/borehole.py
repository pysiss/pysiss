""" file:   borehole.py (pysiss.borehole)
    author: Jess Robertson & Ben Caradoc-Davies
            CSIRO Earth Science and Resource Engineering
    date:   September 10, 2013

    description: Borehole class implementation
"""

from __future__ import division, print_function

from .details import Details, detail_type
from .datasets import DataSet, PointDataSet, IntervalDataSet
from .properties import Property
from ..utilities import id_object


class Borehole(id_object):

    """ Class to represent a borehole.

        Borehole has point features and datasets on which properties are
        defined. A property can be defined on multiple datasets. Features and
        datasets are containers for the properties defined on them.

        A Feature is analogous to a spatial point feature. It has a depth and
        properties but it makes no sense to perform any interpolation on these.

        An IntervalDataSet is is a sequence of borehole segments each having a
        single value for each property; this value is taken to be the same
        across the entire length of the interval. IntervalDataSets can be
        merged to form a new IntervalDataSet that has the intervals whose
        boundaries are the union of the boundaries of the source
        IntervalDataSets. An IntervalDataSet can be interpolated onto a
        PointDataSet.

        A PointDataSet is a sequence of depths at which continuous properties
        are sampled. Analogous to a coverage. One PointDataSet can be
        interpolated onto another.

        Depths are measured in metres down-hole from the borehole collar; depth
        sequences must be in monotonically increasing order.

        Property units are expressed as Unified Code for Units of Measure
        (UCUM): http://unitsofmeasure.org/ucum.html

        Some useful properties include:
            features - dict mapping feature ident to Feature
            interval_datasets - dict mapping interval dataset ident to
                IntervalDataSet
            point_datasets - dict mapping sampling dataset ident to
                PointDataSet

        :param ident: An identifier for the borehole
        :type ident: `string`
        :param origin_position: The borehole's position (lat/long; defaults to
            None)
        :type origin_position: OriginPosition class

    """

    # Mapping dataset types to class attributes
    _type_to_attr = {
        DataSet: 'datasets',
        PointDataSet: 'point_datasets',
        IntervalDataSet: 'interval_datasets',
    }

    def __init__(self, ident, latitude, longitude, elevation=None,
                 metadata=None):
        super(Borehole, self).__init__(ident=ident)
        self.ident = ident
        self.collar = namedtuple('location elevation')
        self.collar.location = \
            shapely.geometry.Point(longitude, latitude, elevation)
        self.collar.elevation = elevation
        self.survey = None
        self.metadata = metadata

        # Initialize dataset lists
        self.features = {}
        self.datasets = {}
        self.point_datasets = {}
        self.interval_datasets = {}

    def __repr__(self):
        """ String representation
        """
        info = 'Borehole {0} at {1} contains '
        info_str = info.format(self.ident, self.origin_position.xy)
        n_datasets = sum([len(getattr(self, a))
                          for a in self._type_to_attr.values()])
        summary_str = '{0} datasets'.format(n_datasets)
        summary_str += ' & {0} features'.format(len(self.features))
        dataset_list = ''
        if len(self.interval_datasets) > 0:
            idnames = [str(i) for i in self.interval_datasets.values()]
            dataset_list += ('\nIDs: ' + '\n     '.join(idnames))
        if len(self.point_datasets) > 0:
            pdnames = [str(p) for p in self.point_datasets.values()]
            dataset_list += ('\nSDs: ' + '\n     '.join(pdnames))
        else:
            borehole_details_str = ''

        return info_str + summary_str + dataset_list + borehole_details_str

    def add_feature(self, ident, depth):
        """ Add and return a new Feature.

            :param ident: The identifier for the new feature
            :type ident: `string`
            :param depth: Down-hole depth in metres from collar
            :type depth: `int` or `float`
            :returns: the new `pysiss.borehole.Feature` instance
        """
        self.features[ident] = Feature(ident, depth)
        return self.features[ident]

    def add_dataset(self, dataset):
        """ Add and return an existing dataset instance to the borehole.

            :param dataset: A precooked dataset with data
            :type dataset: subclassed from `pysiss.borehole.DataSet`
        """
        # Work out which attribute we should add the dataset to
        add_to_attr = self._type_to_attr[type(dataset)]

        # Add to the given attribute using the dataset ident as a key
        getattr(self, add_to_attr)[dataset.ident] = dataset
        return dataset

    def add_interval_dataset(self, ident, from_depths, to_depths):
        """ Add and return a new IntervalDataSet

            :param ident: The identifier for the new IntervalDataSet
            :type ident: `string`
            :param from_depths: Interval start point down-hole depths in metres
                    from collar
            :type from_depths: iterable of numeric values
            :param to_depths: Interval end point down-hole depths in metres
                from collar
            :type to_depths: iterable of numeric values

            :returns: the new `pysiss.borehole.IntervalDataSet` instance.
        """
        return self.add_dataset(IntervalDataSet(ident=ident,
                                                from_depths=from_depths,
                                                to_depths=to_depths))

    def add_point_dataset(self, ident, depths):
        """ Add and return a new PointDataSet.

            :param ident: The identifier for the new PointDataSet
            :type ident: `string`
            :param depths: Sample locations given as down-hole depths in metres
                    from collar
            :type depths: iterable of numeric values
            :returns: the new `pysiss.borehole.PointDataSet` instance.
        """
        return self.add_dataset(PointDataSet(ident=ident,
                                             depths=depths))

    # def desurvey(self, depths, crs):
    #     """ Return the depths as three-dimensional points in the given
    #         coordinate reference system
    #     """
    #     raise NotImplementedError

    # def add_merged_interval_dataset(self, ident, source_a, source_b):
    #     """ Add a new merged interval dataset from the two sources
    #     """
    #     raise NotImplementedError

    # def add_detail(self, ident, values, property_type=None):
    #     """ Add a detail to this borehole object.

    #         :param ident: An identifier for the detail
    #         :type ident: string
    #         :param values: The data to add
    #         :type values: any Python object
    #         :param property_type: The property type of the detail, optional,
    #                defaults to None
    #         :type property_type: pysiss.borehole.PropertyType
    #     """
    #     self.details.add_detail(ident, values, property_type)


class Feature(id_object):

    """A point feature with properties but no spatial extent.

        Useful properties:
            depth - down-hole depth in metres
            properties - dict mapping property ident to Property

        :param ident: The identifier for the new PointDataSet
        :type ident: `string`
        :param depth: Feature location given as down-hole depth in metres
                from collar
        :type depth: numeric value
    """

    def __init__(self, ident, depth):
        super(Feature, self).__init__(ident=ident)
        self.ident = ident
        self.depth = depth
        self.properties = dict()

    def __repr__(self):
        """ String representation
        """
        info = 'Feature {0}: at {1} depth with {2} properties'
        return info.format(self.ident, len(self.depth), len(self.properties))

    def add_property(self, property_type, values):
        """ Add a property to this feature.

            values - a single value or multiple values for a multivalued
                property
        """
        self.properties[property_type.ident] = Property(property_type, values)

    def get_property_idents(self):
        """ Return the idents of the available properties for this feature
        """
        return list(self.properties.keys())


# class CoordinateReferenceSystem(object):

#     """System for describing a spatial location as a tuple of real numbers."""

#     def __init__(self):
#         raise NotImplementedError


# class Survey(object):

#     """ The spatial shape of the borehole path in three dimensions from the
#         collar.

#         Used to convert a sequence of down-hole depths into a sequence of
#         three-dimensional points in some coordinate reference system.
#     """

#     def __init__(self):
#         raise NotImplementedError


class OriginPosition(id_object):

    """Representation of borehole origin position in terms of latitude,
       longitude, and elevation.
    """

    def __init__(self, latitude, longitude, elevation):
        super(OriginPosition, self).__init__(ident=str((latitude,
                                                        longitude,
                                                        elevation,
                                                        property_type)))
        self.location = shapely.geometry.Point(longitude, latitude)
        self.elevation = elevation

    def __repr__(self):
        """ String representation
        """
        info = "latitude {0[0]}, longitude {0[1]}, elevation {1}"
        info = info.format(self.location.xy, self.elevation)
        return info

    @property
    def xy(self):
        return self.location.xy



class BoreholeDetails(Details):

    """ Class to store details about drilling a Borehole
    """

    detail_type = detail_type('BoreholeDetail', 'ident values property_type')
