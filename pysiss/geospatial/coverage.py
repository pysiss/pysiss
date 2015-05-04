""" file:   coverage.py (pysiss.geospatial)
    author: Jess Robertson
            CSIRO Minerals Resources Flagship
    date:   Monday 25 August, 2014

    desription: Implementation of classes for raster coverage data
"""

from __future__ import division, print_function

from ..metadata import unmarshal_all, ObjectWithMetadata

import rasterio
from matplotlib.pyplot import gca, get_cmap
import numpy


class Coverage(ObjectWithMetadata):

    """ Class containing raster GIS coverage data.
    """

    __metadata_tag__ = 'coverage'

    def __init__(self, filename, metadata, ident=None, **kwargs):
        super(Coverage, self).__init__(ident=ident)
        self.filename = filename

        # Set up geotiff data
        with rasterio.drivers():
            self._data = rasterio.open(self.filename)
        self.projection = self._data.crs
        self.bounds = self._data.bounds
        self._array = None

        # Store other metadata
        if kwargs:
            for attrib, value in kwargs.items():
                setattr(self, attrib, value)
        self.metadata.append_metadata(metadata)
        try:
            self.mask_value = \
                unmarshal_all(self.metadata,
                              '//wcs:nullvalues/wcs:singlevalue')[0]
        except IndexError:
            self.mask_value = None
        except AttributeError:
            self.mask_value = None

    def __del__(self):
        with rasterio.drivers():
            self._data.close()

    @property
    def array(self):
        """ Returns the data as a numpy array
        """
        if self._array is None:
            self._array = self._data.read()
        return self._array

    @property
    def mask(self):
        """ Returns the mask of the data array
        """
        if self.mask_value:
            return self.array == self.mask_value
        else:
            return numpy.zeros(shape=self.array.shape())

    def show(self, band=None, axes=None):
        """ Show the data stored in the image
        """
        # Get axes to stick the image in
        if axes is None:
            axes = gca()

        # Create a masked version of the image, masked values are 1
        band = band or 0
        if self.mask_value:
            image = numpy.ma.MaskedArray(self.array[band], mask=self.mask)
        else:
            image = self.array[band]

        # Constrain floats to lie between 0 and 1
        min_index = image.min()
        max_index = image.max()
        axes.imshow((image - min_index) / float(max_index - min_index),
                    interpolation='none',
                    cmap=get_cmap('coolwarm'))
        axes.set_axis_off()
