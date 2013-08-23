#!/usr/bin/env python
""" file:   __init__.py (borehole_analysis)
    author: Jess Robertson
            CSIRO Earth Science and Resource Engineering
    email:  jesse.robertson@csiro.au
    date:   Wednesday May 1, 2013

    description: Initialisation of the borehole_analysis module.
"""

import sklearn
import cwavelets
from borehole_analysis.borehole import Borehole, Feature
import borehole_analysis.importers as importers
import borehole_analysis.wavelets as wavelets
from borehole_analysis.wavelets import WaveletDomain
from borehole_analysis.domains import Domain, \
    SamplingDomain, IntervalDomain, Property, PropertyType
from borehole_analysis.survey import CoordinateReferenceSystem, Survey
import borehole_analysis.plotting as plotting

# Reassign the data classes to the base namespace
OBJECTS = [Borehole, Feature, Domain, \
    SamplingDomain, IntervalDomain, Property, PropertyType, \
    CoordinateReferenceSystem, Survey, WaveletDomain]
for obj in OBJECTS:
    obj.__module__ = 'borehole_analysis'