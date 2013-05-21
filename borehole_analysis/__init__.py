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
import borehole_analysis.clustering as clustering
from borehole_analysis.analyser import AnalystNode, Analyst
from borehole_analysis.borehole import Borehole
import borehole_analysis.domaining as domaining
import borehole_analysis.plotting as plotting

# Reassign the data classes to the base namespace
OBJECTS = [
    Borehole,
]
for obj in OBJECTS:
    obj.__module__ = 'borehole_analysis'