""" file:   vector.py (pysiss.coverage)
    author: Jess Robertson
            CSIRO Minerals Resources Flagship
    date:   Monday 25 August, 2014

    desription: Implementation of classes for vector coverage data
"""

from ..utilities import project, id_object


class MappedFeature(id_object):

    """ Class containing vector GIS data.

        Corresponds roughly to gsml:MappedFeatures
    """

    def __init__(self, shape, projection, ident=None, metadata=None, **kwargs):
        super(MappedFeature, self).__init__(name='mapped_feature')
        self.ident = ident or self.uuid

        # Store some info on the shape
        self.shape = shape
        self.projection = projection
        self.centroid = self.shape.representative_point()

        # Store other metadata
        for attrib, value in kwargs.items():
            setattr(self, attrib, value)
        self.metadata = metadata

    def __repr__(self):
        """ String representation
        """
        info = 'MappedFeature {0} somewhere near {1} contains '
        info_str = info.format(self.ident, self.centroid)
        return info_str

    def reproject(self, new_projection):
        """ Reproject the shape to a new projection.

            :param new_projection: The identifier for the new projection
            :type new_projection: int
        """
        self.shape = type(self.shape)(project(self.shape.positions))
