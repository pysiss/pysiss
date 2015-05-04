""" file:   collar.py (pysiss.borehole)
    author: Jess Robertson
            CSIRO Earth Science and Resource Engineering
    date:   May 1, 2015

    description: Borehole collar class implementation
"""

from __future__ import division, print_function

from shapely.geometry import Point
from ..utilities import id_object


class Collar(id_object):

    """Representation of borehole origin position in terms of latitude,
       longitude, and elevation.
    """

    def __init__(self, latitude, longitude, elevation=None):
        super(Collar, self).__init__(ident=str((latitude, longitude, elevation, 'collar')))
        self.location = Point(longitude, latitude)
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