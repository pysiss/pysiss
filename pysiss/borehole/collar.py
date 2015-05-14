""" file:   collar.py (pysiss.borehole)
    author: Jess Robertson
            CSIRO Earth Science and Resource Engineering
    date:   May 1, 2015

    description: Borehole collar class implementation
"""

from __future__ import division, print_function

from ..metadata import with_metadata

from shapely.geometry import Point


@with_metadata(tag='collarLocation')
class Collar(object):

    """Representation of borehole origin position in terms of latitude,
       longitude, and elevation.
    """

    def __init__(self, latitude, longitude, elevation=None, ident=None):
        super(Collar, self).__init__()
        self.ident = ident
        self.location = Point(longitude, latitude)
        self.elevation = elevation

    def __repr__(self):
        """ String representation
        """
        info = "Collar location at {0}, elevation {1}"
        info = info.format(self.location, self.elevation)
        return info

    @property
    def xy(self):
        return self.location.xy
