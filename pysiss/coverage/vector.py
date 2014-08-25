""" file:   vector.py
    author: Jess Robertson
            CSIRO Minerals Resources Flagship
    date:   Monday 25 August, 2014

    desription: Implementation of classes for vector coverage data
"""


class Vector(object):
    
    """ Class containing vector GIS data
    """
    
    def __init__(self, ident, shape, projection, metadata):
        super(VectorCoverage, self).__init__()
        self.ident = ident
        self.shape = shape
        self.projection = projection
        self.metadata = metadata

    def reproject(self, new_projection):
        """ Reproject 


def VectorCollection(object)