""" file:   raster.py (pysiss.coverage)
    author: Jess Robertson
            CSIRO Minerals Resources Flagship
    date:   Monday 25 August, 2014

    desription: Implementation of classes for raster coverage data
"""

from ..utilities import id_object
from ..metadata import MetadataRegistry

import rasterio


class Coverage(id_object):

    """ Class containing raster GIS coverage data.
    """

    md_registry = MetadataRegistry()

    def __init__(self, filename, metadata=None, ident=None, **kwargs):
        super(Coverage, self).__init__(ident='raster')
        self.ident = ident or self.uuid
        self.filename = filename

        # Set up geotiff data
        with rasterio.drivers():
            self.data = rasterio.open(self.filename)
        self.projection = self.data.crs
        self.bounds = self.data.bounds

        # Store other metadata
        if kwargs:
            for attrib, value in kwargs.items():
                setattr(self, attrib, value)

        if metadata:
            self._md_ident = metadata.ident
            self.type = metadata.type
            self.md_registry.register(metadata)
        else:
            self._md_ident = None
            self.type = None

    @property
    def metadata(self):
        """ Return metadata associated with this Coverage array
        """
        if self._md_ident:
            return self.md_registry[self._md_ident]
