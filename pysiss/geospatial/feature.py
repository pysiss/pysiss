""" file:   vector.py (pysiss.coverage)
    author: Jess Robertson
            CSIRO Minerals Resources Flagship
    date:   Monday 25 August, 2014

    desription: Implementation of classes for vector coverage data
"""

from __future__ import division, print_function

from ..metadata import ObjectWithMetadata


class Feature(ObjectWithMetadata):

    """ Class containing vector GIS data.

        Corresponds roughly to gsml:MappedFeatures
    """

    __metadata_tag__ = 'feature'

    def __init__(self, shape, ident=None, **kwargs):
        super(Feature, self).__init__(ident=ident)
        self.ident = ident or self.uuid

        # Store some info on the shape
        self.shape = shape

        # Store other metadata
        for attrib, value in kwargs.items():
            setattr(self, attrib, value)
        self.specification = specification
        self.type = self.md_registry[self.specification].type

    def __repr__(self):
        """ String representation
        """
        info = 'Feature {0} somewhere near {1} contains '
        info_str = info.format(self.ident,
                               self.shape.representative_point())
        return info_str
