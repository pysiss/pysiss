#!/usr/bin/env python
""" file:   __init__.py (pyboreholes.analysis)
    author: Jess Robertson
            CSIRO Earth Science and Resource Engineering
    email:  jesse.robertson@csiro.au
    date:   Wednesday May 1, 2013

    description: Initialisation of the pyboreholes.modifiers module.
"""

from .regularizer import ReSampler, unique
from .detrend import detrend, demean