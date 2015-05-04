""" file:   survey.py (pysiss.borehole)
    author: Jess Robertson
            CSIRO Earth Science and Resource Engineering
    date:   May 1, 2015

    description: Borehole collar class implementation
"""

from __future__ import print_function, division

from ..metadata import ObjectWithMetadata


class Survey(ObjectWithMetadata):

    """ The spatial shape of the borehole path in three dimensions from the
        collar.

        Used to convert a sequence of down-hole depths into a sequence of
        three-dimensional points in some coordinate reference system.
    """

    __metadata_tag__ = 'boreholeSurvey'

    def __init__(self):
        raise NotImplementedError
