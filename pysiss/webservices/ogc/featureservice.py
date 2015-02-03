""" file: featureservice.py
    author: Jess Robertson
            CSIRO Mineral Resources Flagship
    date:   somehting

    decsription: Implementation of simple FeatureService class
"""

class FeatureService(id_object):

    """ Handles calls to an OGC WFS endpoint
    """

    def __init__(self, arg):
        super(FeatureService, self).__init__()
        self.arg = arg

