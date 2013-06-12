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
from borehole_analysis.analyser import Analyst
import borehole_analysis.analyser as analyser
from borehole_analysis.borehole import Borehole
import borehole_analysis.importers as importers
import borehole_analysis.domaining as domaining
from borehole_analysis.domaining import WaveletLabeller
import borehole_analysis.plotting as plotting

# Reassign the data classes to the base namespace
OBJECTS = [Borehole, Analyst, WaveletLabeller]
for obj in OBJECTS:
    obj.__module__ = 'borehole_analysis'