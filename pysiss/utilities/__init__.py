""" file:   utilities.py (pysiss.borehole)
    author: Jess Robertson
            CSIRO Earth Science and Resource Engineering
    email:  jesse.robertson@csiro.au
    date:   Wednesday May 1, 2013

    description: Utility functions for the cwavelet module.
"""

from maths import heaviside, same_sign, integrate, mask_all_nans, try_float
from collection import Collection
from id_object import id_object
# from projection import project
from singleton import Singleton

__all__ = ['Collection', 'id_object', 'Singleton',
           'heaviside', 'same_sign', 'integrate', 'mask_all_nans', 'try_float']
