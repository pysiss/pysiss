""" file:   __init__.py (pysiss.borehole)
    author: Jess Robertson
            CSIRO Earth Science and Resource Engineering
    email:  jesse.robertson@csiro.au
    date:   Wednesday May 1, 2013

    description: Initialisation of the pysiss.borehole module.
"""

from .borehole import Borehole, Feature
from .borehole_collection import BoreholeCollection
from .datasets import DataSet, PointDataSet, IntervalDataSet
from .properties import Property, PropertyType
from pysiss.borehole.siss.borehole_generator import SISSBoreholeGenerator
from . import importers, plotting, analysis

__all__ = [Borehole, Feature, BoreholeCollection,
           DataSet, PointDataSet, IntervalDataSet,
           Property, PropertyType,
           SISSBoreholeGenerator,
           importers, plotting, analysis]
