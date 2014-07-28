#!/usr/bin/env python
""" file:   __init__.py (pysiss.borehole.analysis)
    author: Jess Robertson
            CSIRO Earth Science and Resource Engineering
    email:  jesse.robertson@csiro.au
    date:   Wednesday May 1, 2013

    description: Initialisation of the pysiss.borehole.modifiers module.
"""

from .regularizer import ReSampler, unique
from .detrend import detrend, demean