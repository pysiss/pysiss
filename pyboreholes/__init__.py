#!/usr/bin/env python
""" file:   __init__.py (pyboreholes)
    author: Jess Robertson
            CSIRO Earth Science and Resource Engineering
    email:  jesse.robertson@csiro.au
    date:   Wednesday May 1, 2013

    description: Initialisation of the pyboreholes module.
"""

import sklearn
import cwavelets
from pyboreholes.borehole import Borehole, Feature, \
    CoordinateReferenceSystem, Survey
import pyboreholes.importers as importers
import pyboreholes.wavelets as wavelets
from pyboreholes.wavelets import WaveletDomain
from pyboreholes.domains import Domain, \
    SamplingDomain, IntervalDomain, Property, PropertyType
import pyboreholes.plotting as plotting