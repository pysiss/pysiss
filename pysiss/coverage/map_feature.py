""" file:   feature.py (pysiss.coverage)
    author: Jess Robertson
            CSIRO Minerals Resources Flagship
    date:   Monday 25 August, 2014

    desription: Implementation of classes for vector coverage data
"""

from ..utilities import id_object
from ..metadata import MetadataRegistry


class MapFeature(id_object):

    """ Class containing vector GIS data.

        Corresponds roughly to gsml:MappedFeatures
    """

    md_registry = MetadataRegistry()

    def __init__(self, shape, projection, metadata_ident, ident=None,
                 **kwargs):
        super(MapFeature, self).__init__(ident='map_feature')
        self.ident = ident or self.uuid

        # Store some info on the shape
        self.shape = shape
        self.projection = projection
        self.centroid = self.shape.representative_point()

        # Store other metadata
        if kwargs:
            for attrib, value in kwargs.items():
                setattr(self, attrib, value)
        self.metadata_ident = metadata_ident
        self.type = self.md_registry[self.metadata_ident].type

    def __repr__(self):
        """ String representation
        """
        info = 'MapFeature {0} somewhere near {1} contains '
        info_str = info.format(self.ident, self.centroid)
        return info_str

    def reproject(self, new_projection):
        """ Reproject the shape to a new projection.

            :param new_projection: The identifier for the new projection
            :type new_projection: int
        """
        raise NotImplementedError
        # self.shape = type(self.shape)(project(self.shape.positions))

    @property
    def metadata(self):
        """ Return the metadata associated with the MappedFeature
        """
        return self.md_registry[self.metadata_ident]
