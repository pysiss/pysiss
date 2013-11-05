#!/usr/bin/env python
""" file:   __init__.py (python_boreholes)
    author: Jess Robertson
            CSIRO Earth Science and Resource Engineering
    email:  jesse.robertson@csiro.au
    date:   Wednesday May 1, 2013

    description: Initialisation of the python_boreholes module.
"""

import sklearn
import cwavelets
from python_boreholes.borehole import Borehole, Feature, \
    CoordinateReferenceSystem, Survey
import python_boreholes.importers as importers
import python_boreholes.wavelets as wavelets
from python_boreholes.wavelets import WaveletDomain
from python_boreholes.domains import Domain, \
    SamplingDomain, IntervalDomain, Property, PropertyType
import python_boreholes.plotting as plotting