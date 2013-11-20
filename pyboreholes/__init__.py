#!/usr/bin/env python
""" file:   __init__.py (pyboreholes)
    author: Jess Robertson
            CSIRO Earth Science and Resource Engineering
    email:  jesse.robertson@csiro.au
    date:   Wednesday May 1, 2013

    description: Initialisation of the pyboreholes module.
"""

from .borehole import Borehole, Feature, \
    CoordinateReferenceSystem, Survey
import importers
from pyboreholes.domains import Domain, \
    SamplingDomain, IntervalDomain, WaveletDomain, SpectralDomain
from .properties import Property, PropertyType
import plotting