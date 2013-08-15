#!/usr/bin/env python
""" file: survey.py
    authors: Jess Robertson & Ben Caradoc-Davies
             CSIRO Earth Science and Resource Engineering
    date: Thursday August 15, 2013

    description: Classes and utilities for manipulating borehole surveys.
"""

class CoordinateReferenceSystem(object):

    """System for describing a spatial location as a tuple of real numbers."""

    def  __init__(self):
        raise NotImplementedError


class Survey(object):

    """The spatial shape of the borehole path in three dimensions from the collar.
    Used to convert a sequence of down-hole depths into a sequence of three-dimensional
    points in some coordinate reference system.
    """

    def __init__(self):
        raise NotImplementedError

