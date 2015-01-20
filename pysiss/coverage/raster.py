""" file:   vector.py (pysiss.coverage)
    author: Jess Robertson
            CSIRO Minerals Resources Flagship
    date:   Monday 25 August, 2014

    desription: Implementation of classes for raster coverage data
"""

from ..utilities import id_object
from ..metadata import MetadataRegistry


class Raster(id_object):

    """ Class containing raster GIS data.
    """

    md_registry = MetadataRegistry()

    def __init__(self, filename, metadata=None, ident=None, **kwargs):
        super(MappedFeature, self).__init__(ident='raster')

        # Some slots to store other data
        self._data = None
        self.projection = None
        self.bounds = None

        # Store other metadata
        if kwargs:
            for attrib, value in kwargs.items():
                setattr(self, attrib, value)

        self.metadata_ident = metadata_ident
        self.type = self.md_registry[self.metadata_ident].type

    @property
    def data(self):
        """ Return data as a rasterio file object
        """
        if self._data is None:
            
        with 